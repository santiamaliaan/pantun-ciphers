#!/usr/bin/env python3
import argparse, json, sys, os, re
from typing import List
from .ciphers import caesar, vigenere
from .codebook import Codebook
from .pantun import layout_abab

def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def cmd_encrypt(args):
    text = args.input.read() if hasattr(args.input, "read") else args.input
    algo = args.algo.lower()
    key = args.key or ""

    # Step 1: classical cipher (optional)
    if algo == "vigenere":
        step = vigenere.encrypt(text, key)
    elif algo == "caesar":
        step = caesar.encrypt(text, key)
    else:
        print(f"Unsupported algo: {algo}", file=sys.stderr)
        sys.exit(2)

    # Step 2: codebook lyric mapping (bytes -> words), guaranteeing full coverage
    cb = Codebook.load_json(args.theme)
    code_words = cb.encode_bytes(step.encode("utf-8")).split()

    if args.pantun:
        lines = layout_abab(code_words, cb.rhyme_suffixes.get("a",["a","u"]), cb.rhyme_suffixes.get("b",["i","e"]))
        out = ",\n".join(lines[:3]) + ".\n" + lines[3] + "."  # add light punctuation
    else:
        out = " ".join(code_words)

    sys.stdout.write(out)

def cmd_decrypt(args):
    text = args.input.read() if hasattr(args.input, "read") else args.input
    cb = Codebook.load_json(args.theme)
    # Remove punctuation introduced in pantun mode
    cleaned = re.sub(r"[,\.]+", "", text)
    # Gather words and decode via codebook
    raw = cb.decode_to_bytes(cleaned).decode("utf-8")

    algo = args.algo.lower()
    key = args.key or ""
    if algo == "vigenere":
        plain = vigenere.decrypt(raw, key)
    elif algo == "caesar":
        plain = caesar.decrypt(raw, key)
    else:
        print(f"Unsupported algo: {algo}", file=sys.stderr)
        sys.exit(2)

    # Optional normalization
    if args.normalize:
        plain = normalize_spaces(plain)

    sys.stdout.write(plain)

def cmd_test(args):
    # quick deterministic round-trip sanity check
    samples = [
        "PADAMU NEGERI JIWA RAGA KAMI",
        "Halo, dunia! Ini contoh multiline\nDengan emoji 😊 dan akronim APT/SOC.",
        "1234567890 -- tetap utuh, non-alfabet.",
        "Spasi    berlebih\takan   dipertahankan.",
        "Pantun mode cek rhyme ABAB agar enak dibaca."
    ]
    key = args.key or "GARUDA"
    cbpath = args.theme
    for algo in ["vigenere", "caesar"]:
        for pantun_flag in [False, True]:
            for s in samples:
                # encrypt
                ns = argparse.Namespace(algo=algo, key=key, theme=cbpath, pantun=pantun_flag, input=s)
                enc = capture(lambda: cmd_encrypt(ns))
                # decrypt
                nd = argparse.Namespace(algo=algo, key=key, theme=cbpath, normalize=False, input=enc)
                dec = capture(lambda: cmd_decrypt(nd))
                assert s == dec, f"Roundtrip failed for algo={algo}, pantun={pantun_flag}\norig={s}\nback={dec}"
    print("Self-test OK")

def capture(fn):
    from io import StringIO
    old_out = sys.stdout
    buf = StringIO()
    sys.stdout = buf
    try:
        fn()
    finally:
        sys.stdout = old_out
    return buf.getvalue()

def main():
    p = argparse.ArgumentParser(description="Lirik/Pantun Cipher CLI")
    sub = p.add_subparsers(dest="command", required=True)

    pe = sub.add_parser("encrypt", help="Encrypt -> lyric/pantun")
    pe.add_argument("--algo", choices=["vigenere","caesar"], default="vigenere")
    pe.add_argument("--key", type=str, required=True, help="Key string for the classical cipher")
    pe.add_argument("--theme", type=str, required=True, help="Path to codebook JSON")
    pe.add_argument("--pantun", action="store_true", help="Format output as 4-line pantun (ABAB)")
    pe.add_argument("input", nargs="?", type=str, default="", help="Plaintext input (or pipe via STDIN)")
    pe.set_defaults(func=cmd_encrypt)

    pd = sub.add_parser("decrypt", help="Decrypt from lyric/pantun back to plaintext")
    pd.add_argument("--algo", choices=["vigenere","caesar"], default="vigenere")
    pd.add_argument("--key", type=str, required=True, help="Key string used for encryption")
    pd.add_argument("--theme", type=str, required=True, help="Path to codebook JSON")
    pd.add_argument("--normalize", action="store_true", help="Normalize spaces in output")
    pd.add_argument("input", nargs="?", type=str, default="", help="Cipher text (or pipe via STDIN)")
    pd.set_defaults(func=cmd_decrypt)

    pt = sub.add_parser("test", help="Run a quick round-trip self test")
    pt.add_argument("--key", type=str, default="GARUDA")
    pt.add_argument("--theme", type=str, required=True)
    pt.set_defaults(func=cmd_test)

    args = p.parse_args()
    if args.command:
        args.func(args)

if __name__ == "__main__":
    main()
