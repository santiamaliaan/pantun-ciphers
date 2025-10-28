# Lirik/Pantun Cipher (Python)

Aplikasi untuk mengenkripsi **plaintext** menjadi **cipher text yang terbaca** seperti lirik/pantun, dan dapat didekripsi kembali secara **deterministik** ke plaintext semula.

## Fitur Utama
- **Algoritma klasik**: Vigenère & Caesar (pilih salah satu saat berjalan).
- **Codebook/Homofonik bertema**: memetakan alfabet Base64 ke **kata/frasalirik** (unik & invertibel).
- **Pantun mode (ABAB)**: formatter 4 baris dengan pemilihan breakpoint deterministik agar ujung baris mengikuti rima sederhana (ABAB) *tanpa mengubah urutan token* sehingga tetap 100% dapat balik.
- **Lokalisasi**: menjaga spasi, tanda baca, dan huruf kapital (pada tahap klasik). Semua karakter non-alfabet dipertahankan.
- **100% Round-trip**: `decrypt(encrypt(plaintext)) == plaintext` (opsional normalisasi spasi tersedia).

## Alur Kriptografi
1. **Klasik (Vigenère/Caesar)**: Terapkan ke plaintext agar ada lapisan kriptografi standar (huruf A–Z/a–z). Non-alfabet tidak berubah, sehingga emoji/angka/tanda baca aman.
2. **Codebook Lyric**: Hasil tahap 1 di-**UTF‑8** lalu di-**Base64**, setiap simbol Base64 dipetakan ke sebuah **kata** dari codebook JSON (unik & invertibel). Inilah *cipher text bergaya lirik*.
3. **Pantun Mode (opsional)**: Token kata yang sudah jadi **dipecah** ke 4 baris. Algoritma memilih breakpoint agar kata terakhir baris 1 & 3 berakhiran sufiks grup **A** (mis. `u, ah, yu, du`) dan baris 2 & 4 grup **B** (mis. `i, ri, ni, ti`). **Tidak ada token yang diubah atau disisipkan**, sehingga dekripsi cukup mengabaikan tanda baca koma/titik.

## Arsitektur Singkat
```
src/
  ciphers/
    caesar.py       # Caesar (shift by sum(key) mod 26)
    vigenere.py     # Vigenère (huruf saja; non-alfabet passthrough)
  codebook.py       # Base64 <-> kata/lyric mapping; JSON profile & inverse map
  pantun.py         # ABAB line breaking (deterministik, tidak ubah token order)
  cli.py            # CLI: encrypt/decrypt/test
data/
  themes/
    default_codebook.json  # Profil tema (Indonesia), lengkap 65 token (Base64 + '=')
tests/
  test_roundtrip.py  # 5 skenario unit test
app_streamlit.py
requirements.txt
```
---
## Instalasi & Menjalankan (Python 3.9+).
Untuk menjalankan antarmuka web lokal:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app_streamlit.py
```
Lalu buka URL http://localhost:8501 di browser.
