"""Tests for envoy.crypto encryption/decryption module."""

import pytest
from cryptography.exceptions import InvalidTag
from envoy.crypto import encrypt, decrypt


PASSWORD = "super-secret-password"
PLAINTEXT = "DB_HOST=localhost\nDB_PASS=hunter2\nAPI_KEY=abc123"


def test_encrypt_returns_string():
    result = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(result, str)
    assert len(result) > 0


def test_encrypt_decrypt_roundtrip():
    encoded = encrypt(PLAINTEXT, PASSWORD)
    decoded = decrypt(encoded, PASSWORD)
    assert decoded == PLAINTEXT


def test_encrypt_produces_different_ciphertexts():
    """Each encryption call should produce a unique ciphertext (random salt/nonce)."""
    enc1 = encrypt(PLAINTEXT, PASSWORD)
    enc2 = encrypt(PLAINTEXT, PASSWORD)
    assert enc1 != enc2


def test_decrypt_wrong_password_raises():
    encoded = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(InvalidTag):
        decrypt(encoded, "wrong-password")


def test_encrypt_empty_string():
    encoded = encrypt("", PASSWORD)
    assert decrypt(encoded, PASSWORD) == ""


def test_encrypt_unicode_content():
    content = "SECRET=café\nNAME=日本語"
    encoded = encrypt(content, PASSWORD)
    assert decrypt(encoded, PASSWORD) == content


def test_decrypt_tampered_data_raises():
    encoded = encrypt(PLAINTEXT, PASSWORD)
    raw = bytearray(__import__('base64').b64decode(encoded))
    raw[-1] ^= 0xFF  # flip last byte
    tampered = __import__('base64').b64encode(bytes(raw)).decode()
    with pytest.raises(InvalidTag):
        decrypt(tampered, PASSWORD)
