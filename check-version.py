import subprocess, pytesseract, re

# path used by pytesseract
print("pytesseract uses:", pytesseract.pytesseract.tesseract_cmd)

# engine version
ver = subprocess.check_output([pytesseract.pytesseract.tesseract_cmd, "--version"], text=True)
print(ver.splitlines()[0])   # first line prints e.g.  "tesseract 5.3.4"
