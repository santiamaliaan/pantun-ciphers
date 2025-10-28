"""
Codebook/Homophonic encoder that maps Base64 alphabet to themed words/phrases,
so the output reads like a lyric. The mapping is stored in a JSON profile and is
fully invertible.

JSON format (example):

{
  "name": "default_codebook_id",
  "description": "Lyric-like Indonesian words for Base64 alphabet",
  "alphabet": "base64",  # currently only "base64" supported
  "tokens": {
    "A": "cahaya",
    "B": "bening",
    ...
    "/": "pelangi",
    "=": "padam"
  },
  "rhyme_suffixes": {
    "a": ["a","u","ah","u"],
    "b": ["i","e","ih","i"]
  }
}

Rules:
- We always join tokens with a single space.
- For decryption we split on whitespace and match exact token words.
- Non-codebook punctuation (commas, periods) is ignored during parsing.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
import base64, json, re

BASE64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="

@dataclass
class Codebook:
    name: str
    tokens: Dict[str, str]  # map symbol -> word
    inv: Dict[str, str]     # map word -> symbol
    rhyme_suffixes: Dict[str, List[str]]

    @staticmethod
    def load_json(path: str) -> "Codebook":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("alphabet") != "base64":
            raise ValueError("Only base64 alphabet codebooks are supported")
        tokens = data["tokens"]
        # Basic validation: cover all base64 symbols
        for ch in BASE64_ALPHABET:
            if ch not in tokens:
                raise ValueError(f"Missing mapping for '{ch}' in codebook")
        inv = {v: k for k, v in tokens.items()}
        if len(inv) != len(tokens):
            raise ValueError("Codebook values (words) must be unique")
        rhyme_suffixes = data.get("rhyme_suffixes", {"a":["a","u"], "b":["i","e"]})
        return Codebook(name=data.get("name","codebook"), tokens=tokens, inv=inv, rhyme_suffixes=rhyme_suffixes)

    def encode_bytes(self, b: bytes) -> str:
        s = base64.b64encode(b).decode("ascii")
        words = [self.tokens[ch] for ch in s]
        return " ".join(words)

    def decode_to_bytes(self, text: str) -> bytes:
        # remove punctuation that is not part of words (commas, periods) safely
        cleaned = re.sub(r"[,\.\!\?\:\;\-\—\(\)\[\]\{\}]", "", text)
        words = cleaned.split()
        symbols = []
        for w in words:
            if w not in self.inv:
                raise ValueError(f"Unknown codebook token in text: '{w}'")
            symbols.append(self.inv[w])
        s = "".join(symbols)
        return base64.b64decode(s.encode("ascii"))
