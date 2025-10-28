"""
Vigenère cipher over letters A-Z, a-z. Non-letters are passed through unchanged.
Key is any string; only alphabetic characters contribute to shifts (A/a=0...Z/z=25).
Case preserved. Deterministic & reversible.
"""
from typing import List

def _shift(ch: str, k: int) -> str:
    if 'A' <= ch <= 'Z':
        base = ord('A')
        return chr((ord(ch) - base + k) % 26 + base)
    if 'a' <= ch <= 'z':
        base = ord('a')
        return chr((ord(ch) - base + k) % 26 + base)
    return ch

def _key_stream(s: str) -> List[int]:
    ks = []
    for ch in s:
        if ch.isalpha():
            ks.append((ord(ch.upper()) - ord('A')) % 26)
    if not ks:
        ks = [0]
    return ks

def encrypt(plaintext: str, key: str) -> str:
    ks = _key_stream(key or "")
    res = []
    j = 0
    for ch in plaintext:
        if ch.isalpha():
            res.append(_shift(ch, ks[j % len(ks)]))
            j += 1
        else:
            res.append(ch)
    return ''.join(res)

def decrypt(ciphertext: str, key: str) -> str:
    ks = _key_stream(key or "")
    res = []
    j = 0
    for ch in ciphertext:
        if ch.isalpha():
            res.append(_shift(ch, -ks[j % len(ks)]))
            j += 1
        else:
            res.append(ch)
    return ''.join(res)
