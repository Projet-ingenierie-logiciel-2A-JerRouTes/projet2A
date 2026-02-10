from datetime import UTC, datetime, timedelta

from src.backend.utils.jwt_utils import decode_jwt, encode_jwt


secret = "test"
now = datetime.now(UTC)

token = encode_jwt(
    {"iss": "projet2a", "uid": 1, "exp": int((now + timedelta(minutes=1)).timestamp())},
    secret=secret,
)

print(token)
print(decode_jwt(token, secret=secret, issuer="projet2a"))
