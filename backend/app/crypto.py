# crypto.py - field-level encryption for anything personal (profile, questions, answers)
import os
from cryptography.fernet import Fernet
from .config import KEY_FILE


def _load_key() -> bytes:
    key = os.getenv("APP_SECRET_KEY")
    if key:
        return key.encode()
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
    return key


_fernet = Fernet(_load_key())


def encrypt_text(text: str) -> str:
    return _fernet.encrypt(text.encode("utf-8")).decode("utf-8")


def decrypt_text(token: str) -> str:
    return _fernet.decrypt(token.encode("utf-8")).decode("utf-8")
