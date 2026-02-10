import bcrypt


users = [
    ("alice", "alice@example.com", "mdpAlice123"),
    ("bob", "bob@example.com", "mdpBob123"),
    ("admin", "admin@example.com", "mdpAdmin123"),
]

print("INSERT INTO users (username, email, password_hash)")
print("VALUES")

values = []
for username, email, password in users:
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt(rounds=12)
    ).decode("utf-8")

    values.append(f"('{username}', '{email}', '{password_hash}')")

print(",\n".join(values) + ";")
