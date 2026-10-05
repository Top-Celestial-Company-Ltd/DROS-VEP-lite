# -*- coding: utf-8 -*-
"""
DROS Drone Execution Request & Posture Validator.
Implements schema validation and cryptographic/hash checks according to
v0.3 schemas (execution_request, drone_posture, provenance, safety_state).
"""

import json
import os
import hashlib
from typing import Dict, Any, Tuple, Optional
import jsonschema

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMAS_DIR = os.path.join(BASE_DIR, "schemas")

def load_schema(schema_name: str) -> Dict[str, Any]:
    schema_path = os.path.join(SCHEMAS_DIR, schema_name)
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)

EXECUTION_REQUEST_SCHEMA = load_schema("execution_request.schema.json")
DRONE_POSTURE_SCHEMA = load_schema("drone_posture.schema.json")
PROVENANCE_SCHEMA = load_schema("provenance.schema.json")
SAFETY_STATE_SCHEMA = load_schema("safety_state.schema.json")

def compute_arg_hash(arguments: Dict[str, Any]) -> str:
    """Computes deterministic SHA-256 hash of an argument dictionary."""
    normalized = json.dumps(arguments, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

def canonical_request_bytes(req: Dict[str, Any]) -> bytes:
    """
    Returns canonical byte serialization of execution request excluding signature
    for deterministic cryptographic signing and verification.
    """
    signing_copy = {}
    for k, v in req.items():
        if k == "provenance" and isinstance(v, dict):
            # Include provenance data fields EXCEPT signature
            prov_copy = dict(v)
            if "data" in prov_copy and isinstance(prov_copy["data"], dict):
                inner_data = dict(prov_copy["data"])
                inner_data.pop("signature", None)
                prov_copy["data"] = inner_data
            signing_copy[k] = prov_copy
        else:
            signing_copy[k] = v
    normalized = json.dumps(signing_copy, sort_keys=True, separators=(',', ':'))
    return normalized.encode('utf-8')

def sign_execution_request(req: Dict[str, Any], private_key_hex: str) -> str:
    """Signs canonical request bytes with Ed25519 private key, returns hex signature."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    priv = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(private_key_hex))
    sig_bytes = priv.sign(canonical_request_bytes(req))
    return sig_bytes.hex()

def verify_execution_signature(req: Dict[str, Any], signature_hex: str, public_key_hex: str) -> bool:
    """Verifies Ed25519 signature over canonical request bytes against authoritative public key."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.exceptions import InvalidSignature
    try:
        pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
        sig_bytes = bytes.fromhex(signature_hex)
        pub.verify(sig_bytes, canonical_request_bytes(req))
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False

def validate_execution_request(req: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validates raw request against execution_request.schema.json."""
    try:
        jsonschema.validate(instance=req, schema=EXECUTION_REQUEST_SCHEMA)
        return True, None
    except jsonschema.ValidationError as e:
        return False, e.message

def validate_drone_posture(posture: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validates runtime posture against drone_posture.schema.json."""
    try:
        jsonschema.validate(instance=posture, schema=DRONE_POSTURE_SCHEMA)
        return True, None
    except jsonschema.ValidationError as e:
        return False, e.message

def validate_provenance(prov: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validates provenance against provenance.schema.json."""
    try:
        jsonschema.validate(instance=prov, schema=PROVENANCE_SCHEMA)
        return True, None
    except jsonschema.ValidationError as e:
        return False, e.message

def validate_safety_state(state: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validates safety state record against safety_state.schema.json."""
    try:
        jsonschema.validate(instance=state, schema=SAFETY_STATE_SCHEMA)
        return True, None
    except jsonschema.ValidationError as e:
        return False, e.message
