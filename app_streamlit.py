
import streamlit as st
import re
from pathlib import Path
from src.ciphers import caesar, vigenere
from src.codebook import Codebook
from src.pantun import layout_abab

st.set_page_config(page_title="Lirik/Pantun Cipher", layout="centered")
st.title("🎶 Lirik/Pantun Cipher — GUI")
st.caption("Encrypt plaintext → lirik/pantun, dan decrypt kembali secara deterministik.")

# Sidebar: Theme (Codebook)
st.sidebar.header("🎨 Theme / Codebook")
default_theme_path = Path("data/themes/default_codebook.json")
theme_bytes = None

use_custom = st.sidebar.checkbox("Upload custom theme (JSON)", value=False)
if use_custom:
    up = st.sidebar.file_uploader("Pilih file JSON codebook", type=["json"])
    if up is not None:
        theme_bytes = up.read()
else:
    if default_theme_path.exists():
        theme_bytes = default_theme_path.read_bytes()
    else:
        st.sidebar.error("Default theme tidak ditemukan: data/themes/default_codebook.json")

codebook = None
if theme_bytes:
    try:
        with open(".active_theme.json", "wb") as f:
            f.write(theme_bytes)
        codebook = Codebook.load_json(".active_theme.json")
        st.sidebar.success(f"Theme loaded: {codebook.name}")
    except Exception as e:
        st.sidebar.error(f"Gagal load theme: {e}")

# Controls
st.subheader("Mode & Kunci")
algo = st.selectbox("Algoritma klasik", ["vigenere", "caesar"], index=0)
key = st.text_input("Key", value="GARUDA", help="Untuk Vigenère, hanya huruf memengaruhi shift.")
pantun = st.checkbox("Pantun mode (ABAB)", value=True)
normalize = st.checkbox("Normalize spaces saat decrypt", value=False)

st.subheader("Teks")
tab1, tab2 = st.tabs(["Encrypt", "Decrypt"])

def do_encrypt(txt: str) -> str:
    if algo == "vigenere":
        step = vigenere.encrypt(txt, key or "")
    else:
        step = caesar.encrypt(txt, key or "")
    code_words = codebook.encode_bytes(step.encode("utf-8")).split()
    if pantun:
        lines = layout_abab(code_words, codebook.rhyme_suffixes.get("a",["a","u"]),
                                         codebook.rhyme_suffixes.get("b",["i","e"]))
        out = ",\n".join(lines[:3]) + ".\n" + lines[3] + "."
    else:
        out = " ".join(code_words)
    return out

def do_decrypt(txt: str) -> str:
    cleaned = re.sub(r"[,\.]+", "", txt)
    raw = codebook.decode_to_bytes(cleaned).decode("utf-8")
    if algo == "vigenere":
        plain = vigenere.decrypt(raw, key or "")
    else:
        plain = caesar.decrypt(raw, key or "")
    if normalize:
        plain = re.sub(r"\s+", " ", plain).strip()
    return plain

with tab1:
    pt = st.text_area("Plaintext", height=140, placeholder="Tulis teks di sini...")
    if st.button("🔐 Encrypt"):
        if not pt:
            st.warning("Isi dulu plaintext-nya.")
        else:
            try:
                enc = do_encrypt(pt)
                st.success("Berhasil dienkripsi!")
                st.code(enc, language="text")
                st.download_button("⬇️ Download cipher", enc, file_name="cipher.txt")
            except Exception as e:
                st.error(f"Gagal encrypt: {e}")

with tab2:
    ct = st.text_area("Cipher text", height=180, placeholder="Tempel hasil cipher di sini...")
    if st.button("🔓 Decrypt"):
        if not ct:
            st.warning("Tempel dulu cipher-nya.")
        else:
            try:
                dec = do_decrypt(ct)
                st.success("Berhasil didekripsi!")
                st.code(dec, language="text")
                st.download_button("⬇️ Download plaintext", dec, file_name="plaintext.txt")
            except Exception as e:
                st.error(f"Gagal decrypt: {e}")
