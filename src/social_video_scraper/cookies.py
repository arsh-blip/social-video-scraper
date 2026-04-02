"""
Chrome cookie extraction for macOS.

Extracts and decrypts cookies from Chrome's encrypted cookie store.
Adapted from GridBank batch downloader.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sqlite3
import subprocess
import tempfile
from typing import Optional


def get_chrome_cookies(domain: str, cookie_names: Optional[list[str]] = None) -> dict[str, str]:
    """
    Extract cookies for a domain from Chrome's encrypted cookie store on macOS.

    Args:
        domain: The domain to extract cookies for (e.g., ".x.com", "instagram.com")
        cookie_names: Optional list of specific cookie names to extract. If None, extracts all.

    Returns:
        Dict of {cookie_name: cookie_value}
    """
    chrome_base = os.path.expanduser("~/Library/Application Support/Google/Chrome")

    if not os.path.exists(chrome_base):
        return {}

    # Get Chrome Safe Storage password from Keychain
    key = _get_encryption_key()
    if key is None:
        return {}

    cookies: dict[str, str] = {}

    # Try each Chrome profile
    for profile in ["Default"] + [f"Profile {i}" for i in range(1, 20)]:
        cookie_path = os.path.join(chrome_base, profile, "Cookies")
        if not os.path.exists(cookie_path):
            continue

        profile_cookies = _extract_from_profile(cookie_path, key, domain, cookie_names)
        # Merge — later profiles don't overwrite earlier ones
        for name, value in profile_cookies.items():
            if name not in cookies:
                cookies[name] = value

        # If we found what we need, stop
        if cookie_names and all(n in cookies for n in cookie_names):
            break

    return cookies


def _get_encryption_key() -> Optional[bytes]:
    """Get the AES key derived from Chrome's Safe Storage password."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-w", "-s", "Chrome Safe Storage", "-a", "Chrome"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return None

        password = result.stdout.strip()
        return hashlib.pbkdf2_hmac("sha1", password.encode("utf-8"), b"saltysalt", 1003, dklen=16)
    except Exception:
        return None


def _extract_from_profile(
    cookie_path: str,
    key: bytes,
    domain: str,
    cookie_names: Optional[list[str]] = None,
) -> dict[str, str]:
    """Extract cookies from a single Chrome profile's cookie database."""
    cookies: dict[str, str] = {}
    tmp_db = tempfile.mktemp(suffix=".db")

    try:
        shutil.copy2(cookie_path, tmp_db)
        conn = sqlite3.connect(tmp_db)
        cursor = conn.cursor()

        # Match both ".domain.com" and "domain.com"
        clean_domain = domain.lstrip(".")
        query = "SELECT name, encrypted_value FROM cookies WHERE (host_key LIKE ? OR host_key LIKE ?)"
        params = [f"%{clean_domain}", f"%.{clean_domain}"]

        if cookie_names:
            placeholders = ",".join(["?" for _ in cookie_names])
            query += f" AND name IN ({placeholders})"
            params.extend(cookie_names)

        cursor.execute(query, params)

        for name, encrypted_value in cursor.fetchall():
            value = _decrypt_cookie(encrypted_value, key)
            if value:
                cookies[name] = value

        conn.close()
    except Exception:
        pass
    finally:
        if os.path.exists(tmp_db):
            os.unlink(tmp_db)

    return cookies


def _decrypt_cookie(encrypted_value: bytes, key: bytes) -> Optional[str]:
    """Decrypt a Chrome cookie value using AES-CBC."""
    if not encrypted_value:
        return None

    try:
        # Chrome on macOS prefixes encrypted cookies with b'v10' or b'v11'
        if encrypted_value[:3] in (b"v10", b"v11"):
            encrypted_data = encrypted_value[3:]
        else:
            # Not encrypted, return as-is
            return encrypted_value.decode("utf-8", errors="ignore")

        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend

        iv = b" " * 16
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted_data) + decryptor.finalize()

        # Remove PKCS7 padding
        if decrypted:
            pad_len = decrypted[-1]
            if 0 < pad_len <= 16:
                decrypted = decrypted[:-pad_len]

        # Clean up any null bytes
        decrypted = decrypted.rstrip(b"\x00")

        # After AES-CBC decryption, the first block (16 bytes) may contain
        # garbage bytes from the IV mismatch. The actual cookie value is
        # printable ASCII. Find where the printable content starts.
        # Try full decode first
        try:
            return decrypted.decode("ascii")
        except (UnicodeDecodeError, ValueError):
            pass

        # Strip leading non-printable bytes to find the real value
        for i in range(len(decrypted)):
            if 0x20 <= decrypted[i] <= 0x7E:
                # Check if the rest is all printable ASCII
                candidate = decrypted[i:]
                try:
                    text = candidate.decode("ascii")
                    # Sanity check: cookie values should be reasonably long
                    if len(text) >= 8:
                        return text
                except (UnicodeDecodeError, ValueError):
                    continue

        # Last resort: decode ignoring errors
        return decrypted.decode("utf-8", errors="ignore")
    except Exception:
        return None
