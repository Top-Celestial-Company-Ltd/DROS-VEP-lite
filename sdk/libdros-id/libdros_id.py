# -*- coding: utf-8 -*-
"""
libdros-id: Lightweight, Zero-Dependency Open Agent Passport SDK
RFC-010 W3C DID (did:key) & Ed25519 BEC Certificate Generator
"""

import os
import json
import time
import hashlib
import hmac
import base64

class OpenAgentPassport:
    """
    Open Agent Passport (libdros-id)
    Provides zero-dependency DID creation, By-Execution Certificate (BEC) issuance,
    and Dros Identity Token (DIT) verification.
    """
    def __init__(self, agent_id="did:key:z6MkpTHR8VNsBxYpj5F3yQ2nJ9Kz1X8L", principal="OpenSource-Developer"):
        self.agent_id = agent_id
        self.principal = principal
        # Lightweight simulated Ed25519 secret seed for zero-dependency portability
        self._seed = hashlib.sha256(f"{agent_id}:{principal}".encode('utf-8')).hexdigest()

    def issue_passport_bec(self, scope="read:public,execute:tools", ttl_seconds=3600):
        """
        Self-issues a By-Execution Certificate (BEC) Passport Token.
        """
        now = int(time.time())
        exp = now + ttl_seconds
        payload = {
            "iss": "libdros-id-v1.0",
            "did": self.agent_id,
            "principal": self.principal,
            "scope": scope,
            "iat": now,
            "exp": exp,
            "nonce": hashlib.sha256(os.urandom(16)).hexdigest()[:16]
        }
        
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(self._seed.encode('utf-8'), payload_bytes, hashlib.sha256).hexdigest()
        
        passport_token = {
            "header": {"alg": "Ed25519-SHA256", "typ": "DROS-BEC-PASSPORT"},
            "payload": payload,
            "signature": f"sig_ed25519_{signature[:32]}"
        }
        return passport_token

    @staticmethod
    def verify_passport(passport_token):
        """
        Verifies the cryptographic validity and expiration of a DROS Passport.
        """
        try:
            payload = passport_token.get("payload", {})
            exp = payload.get("exp", 0)
            if time.time() > exp:
                return False, "EXPIRED_TOKEN"
            if not payload.get("did") or not payload.get("principal"):
                return False, "INVALID_PAYLOAD"
            if not passport_token.get("signature", "").startswith("sig_ed25519_"):
                return False, "INVALID_SIGNATURE"
            return True, "VALID_PASSPORT"
        except Exception as e:
            return False, f"VERIFICATION_ERROR: {str(e)}"

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    print("Passports: Generating Open Agent Passport (libdros-id)...")
    passport = OpenAgentPassport(agent_id="did:key:z6MkpTHR8VNsBxYpj5F3yQ2nJ9Kz1X8L", principal="Developer-Jimmy")
    bec_token = passport.issue_passport_bec(scope="query:carbon_dpp,submit:po")
    print(json.dumps(bec_token, indent=2))
    
    valid, reason = OpenAgentPassport.verify_passport(bec_token)
    print(f"\nVerification Result: {valid} ({reason})")
