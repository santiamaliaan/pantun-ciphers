import unittest, subprocess, os, sys, json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLI = ROOT / "src" / "cli.py"
THEME = ROOT / "data" / "themes" / "default_codebook.json"

def run_cmd(args, input_text=None):
    import subprocess
    if input_text is not None:
        p = subprocess.run([sys.executable, str(CLI)] + args, input=input_text.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        p = subprocess.run([sys.executable, str(CLI)] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {args}\nSTDERR:\n{p.stderr.decode()}")
    return p.stdout.decode("utf-8")

class TestRoundTrip(unittest.TestCase):
    def test_short_plain(self):
        txt = "Halo"
        enc = run_cmd(["encrypt","--algo","vigenere","--key","GARUDA","--theme",str(THEME)], input_text=txt)
        dec = run_cmd(["decrypt","--algo","vigenere","--key","GARUDA","--theme",str(THEME)], input_text=enc)
        self.assertEqual(txt, dec)

    def test_long_plain(self):
        txt = "PADAMU NEGERI JIWA RAGA KAMI, Indonesia jaya! " * 3
        enc = run_cmd(["encrypt","--algo","vigenere","--key","GARUDA","--theme",str(THEME)], input_text=txt)
        dec = run_cmd(["decrypt","--algo","vigenere","--key","GARUDA","--theme",str(THEME)], input_text=enc)
        self.assertEqual(txt, dec)

    def test_non_alphabet(self):
        txt = "1234567890 -- tetap utuh, non-alfabet."
        enc = run_cmd(["encrypt","--algo","caesar","--key","123","--theme",str(THEME)], input_text=txt)
        dec = run_cmd(["decrypt","--algo","caesar","--key","123","--theme",str(THEME)], input_text=enc)
        self.assertEqual(txt, dec)

    def test_multiline_pantun(self):
        txt = "Baris satu.\nBaris dua.\nBaris tiga."
        enc = run_cmd(["encrypt","--algo","vigenere","--key","KUNCI","--theme",str(THEME), "--pantun"], input_text=txt)
        dec = run_cmd(["decrypt","--algo","vigenere","--key","KUNCI","--theme",str(THEME)], input_text=enc)
        self.assertEqual(txt, dec)

    def test_emoji_and_acronym(self):
        txt = "APT/SOC 😊 tetap terbaca."
        enc = run_cmd(["encrypt","--algo","vigenere","--key","GARUDA","--theme",str(THEME)], input_text=txt)
        dec = run_cmd(["decrypt","--algo","vigenere","--key","GARUDA","--theme",str(THEME)], input_text=enc)
        self.assertEqual(txt, dec)

if __name__ == "__main__":
    unittest.main()
