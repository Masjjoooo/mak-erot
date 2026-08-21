```markdown
# 🚀 MAK EROT v3 - Marriott Bonvoy Auto Registration

<div align="center">
  
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
  [![Selenium](https://img.shields.io/badge/Selenium-4.0+-green.svg)](https://www.selenium.dev/)
  [![2Captcha](https://img.shields.io/badge/2Captcha-API-orange.svg)](https://2captcha.com/)
  [![Termux](https://img.shields.io/badge/Termux-Compatible-brightgreen.svg)](https://termux.com/)
  
  <p align="center">
    <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status">
    <img src="https://img.shields.io/badge/Version-3.0-red.svg" alt="Version">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  </p>
  
  <p><b>Otomatisasi Registrasi Marriott Bonvoy dengan 2Captcha & Temp Mail</b></p>
  
  <p>✨ <b>MAK EROT v3</b> adalah tools untuk auto register akun Marriott Bonvoy secara massal dengan dukungan reCAPTCHA solver via 2Captcha dan temporary email dari Gwenjot Mail API.</p>
  
</div>

---

## 📋 Daftar Isi

- [Fitur Utama](#-fitur-utama)
- [Prerequisites](#-prerequisites)
- [Instalasi](#-instalasi)
- [Cara Penggunaan](#-cara-penggunaan)
- [Struktur Data](#-struktur-data)
- [Flow Diagram](#-flow-diagram)
- [Troubleshooting](#-troubleshooting)
- [Disclaimer](#-disclaimer)
- [Lisensi](#-lisensi)

---

## ⚡ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 🤖 **Auto Register** | Registrasi akun Marriott Bonvoy otomatis |
| 🧩 **2Captcha Integration** | Solve reCAPTCHA v2 via 2Captcha API |
| 📧 **Temp Mail** | Menggunakan Gwenjot Mail API untuk email sementara |
| 🔄 **Multi Account** | Buat multiple akun sekaligus |
| 💾 **Data Export** | Simpan data ke CSV (nama, email, password, member ID) |
| 🌐 **Termux Support** | Berjalan di Android via Termux |
| ⏯️ **Interactive Loop** | Kontrol penuh proses registrasi |

---

## 📦 Prerequisites

### Untuk PC / Laptop
- Python 3.8 atau lebih baru
- Chrome Browser
- ChromeDriver (sesuai versi Chrome)
- Koneksi Internet

### Untuk Android (Termux)
```bash
# Install Termux dari F-Droid atau Google Play
# Kemudian jalankan:
pkg update && pkg upgrade
pkg install python chromium chromedriver
```

Akun yang Dibutuhkan

· 2Captcha API Key - Daftar di 2Captcha.com
· Gwenjot Mail - Gratis, sudah terintegrasi

---

🛠️ Instalasi

1. Clone Repository

```bash
git clone https://github.com/yourusername/makerot.git
cd makerot
```

2. Install Dependencies

```bash
pip install -r requirements.txt
```

Atau manual:

```bash
pip install requests beautifulsoup4 selenium
```

3. Setup ChromeDriver

Windows

1. Download ChromeDriver
2. Extract dan letakkan di C:\Windows\System32\ atau tambahkan ke PATH

Linux / Termux

```bash
# Termux
pkg install chromedriver

# Linux
sudo apt-get install chromium-chromedriver
```

macOS

```bash
brew install chromedriver
```

4. Buat File Requirements

Buat file requirements.txt:

```txt
requests>=2.28.0
beautifulsoup4>=4.11.0
selenium>=4.0.0
lxml>=4.9.0
```

---

🚀 Cara Penggunaan

Jalankan Script

```bash
python mak.py
```

Alur Input

```
  ███╗   ███╗ █████╗ ██╗  ██╗    ███████╗██████╗  ██████╗ ████████╗
  ████╗ ████║██╔══██╗██║ ██╔╝    ██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝
  ██╔████╔██║███████║█████╔╝     █████╗  ██████╔╝██║   ██║   ██║   
  ██║╚██╔╝██║██╔══██║██╔═██╗     ██╔══╝  ██╔══██╗██║   ██║   ██║   
  ██║ ╚═╝ ██║██║  ██║██║  ██╗    ███████╗██║  ██║╚██████╔╝   ██║   
  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   
                                                                     
                          v3 © Masjjoooo 2026

============================================================
🤖 MARRIOTT BONVOY AUTO REGISTRATION v3
============================================================

🔑 Masukkan 2Captcha API Key (atau kosongkan untuk manual): 
🔑 Masukkan password (min 8 karakter, huruf besar/kecil, angka/simbol): 
📊 Berapa akun yang ingin dibuat? 
```

Menu Opsi Setelah Setiap Akun

```
============================================================
📋 Opsi:
  [1] Lanjut buat akun berikutnya
  [2] Hentikan proses
  [3] Keluar dari program
============================================================
```

---

📊 Struktur Data

Output CSV: marriott_accounts.csv

Column Description
account_num Nomor urut akun
first_name Nama depan
last_name Nama belakang
email Email temp mail
phone Nomor telepon (Indonesia)
password Password yang digunakan
member_id Nomor keanggotaan Marriott
created_at Waktu pembuatan akun

Contoh Data

```csv
account_num,first_name,last_name,email,phone,password,member_id,created_at
1,John,Smith,abc123@anl.my.id,081234567890,MySecurePass123!,123456789,2026-08-21 10:30:00
```

---

📈 Flow Diagram

```
┌─────────────────┐
│  START PROGRAM  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Input Password │
│  & Jumlah Akun  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Akses Landing  │
│     Page        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ekstrak Param  │
│  prefill_id     │
│  client_id      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Buka Browser   │
│  Registrasi     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Isi Form       │
│  (Nama, Email,  │
│   Telepon)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Kirim Kode     │
│  Verifikasi     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Tunggu Email   │
│  & Ekstrak Kode │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Isi Password   │
│  & Centang      │
│  Persetujuan    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2Captcha       │
│  Solve CAPTCHA  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Submit &       │
│  Get Member ID  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Save to CSV    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Tanya Lanjut?  │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
  YES        NO
    │         │
    ▼         ▼
  LOOP     EXIT
```

---

🐛 Troubleshooting

Error: ModuleNotFoundError: No module named 'distutils'

Solusi: Python 3.14+ menghapus distutils. Install setuptools:

```bash
pip install setuptools
```

Error: ChromeDriver not found

Solusi Termux:

```bash
pkg install chromedriver
which chromedriver
# Output: /data/data/com.termux/files/usr/bin/chromedriver
```

Solusi Windows:

1. Download ChromeDriver dari sini
2. Letakkan di folder project atau tambahkan ke PATH

Error: reCAPTCHA tidak tersolve

Solusi:

1. Cek API Key 2Captcha (pastikan ada saldo)
2. Jika tidak punya API Key, script akan fallback ke manual
3. Selesaikan reCAPTCHA manual di browser

Error: Email tidak masuk

Solusi:

1. Cek koneksi internet
2. Coba domain email lain di Gwenjot Mail
3. Tunggu lebih lama (beberapa email butuh waktu)

---

⚠️ Disclaimer

PENTING!

1. Tools ini dibuat untuk tujuan edukasi dan testing otomatisasi
2. Gunakan dengan bijak dan patuhi Terms of Service Marriott
3. Pembuat tidak bertanggung jawab atas penyalahgunaan tools ini
4. Jangan digunakan untuk spam atau aktivitas ilegal
5. Registrasi massal dapat mengakibatkan IP banned
6. Selalu hormati privasi dan data pribadi

---

📝 Lisensi

```
MIT License

Copyright (c) 2026 Masjjoooo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

🙏 Credits

Contributor Role
Masjjoooo Developer & Maintainer
2Captcha CAPTCHA Solver API
Gwenjot Mail Temporary Email API
Marriott Bonvoy Target Platform

---

📞 Contact & Support

· GitHub Issues: Laporkan Bug
· Telegram: @masjjoooo

---

<div align="center">

  <p>Made with ❤️ by <b>Masjjoooo</b></p>

⭐ Star this repo if you find it useful! ⭐

</div>
```

---
