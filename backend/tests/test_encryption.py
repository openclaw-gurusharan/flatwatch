# Tests for encryption service
import pytest

from app.encryption import (
    encrypt_data,
    decrypt_data,
    encrypt_email,
    decrypt_email,
    encrypt_amount,
    decrypt_amount,
    hash_sensitive_data,
)


def test_encrypt_decrypt_basic():
    """Test basic encrypt/decrypt cycle."""
    original = "sensitive_data_123"
    encrypted = encrypt_data(original)
    decrypted = decrypt_data(encrypted)

    assert encrypted != original
    assert decrypted == original


def test_encrypt_empty_string():
    """Test encrypting empty string."""
    assert encrypt_data("") == ""
    assert decrypt_data("") == ""


def test_encrypt_email():
    """Test email encryption."""
    email = "user@example.com"
    encrypted = encrypt_email(email)
    decrypted = decrypt_email(encrypted)

    assert encrypted != email
    assert decrypted == email


def test_encrypt_amount():
    """Test amount encryption."""
    amount = 12500.50
    encrypted = encrypt_amount(amount)
    decrypted = decrypt_amount(encrypted)

    assert encrypted != str(amount)
    assert decrypted == amount


def test_encryption_is_deterministic():
    """Each encryption should produce unique output (due to nonce)."""
    data = "same_data"
    encrypted1 = encrypt_data(data)
    encrypted2 = encrypt_data(data)

    # Different nonces should produce different ciphertext
    assert encrypted1 != encrypted2

    # But both should decrypt correctly
    assert decrypt_data(encrypted1) == data
    assert decrypt_data(encrypted2) == data


def test_hash_sensitive_data():
    """Test hashing for verification."""
    data = "sensitive_data"
    hash1 = hash_sensitive_data(data)
    hash2 = hash_sensitive_data(data)

    # Same data should produce same hash
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 produces 64 hex chars


def test_different_data_different_hash():
    """Test different data produces different hash."""
    hash1 = hash_sensitive_data("data1")
    hash2 = hash_sensitive_data("data2")

    assert hash1 != hash2


def test_decrypt_invalid_base64():
    """Test decrypting invalid base64 returns original."""
    invalid = "not_valid_base64!!!"
    result = decrypt_data(invalid)
    assert result == invalid  # Should return original on failure


def test_decrypt_amount_invalid():
    """Test decrypting invalid amount returns 0.0."""
    result = decrypt_amount("not_a_number")
    assert result == 0.0


def test_encryption_output_format():
    """Test encrypted output is valid base64."""
    data = "test_data"
    encrypted = encrypt_data(data)

    # Should be base64 (alphanumeric + +/ and padding)
    assert all(c.isalnum() or c in "+/=" for c in encrypted)
