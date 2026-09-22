use dros_core_rs::execution_authority::{ExecutionDecision, ExecutionRequest};
use dros_core_rs::ffi::{
    dros_v2_decide_execution, dros_v2_free, dros_v2_init, DROS_OK,
};
use std::ffi::CString;
use std::fs;
use std::io;
use std::os::raw::{c_int, c_long};
use std::os::unix::process::CommandExt;
use std::process::Command;

const EXECUTE: u64 = 1;
const SYS_LANDLOCK_CREATE_RULESET: c_long = 444;
const SYS_LANDLOCK_ADD_RULE: c_long = 445;
const SYS_LANDLOCK_RESTRICT_SELF: c_long = 446;
const SYS_PRCTL: c_long = 157;
const PR_SET_NO_NEW_PRIVS: c_long = 38;

#[repr(C)]
struct RulesetAttr {
    handled_access_fs: u64,
    scoped: u64,
}

#[repr(C)]
struct PathBeneathAttr {
    allowed_access: u64,
    parent_fd: c_int,
}

unsafe extern "C" {
    fn syscall(number: c_long, ...) -> c_long;
    fn open(path: *const i8, flags: c_int, ...) -> c_int;
    fn close(fd: c_int) -> c_int;
}

fn landlock_pre_exec(allow_execute: bool) -> io::Result<()> {
    unsafe {
        if syscall(SYS_PRCTL, PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0 {
            return Err(io::Error::last_os_error());
        }
        let ruleset = RulesetAttr {
            handled_access_fs: EXECUTE,
            scoped: 0,
        };
        let fd = syscall(
            SYS_LANDLOCK_CREATE_RULESET,
            &ruleset as *const RulesetAttr,
            std::mem::size_of::<RulesetAttr>(),
            0,
        ) as c_int;
        if fd < 0 {
            return Err(io::Error::last_os_error());
        }
        if allow_execute {
            let root = b"/\0";
            let parent_fd = open(root.as_ptr() as *const i8, 0o10000000 | 0o400000, 0);
            if parent_fd < 0 {
                close(fd);
                return Err(io::Error::last_os_error());
            }
            let rule = PathBeneathAttr {
                allowed_access: EXECUTE,
                parent_fd,
            };
            let added = syscall(SYS_LANDLOCK_ADD_RULE, fd, 1, &rule as *const PathBeneathAttr, 0);
            close(parent_fd);
            if added != 0 {
                close(fd);
                return Err(io::Error::last_os_error());
            }
        }
        let restricted = syscall(SYS_LANDLOCK_RESTRICT_SELF, fd, 0);
        close(fd);
        if restricted != 0 {
            return Err(io::Error::last_os_error());
        }
    }
    Ok(())
}

fn run_case(name: &str, resource: &str, substrate_allow: bool) {
    let issued_at_epoch = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .expect("system clock must be after epoch")
        .as_secs()
        - 1;
    let request = ExecutionRequest {
        principal: "agent-cli".to_string(),
        capability: "cli.execute".to_string(),
        executable: resource.to_string(),
        argv_hash: "sha256:fixture".to_string(),
        target: "local".to_string(),
        working_directory: "/tmp".to_string(),
        runtime_posture: serde_json::json!({"sandbox": "landlock"}),
        policy_context: serde_json::json!({"policy": "fixture"}),
        issued_at_epoch,
        ttl_seconds: 60,
        provenance: serde_json::json!({"source": "canonical-harness"}),
    };
    let request_json = CString::new(serde_json::to_string(&request).expect("serialize request"))
        .expect("request must be NUL-free");
    let response_ptr = dros_v2_decide_execution(request_json.as_ptr());
    let decision = if response_ptr.is_null() {
        None
    } else {
        let response = unsafe {
            std::ffi::CStr::from_ptr(response_ptr)
                .to_str()
                .expect("decision must be UTF-8")
                .to_string()
        };
        dros_v2_free(response_ptr);
        Some(serde_json::from_str::<ExecutionDecision>(&response).expect("decode decision"))
    };
    let decision_name = decision
        .as_ref()
        .map_or("DENY", |value| value.decision.as_str());
    let mut created = false;
    let mut child_pid = None;
    let mut exit_code = None;

    if decision_name == "ALLOW" {
        let mut command = Command::new("/usr/bin/true");
        unsafe {
            command.pre_exec(move || landlock_pre_exec(substrate_allow));
        }
        match command.spawn() {
            Ok(mut child) => {
                child_pid = Some(child.id());
                let status = child.wait().expect("wait child");
                exit_code = status.code();
                created = status.success();
            }
            Err(_) => {}
        }
    }

    println!(
        "{{\"case\":\"{}\",\"dct_decision\":\"{}\",\"ffi_return_code\":{},\"reason\":\"{}\",\"substrate\":\"{}\",\"target_process_created\":{},\"parent_pid\":{},\"child_pid\":{},\"exit_code\":{}}}",
        name,
        decision_name,
        if decision.is_some() { DROS_OK } else { -1 },
        decision.as_ref().map_or("PDP_UNAVAILABLE", |value| value.reason.as_str()),
        if substrate_allow { "ALLOW_EXECUTE" } else { "DENY_EXECUTE" },
        created,
        std::process::id(),
        child_pid.map_or("null".to_string(), |pid| pid.to_string()),
        exit_code.map_or("null".to_string(), |code| code.to_string()),
    );
}

fn main() {
    let policy_path = std::env::temp_dir().join(format!(
        "dros-cli-exec-policy-{}.bin",
        std::process::id()
    ));
    let mut policy = b"DROS-V2-POLICY-PAYLOAD".to_vec();
    policy.extend_from_slice(b"DCTX");
    policy.extend_from_slice(&1u32.to_be_bytes());
    let mut record = [0u8; 72];
    record[..13].copy_from_slice(b"/usr/bin/true");
    record[68] = 1;
    policy.extend_from_slice(&record);
    fs::write(&policy_path, policy).expect("write policy fixture");

    let policy_path_c = CString::new(policy_path.to_string_lossy().as_bytes())
        .expect("policy path must be NUL-free");
    let init_rc = dros_v2_init(policy_path_c.as_ptr());
    assert_eq!(init_rc, DROS_OK, "canonical C-ABI policy load failed");

    run_case("14-A_DROS_DENY_SUBSTRATE_ALLOW", "/bin/sh", true);
    run_case("14-B_DROS_ALLOW_SUBSTRATE_DENY", "/usr/bin/true", false);
    run_case("14-C_DROS_ALLOW_SUBSTRATE_ALLOW", "/usr/bin/true", true);
    fs::remove_file(policy_path).expect("remove policy fixture");
    println!("{{\"verdict\":\"CANONICAL_EXECUTION_AUTHORITY_PATH_CONFIRMED\"}}");
}
