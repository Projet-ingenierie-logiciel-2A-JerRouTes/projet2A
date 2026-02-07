from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any


class JWTError(Exception):
    """Erreur générique JWT."""


class JWTInvalidTokenError(JWTError):
    """Token invalide (format, signature, etc.)."""


class JWTExpiredError(JWTError):
    """Token expiré."""


class JWTIssuerError(JWTError):
    """Issuer (iss) invalide."""


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    # padding base64
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("utf-8"))


def encode_jwt(
    payload: dict[str, Any],
    *,
    secret: str,
    headers: dict[str, Any] | None = None,
) -> str:
    """
    Crée un JWT HS256.
    - payload: dict contenant potentiellement exp/iat/iss/etc.
    - secret: clé HMAC
    - headers: headers custom (optionnel)
    """
    hdr = {"typ": "JWT", "alg": "HS256"}
    if headers:
        hdr.update(headers)

    header_json = json.dumps(hdr, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )

    header_b64 = _b64url_encode(header_json)
    payload_b64 = _b64url_encode(payload_json)

    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_jwt(
    token: str,
    *,
    secret: str,
    verify_exp: bool = True,
    issuer: str | None = None,
) -> dict[str, Any]:
    """
    Décode et vérifie un JWT HS256.
    - verify_exp: si True, vérifie exp
    - issuer: si non None, vérifie payload["iss"] == issuer
    Retourne le payload dict.
    """
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError as exc:
        raise JWTInvalidTokenError("Format JWT invalide.") from exc

    # 1) Parse header/payload
    try:
        header = json.loads(_b64url_decode(header_b64).decode("utf-8"))
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    except Exception as exc:
        raise JWTInvalidTokenError("Header/Payload JWT illisible.") from exc

    # 2) Vérifier alg
    if header.get("alg") != "HS256":
        raise JWTInvalidTokenError("Algorithme JWT non supporté (attendu HS256).")

    # 3) Vérifier signature
    signing_input = f"{header_b64}.{payload_b64}".encode()
    expected_sig = hmac.new(
        secret.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    expected_sig_b64 = _b64url_encode(expected_sig)

    if not hmac.compare_digest(expected_sig_b64, signature_b64):
        raise JWTInvalidTokenError("Signature JWT invalide.")

    # 4) Vérifier issuer
    if issuer is not None and payload.get("iss") != issuer:
        raise JWTIssuerError("Issuer (iss) invalide.")

    # 5) Vérifier exp
    if verify_exp:
        exp = payload.get("exp")
        if exp is None:
            # on peut choisir de l'exiger, ou non. Ici : si absent, ok.
            return payload

        try:
            exp_int = int(exp)
        except (TypeError, ValueError) as exc:
            raise JWTInvalidTokenError("Champ exp invalide.") from exc

        now = int(time.time())
        if exp_int <= now:
            raise JWTExpiredError("JWT expiré.")

    return payload
