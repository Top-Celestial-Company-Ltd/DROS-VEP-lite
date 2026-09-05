# -*- coding: utf-8 -*-
"""
True Native C-ABI FFI Bridge Wrapper (Calling compiled Rust release dynamic library).
Emulates iOS Swift SPM and Android Kotlin AAR JNI bindings against real compiled binary.
"""

import ctypes
import os
import time

class DROSVerdict(ctypes.Structure):
    _fields_ = [
        ("allowed", ctypes.c_uint8),
        ("error_code", ctypes.c_uint32),
        ("latency_ns", ctypes.c_uint64)
    ]

class NativeDROSCore:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            dll_path = os.path.join(
                os.path.dirname(__file__), "..", "native_core", "target", "release", "dros_mobile_native.dll"
            )
            if not os.path.exists(dll_path):
                # Fallback to local build artifact if in different directory
                dll_path = os.path.join(
                    os.path.dirname(__file__), "..", "native_core", "target", "release", "libdros_mobile_native.dll"
                )
            cls._instance = ctypes.CDLL(os.path.abspath(dll_path))
            cls._instance.dros_mobile_verify_action.argtypes = [
                ctypes.c_uint32,  # role_id
                ctypes.c_uint64,  # action_mask
                ctypes.c_uint8,   # is_background
                ctypes.c_uint8    # biometric_valid
            ]
            cls._instance.dros_mobile_verify_action.restype = DROSVerdict
        return cls._instance

class SwiftDROSClient:
    """True Native iOS Swift SPM FFI Interface"""
    def __init__(self):
        self._native = NativeDROSCore.get_instance()
        self.role_map = {
            "MOBILE_CHAT_ASSISTANT": 1,
            "AUTHENTICATED_USER_SESSION": 2,
            "SECURE_ENCLAVE_PAYMENT_DELEGATE": 3
        }
        self.action_map = {
            "RESTRICTED_READ_CONTACTS": 0x0000000100000000,
            "RESTRICTED_ACCESS_PHOTOS": 0x0000000200000000,
            "RESTRICTED_SEND_SMS": 0x0000000400000000,
            "RESTRICTED_READ_CLIPBOARD": 0x0000000800000000,
            "RESTRICTED_GPS_LOCATION": 0x0000001000000000,
            "RESTRICTED_MICROPHONE_RECORD": 0x0000002000000000,
            "CRITICAL_FINANCIAL_PAYMENT": 0x8000000000000000,
            "READ_FAQ": 0x0000000000000001
        }

    def requestToolCall(self, role: str, action: str, params: dict = None, biometricToken: str = None, isBackground: bool = False):
        role_id = self.role_map.get(role, 0)
        action_mask = self.action_map.get(action, 0)
        is_bg = 1 if isBackground else 0
        bio_valid = 1 if biometricToken == "SECURE_ENCLAVE_BIOMETRIC_AUTH_VALID" else 0

        t0 = time.perf_counter_ns()
        verdict = self._native.dros_mobile_verify_action(role_id, action_mask, is_bg, bio_valid)
        t1 = time.perf_counter_ns()

        err_map = {
            0: "OK",
            1: "DENY_UNKNOWN_ROLE",
            2: "DENY_PRIVILEGE_VIOLATION",
            3: "DENY_BACKGROUND_SURVEILLANCE_FORBIDDEN",
            4: "DENY_BIOMETRIC_REQUIRED"
        }
        return {
            "allowed": bool(verdict.allowed),
            "reason": err_map.get(verdict.error_code, "DENIED"),
            "latency_ns": verdict.latency_ns,
            "ffi_bridge_latency_ns": t1 - t0
        }

class KotlinDROSClient:
    """True Native Android Kotlin AAR JNI FFI Interface"""
    def __init__(self):
        self._swift_equiv = SwiftDROSClient()

    def executeAgentAction(self, role: str, action: str, params: dict = None, biometricToken: str = None, isBackground: bool = False):
        res = self._swift_equiv.requestToolCall(role, action, params, biometricToken, isBackground)
        return {
            "isAllowed": res["allowed"],
            "errorCode": res["reason"],
            "durationNs": res["latency_ns"],
            "jniBridgeNs": res["ffi_bridge_latency_ns"]
        }
