"""Unit tests for auth service."""
import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock

from app.auth.service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)


class TestHashPassword:
    """Tests for hash_password function."""

    def test_returns_hashed_string(self):
        """Should return a hashed string."""
        result = hash_password("testpassword")
        assert isinstance(result, str)
        assert result != "testpassword"

    def test_different_hashes_for_same_password(self):
        """Same password should produce different hashes (due to salt)."""
        hash1 = hash_password("testpassword")
        hash2 = hash_password("testpassword")
        assert hash1 != hash2

    def test_hash_starts_with_expected_format(self):
        """Hash should use bcrypt format."""
        result = hash_password("testpassword")
        assert result.startswith("$2b$")  # bcrypt prefix

    def test_empty_password(self):
        """Should hash empty password."""
        result = hash_password("")
        assert isinstance(result, str)
        assert len(result) > 0


class TestVerifyPassword:
    """Tests for verify_password function."""

    def test_verifies_correct_password(self):
        """Should verify correct password."""
        hashed = hash_password("testpassword")
        assert verify_password("testpassword", hashed) is True

    def test_rejects_incorrect_password(self):
        """Should reject incorrect password."""
        hashed = hash_password("testpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_case_sensitive(self):
        """Password comparison should be case-sensitive."""
        hashed = hash_password("TestPassword")
        assert verify_password("testpassword", hashed) is False
        assert verify_password("TestPassword", hashed) is True

    def test_handles_special_characters(self):
        """Should handle special characters."""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_handles_vietnamese_characters(self):
        """Should handle Vietnamese characters."""
        password = "MậtKhẩu2024"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_invalid_hash_format(self):
        """Should return False for invalid hash format."""
        assert verify_password("password", "invalid-hash") is False


class TestCreateAccessToken:
    """Tests for create_access_token function."""

    @patch("app.auth.service.settings")
    def test_returns_jwt_token(self, mock_settings):
        """Should return a JWT token string."""
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.access_token_expire_minutes = 30

        token = create_access_token({"sub": "test-user"})
        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token  # JWT format

    @patch("app.auth.service.settings")
    def test_includes_custom_expiry(self, mock_settings):
        """Should use custom expiry when provided."""
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.access_token_expire_minutes = 30

        token = create_access_token(
            {"sub": "test-user"},
            expires_delta=timedelta(hours=1)
        )
        assert isinstance(token, str)

    @patch("app.auth.service.settings")
    def test_encodes_data_correctly(self, mock_settings):
        """Should encode data in the token."""
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.access_token_expire_minutes = 30

        test_data = {"sub": "user123", "role": "admin"}
        token = create_access_token(test_data)

        # Decode and verify
        decoded = decode_token(token)
        assert decoded["sub"] == "user123"
        assert decoded["role"] == "admin"

    @patch("app.auth.service.settings")
    def test_includes_expiry_claim(self, mock_settings):
        """Should include exp claim in token."""
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.access_token_expire_minutes = 30

        token = create_access_token({"sub": "test-user"})
        decoded = decode_token(token)
        assert "exp" in decoded


class TestDecodeToken:
    """Tests for decode_token function."""

    @patch("app.auth.service.settings")
    def test_decodes_valid_token(self, mock_settings):
        """Should decode a valid token."""
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.access_token_expire_minutes = 30

        token = create_access_token({"sub": "user123"})
        decoded = decode_token(token)

        assert decoded is not None
        assert decoded["sub"] == "user123"

    @patch("app.auth.service.settings")
    def test_returns_none_for_invalid_token(self, mock_settings):
        """Should return None for invalid token."""
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"

        result = decode_token("invalid.token.here")
        assert result is None

    @patch("app.auth.service.settings")
    def test_returns_none_for_tampered_token(self, mock_settings):
        """Should return None for tampered token."""
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.access_token_expire_minutes = 30

        token = create_access_token({"sub": "user123"})
        # Tamper with the token
        tampered = token[:-5] + "xxxxx"
        result = decode_token(tampered)
        assert result is None

    @patch("app.auth.service.settings")
    def test_returns_none_for_wrong_secret(self, mock_settings):
        """Should return None when decoded with wrong secret."""
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"
        mock_settings.access_token_expire_minutes = 30

        token = create_access_token({"sub": "user123"})

        # Try to decode with different secret
        with patch("app.auth.service.settings") as mock_settings_decode:
            mock_settings_decode.jwt_secret_key = "different-secret"
            mock_settings_decode.jwt_algorithm = "HS256"
            result = decode_token(token)
            assert result is None

    @patch("app.auth.service.settings")
    def test_returns_none_for_empty_token(self, mock_settings):
        """Should return None for empty token."""
        mock_settings.jwt_secret_key = "test-secret-key"
        mock_settings.jwt_algorithm = "HS256"

        result = decode_token("")
        assert result is None