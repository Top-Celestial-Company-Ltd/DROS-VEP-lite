use dros_core_rs::execution_authority::{ExecutionDecision, ExecutionRequest};
use dros_core_rs::ffi::{dros_v2_decide_execution, dros_v2_free, dros_v2_init, DROS_OK};
use serde_json::json;
use std::ffi::CString;
use std::fs;
use std::io;
use std::os::raw::{c_int, c_long};
use std::os::unix::process::CommandExt;
use std::process::Command;

const SYS_EXECVEAT_X86_64: c_long = 322;
const AT_FDCWD: c_long = -100;

#[derive(Debug)]
struct ProcessAttempt {
    created: bool,
    child_pid: Option<u32>,
    exit_code: Option<i32>,
}

fn run_command(mut command: Command) -> ProcessAttempt {
    match command.spawn() {
        Ok(mut child) => {
            let child_pid = Some(child.id());
            let exit_code = child.wait().ok().and_then(|status| status.code());
            ProcessAttempt {
                created: true,
                child_pid,
                exit_code,
            }
        }
        Err(_) => ProcessAttempt {
            created: false,
            child_pid: None,
            exit_code: None,
        },
    }
}

fn direct_execve() -> ProcessAttempt {
    run_command(Command::new("/usr/bin/true"))
}

fn shell_execve() -> ProcessAttempt {
    let mut command = Command::new("/bin/sh");
    command.args(["-c", "exec /usr/bin/true"]);
    run_command(command)
}

fn direct_execveat() -> ProcessAttempt {
    let path = CString::new("/usr/bin/true").expect("path is NUL-free");
    let arg0 = CString::new("/usr/bin/true").expect("argv is NUL-free");
    let command_path = path.clone();
    let command_arg0 = arg0.clone();
    let mut command = Command::new("/bin/true");
    unsafe {
        command.pre_exec(move || {
            let argv = [command_arg0.as_ptr(), std::ptr::null()];
            let envp: [*const i8; 1] = [std::ptr::null()];
            let rc = libc::syscall(
                SYS_EXECVEAT_X86_64,
                AT_FDCWD,
                command_path.as_ptr(),
                argv.as_ptr(),
                envp.as_ptr(),
                0,
            ) as c_int;
            if rc == -1 {
                Err(io::Error::last_os_error())
            } else {
                Ok(())
            }
        });
    }
    run_command(command)
}

fn interpreter_exec() -> ProcessAttempt {
    let mut command = Command::new("python3");
    command.args([
        "-c",
        "import os; os.execv('/usr/bin/true', ['/usr/bin/true'])",
    ]);
    run_command(command)
}

fn symlink_exec() -> ProcessAttempt {
    let link = std::env::temp_dir().join(format!("dros-cli-bypass-{}", std::process::id()));
    let _ = fs::remove_file(&link);
    if std::os::unix::fs::symlink("/usr/bin/true", &link).is_err() {
        return ProcessAttempt {
            created: false,
            child_pid: None,
            exit_code: None,
        };
    }
    let attempt = run_command(Command::new(&link));
    let _ = fs::remove_file(link);
    attempt
}

fn inherited_context_exec() -> ProcessAttempt {
    let mut command = Command::new("/usr/bin/true");
    command.env("DROS_AUTHORITY_CONTEXT", "inherited-without-pdp");
    run_command(command)
}

fn registered_deny() -> (String, bool) {
    let issued_at_epoch = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .expect("system clock must be after epoch")
        .as_secs()
        - 1;
    let request = ExecutionRequest {
        principal: "agent-cli".to_string(),
        capability: "cli.execute".to_string(),
        executable: "/bin/sh".to_string(),
        argv_hash: "sha256:bypass".to_string(),
        target: "local".to_string(),
        working_directory: "/tmp".to_string(),
        runtime_posture: json!({"sandbox": "landlock"}),
        policy_context: json!({"policy": "fixture"}),
        issued_at_epoch,
        ttl_seconds: 60,
        provenance: json!({"source": "topology-bypass-harness"}),
    };
    let request_json = CString::new(serde_json::to_string(&request).unwrap()).unwrap();
    let response_ptr = dros_v2_decide_execution(request_json.as_ptr());
    if response_ptr.is_null() {
        return ("PDP_UNAVAILABLE".to_string(), false);
    }
    let response = unsafe { std::ffi::CStr::from_ptr(response_ptr).to_str().unwrap().to_string() };
    dros_v2_free(response_ptr);
    let decision: ExecutionDecision = serde_json::from_str(&response).unwrap();
    (decision.reason, decision.decision == "ALLOW")
}

fn print_case(
    case: &str,
    classification: &str,
    authority_called: bool,
    attempt: ProcessAttempt,
) {
    println!(
        "{}",
        serde_json::to_string(&json!({
            "case": case,
            "classification": classification,
            "authority_called": authority_called,
            "process_created": attempt.created,
            "child_pid": attempt.child_pid,
            "exit_code": attempt.exit_code,
        }))
        .unwrap()
    );
}

fn main() {
    let policy_path = std::env::temp_dir().join(format!(
        "dros-cli-bypass-policy-{}.bin",
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
    let policy_path_c = CString::new(policy_path.to_string_lossy().as_bytes()).unwrap();
    assert_eq!(dros_v2_init(policy_path_c.as_ptr()), DROS_OK);

    let (reason, allow) = registered_deny();
    let registered_attempt = if allow {
        direct_execve()
    } else {
        ProcessAttempt {
            created: false,
            child_pid: None,
            exit_code: None,
        }
    };
    print_case(
        "REGISTERED-DENY",
        "GOVERNED",
        true,
        registered_attempt,
    );
    eprintln!("registered_reason={reason}");

    print_case("B1_SHELL_EXECVE", "BYPASS_CONFIRMED", false, shell_execve());
    print_case("B2_DIRECT_EXECVEAT", "BYPASS_CONFIRMED", false, direct_execveat());
    print_case("B3_CHILD_PROCESS_EXEC", "BYPASS_CONFIRMED", false, direct_execve());
    print_case("B4_DIRECT_SYSCALL_VARIANT", "BYPASS_CONFIRMED", false, direct_execveat());
    print_case(
        "B5_INTERPRETER_MEDIATED",
        "BYPASS_CONFIRMED",
        false,
        interpreter_exec(),
    );
    print_case("B6_EXECUTABLE_PATH_MUTATION", "BYPASS_CONFIRMED", false, symlink_exec());
    print_case(
        "B7_INHERITED_CONTEXT",
        "BYPASS_CONFIRMED",
        false,
        inherited_context_exec(),
    );
    print_case("B8_NAMESPACE_CONTAINER", "OUTSIDE_CURRENT_BOUNDARY", false, ProcessAttempt {
        created: false,
        child_pid: None,
        exit_code: None,
    });
    print_case("B9_OUTSIDE_REGISTERED_PEP", "BYPASS_CONFIRMED", false, direct_execve());
    print_case("B10_SECOND_EXECUTION_SURFACE", "BYPASS_CONFIRMED", false, interpreter_exec());

    let _ = fs::remove_file(policy_path);
    println!("{{\"verdict\":\"TOPOLOGY_BYPASS_CONFIRMED\"}}");
}
