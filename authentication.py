from hashlib import sha256
from pathlib import Path
from secrets import token_bytes

STATIC_PATH = Path(__file__).absolute().parent / "static"
PASSWD_PATH = STATIC_PATH / "etc" / "passwd"

# randomly generate a new admin password for this run:
with open(PASSWD_PATH, "w") as f:
    f.write(f"root:{sha256(token_bytes(32)).hexdigest()}\n")


def is_admin(username: str, password: str) -> bool:
    try:
        password_hash = sha256(password).hexdigest()
        with open(PASSWD_PATH, "r") as f:
            for line in f:
                admin_username, admin_password_hash = line.split(":")
                if admin_username == username and admin_password_hash == password_hash:
                    return True
    except:
        return False
