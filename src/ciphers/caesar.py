"""
Caesar cipher (shift over letters A-Z, a-z). Non-letters are passed through.
Deterministic, reversible. Case preserved.
"""
from typing import Tuple

def _shift_char(ch: str, k: int) -> str:
    if 'A' <= ch <= 'Z':
        base = ord('A')
        return chr((ord(ch) - base + k) % 26 + base)
    if 'a' <= ch <= 'z':
        base = ord('a')
        return chr((ord(ch) - base + k) % 26 + base)
    return ch

def encrypt(plaintext: str, key: str) -> str:
    # interpret key as integer shift from any string by summing code points
    k = sum(ord(c) for c in key) % 26 if key else 0
    return ''.join(_shift_char(ch, k) for ch in plaintext)

def decrypt(ciphertext: str, key: str) -> str:
    k = sum(ord(c) for c in key) % 26 if key else 0
    return ''.join(_shift_char(ch, -k) for ch in ciphertext)
