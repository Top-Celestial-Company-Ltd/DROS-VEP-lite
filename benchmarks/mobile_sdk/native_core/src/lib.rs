// Pure C-ABI FFI Core for Mobile Agent Runtime Governance (iOS / Android)
// No heap allocation on the hot path, O(1) constant-time bitmask evaluation.

#[repr(C)]
pub struct DROSVerdict {
    pub allowed: u8,       // 1 = ALLOW, 0 = DENY
    pub error_code: u32,   // 0 = OK, 1 = ROLE_ERR, 2 = PRIV_VIOLATION, 3 = SURVEILLANCE_ERR, 4 = BIOMETRIC_ERR
    pub latency_ns: u64,
}

// Bitmask Definitions
pub const RESTRICTED_READ_CONTACTS: u64       = 0x0000000100000000;
pub const RESTRICTED_ACCESS_PHOTOS: u64       = 0x0000000200000000;
pub const RESTRICTED_SEND_SMS: u64            = 0x0000000400000000;
pub const RESTRICTED_READ_CLIPBOARD: u64      = 0x0000000800000000;
pub const RESTRICTED_GPS_LOCATION: u64        = 0x0000001000000000;
pub const RESTRICTED_MICROPHONE_RECORD: u64   = 0x0000002000000000;
pub const CRITICAL_FINANCIAL_PAYMENT: u64     = 0x8000000000000000;

// Role Masks
pub const ROLE_CHAT_ASSISTANT_MASK: u64       = 0x0000000000000007; // READ_FAQ | THEME | CACHE
pub const ROLE_AUTHENTICATED_USER_MASK: u64   = 0x0000001300000007; // Above + CONTACTS + PHOTOS + GPS
pub const ROLE_SECURE_ENCLAVE_MASK: u64       = 0x8000000000000000; // FINANCIAL_PAYMENT

/// C-ABI exported entrypoint for iOS Swift SPM and Android JNI Bridge
#[no_mangle]
pub extern "C" fn dros_mobile_verify_action(
    role_id: u32,             // 1 = CHAT_ASSISTANT, 2 = AUTH_USER, 3 = SECURE_ENCLAVE
    action_mask: u64,         // 64-bit capability bit
    is_background: u8,        // 1 = background, 0 = foreground
    biometric_valid: u8       // 1 = verified by Secure Enclave, 0 = none
) -> DROSVerdict {
    let t0 = std::time::Instant::now();

    // 1. Role Bitmask Lookup
    let role_mask = match role_id {
        1 => ROLE_CHAT_ASSISTANT_MASK,
        2 => ROLE_AUTHENTICATED_USER_MASK,
        3 => ROLE_SECURE_ENCLAVE_MASK,
        _ => {
            return DROSVerdict {
                allowed: 0,
                error_code: 1, // ROLE_ERR
                latency_ns: t0.elapsed().as_nanos() as u64,
            };
        }
    };

    // 2. Constant-Time Capability Bitmask Evaluation
    if (role_mask & action_mask) != action_mask {
        return DROSVerdict {
            allowed: 0,
            error_code: 2, // PRIV_VIOLATION
            latency_ns: t0.elapsed().as_nanos() as u64,
        };
    }

    // 3. Background Surveillance Constraint (MobileSafetyBench)
    if is_background == 1 && (action_mask == RESTRICTED_MICROPHONE_RECORD || action_mask == RESTRICTED_GPS_LOCATION) {
        return DROSVerdict {
            allowed: 0,
            error_code: 3, // SURVEILLANCE_ERR
            latency_ns: t0.elapsed().as_nanos() as u64,
        };
    }

    // 4. Financial Payment Biometric Gating (AgentDojo)
    if action_mask == CRITICAL_FINANCIAL_PAYMENT && biometric_valid != 1 {
        return DROSVerdict {
            allowed: 0,
            error_code: 4, // BIOMETRIC_ERR
            latency_ns: t0.elapsed().as_nanos() as u64,
        };
    }

    let latency = t0.elapsed().as_nanos() as u64;
    DROSVerdict {
        allowed: 1,
        error_code: 0,
        latency_ns: latency,
    }
}
