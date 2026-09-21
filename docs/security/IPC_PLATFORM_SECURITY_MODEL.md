# DROS Loopback IPC Platform Security Model (IPC_PLATFORM_SECURITY_MODEL.md)
* **Document Version**: v1.0.0
* **Date**: 2026-09-16
* **Status**: NORMATIVE PLATFORM MAPPING
* **Prerequisite**: Aligned with `BASELINE-VEP-2026-M5.1`, `LOOPBACK_IPC_THREAT_MODEL.md`

---

## 1. Cross-Platform Peer Identity Attribution Matrix

The table below contrasts the actual security guarantees of OS-level peer attribution across Linux and Windows:

| Security Property | Linux Unix Domain Socket (UDS) | Windows Named Pipe |
| :--- | :--- | :--- |
| **Primary API** | `getsockopt(fd, SOL_SOCKET, SO_PEERCRED, ...)` or `getpeereid()` | `GetNamedPipeClientProcessId(pipe_handle, &pid)` |
| **Kernel Verification** | Native kernel socket buffer metadata | Kernel I/O subsystem / Named Pipe File System (`npfs.sys`) |
| **Caller PID Attribution** | **SUPPORTED** (Kernel returns authentic `pid`) | **SUPPORTED** (Kernel returns authentic client `PID`) |
| **Caller UID / User SID** | **SUPPORTED** (Returns numerical `uid` and `gid`) | **SUPPORTED** (Via `ImpersonateNamedPipeClient` + `GetTokenInformation`) |
| **Filesystem ACLs** | POSIX permissions (`chmod 0600 /tmp/dros.sock`) | Windows Security Descriptor / DACLs (`CreateNamedPipeW` with SDDL) |
| **Container / Namespace** | PID/UID namespaces require mapping if crossing cgroup boundary | AppContainer SID isolation |
| **Intra-UID Tamper Risk**| Unconfined `ptrace` allows memory reading unless Yama LSM active | `PROCESS_VM_READ` allowed unless process token restricted / protected |

---

## 2. Linux Implementation Specification

1. **Endpoint Binding**:
   - Path: `/run/dros/dros-pep.sock` or `$XDG_RUNTIME_DIR/dros-pep.sock`.
   - File Mode: `0600` (Read/Write solely for the owner user).
2. **Attribution Mechanism**:
   - PEP executes `getsockopt(client_fd, SOL_SOCKET, SO_PEERCRED, ...)` upon `accept()`.
   - Resolves `(pid, uid, gid)`.
3. **Defense-in-Depth**:
   - Even if `uid == 1000` matches the Agent user, the PEP strictly validates that `pid` matches the specific registered session PID. A sibling process spawned under `uid=1000` has a distinct PID ($PID_B \neq PID_A$) and is rejected at the gate.

---

## 3. Windows Implementation Specification

1. **Endpoint Binding**:
   - Pipe Name: `\\.\pipe\dros_pep_<uuid>`.
   - Security Attributes: Explicit SDDL restricting connection access exclusively to the current user SID (`D:(A;;GA;;;PS)`).
2. **Attribution Mechanism**:
   - PEP queries `GetNamedPipeClientProcessId` upon connection arrival.
   - Extracts calling client PID directly from the Windows kernel.
3. **Execution Policy**:
   - In environments where Windows Named Pipes cannot be spawned (e.g. cross-platform CLI tests), the VEP test harness executes via `MockPeerIdentityProvider`, preserving identical behavioral semantics and verifying attribution invariants deterministically.
