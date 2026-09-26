"""Pure-Python port of the Rahkaran login page's RSA.js `encryptedString`
(Tang Yu Feng's PKCS#1 v1.5 variant of Dave Shapiro's RSA.js).

The login page encrypts ``sessionid + "--" + password`` with the page's
public key (hex ``rsa_e`` / ``rsa_m``). The JS pads each chunk as
``0x00 || 0x02 || random non-zero bytes || 0x00 || message`` (big-endian
over the key's byte length), exponentiates, and prints the result as
big-endian hex in 4-character digit groups; chunks are joined by spaces.
No Node.js needed.
"""
import os

def _utf8(s: str) -> bytes:
    return s.encode("utf-8", "surrogatepass")


def _hex_digits(value: int) -> str:
    """biToHex: 16-bit digits from the highest non-zero digit down, 4 hex chars each."""
    text = format(value, "x")
    return text.rjust((len(text) + 3) // 4 * 4, "0")


def encrypt_string(text: str, rsa_e_hex: str, rsa_m_hex: str, rand: "callable" = None) -> str:
    e = int(rsa_e_hex, 16)
    m = int(rsa_m_hex, 16)
    # RSA.js: digitSize = 2 * biHighIndex(m) + 2  (bytes, rounded up to a 16-bit digit)
    digit_size = ((m.bit_length() + 15) // 16) * 2
    chunk_size = digit_size - 11
    if chunk_size <= 0:
        return "Error"
    rand = rand or (lambda: os.urandom(1)[0] % 254 + 1)
    data = _utf8(text)
    blocks = []
    for start in range(0, len(data), chunk_size):
        message = data[start:start + chunk_size]
        pad_len = max(8, digit_size - 3 - len(message))
        padding = bytes(rand() for _ in range(pad_len))
        em = b"\x00\x02" + padding + b"\x00" + message
        blocks.append(_hex_digits(pow(int.from_bytes(em, "big"), e, m)))
    return " ".join(blocks)


def encrypt_password(password: str, rsa_e_hex: str, rsa_m_hex: str, session_id: str) -> str:
    return encrypt_string(f"{session_id}--{password}", rsa_e_hex, rsa_m_hex)
