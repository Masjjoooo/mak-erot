import os
import sys
import time
import json
import re
import random
import string
import csv
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import requests

# ============================================================
# ASCII ART - MAK EROT v3
# ============================================================
ASCII_BANNER = r"""
  ███╗   ███╗ █████╗ ██╗  ██╗    ███████╗██████╗  ██████╗ ████████╗
  ████╗ ████║██╔══██╗██║ ██╔╝    ██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝
  ██╔████╔██║███████║█████╔╝     █████╗  ██████╔╝██║   ██║   ██║   
  ██║╚██╔╝██║██╔══██║██╔═██╗     ██╔══╝  ██╔══██╗██║   ██║   ██║   
  ██║ ╚═╝ ██║██║  ██║██║  ██╗    ███████╗██║  ██║╚██████╔╝   ██║   
  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   
                                                                     
                          v3 © Masjjoooo 2026
"""

# ============================================================
# KONFIGURASI 2CAPTCHA
# ============================================================
class TwoCaptchaSolver:
    """Kelas untuk menyelesaikan reCAPTCHA menggunakan 2Captcha"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://2captcha.com"
        self.polling_interval = 5
        self.max_retries = 30
        
    def solve_recaptcha_v2(self, sitekey, page_url, invisible=0):
        """Mengirim reCAPTCHA v2 ke 2Captcha dan mendapatkan token solusi"""
        print("🧩 Mengirim reCAPTCHA ke 2Captcha...")
        
        send_data = {
            'key': self.api_key,
            'method': 'userrecaptcha',
            'googlekey': sitekey,
            'pageurl': page_url,
            'invisible': invisible,
            'json': 1
        }
        
        try:
            response = requests.post(f"{self.base_url}/in.php", data=send_data)
            result = response.json()
            
            if result.get('status') != 1:
                print(f"❌ Gagal mengirim captcha: {result.get('request')}")
                return None
            
            captcha_id = result.get('request')
            print(f"✅ Captcha terkirim! ID: {captcha_id}")
            
            return self._get_captcha_result(captcha_id)
            
        except Exception as e:
            print(f"❌ Error mengirim captcha: {e}")
            return None
    
    def _get_captcha_result(self, captcha_id):
        """Polling 2Captcha untuk mendapatkan hasil solusi"""
        print("⏳ Menunggu solusi captcha...")
        
        for attempt in range(self.max_retries):
            try:
                result_data = {
                    'key': self.api_key,
                    'action': 'get',
                    'id': captcha_id,
                    'json': 1
                }
                
                response = requests.get(f"{self.base_url}/res.php", params=result_data)
                result = response.json()
                
                if result.get('status') == 1:
                    token = result.get('request')
                    print(f"✅ Captcha berhasil dipecahkan!")
                    return token
                elif result.get('request') == 'CAPCHA_NOT_READY':
                    print(f"   Menunggu... (percobaan {attempt + 1}/{self.max_retries})")
                    time.sleep(self.polling_interval)
                else:
                    print(f"❌ Error dari 2Captcha: {result.get('request')}")
                    return None
                    
            except Exception as e:
                print(f"⚠️ Error polling: {e}")
                time.sleep(self.polling_interval)
        
        print("❌ Timeout menunggu solusi captcha")
        return None

# ============================================================
# KELAS UTAMA REGISTRASI MARRIOTT
# ============================================================
class MarriottAutoRegister:
    """Kelas untuk otomatisasi registrasi Marriott Bonvoy"""
    
    def __init__(self, custom_password, twocaptcha_api_key):
        self.temp_mail_api = "https://gwenjotmail.anl.my.id/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Data user random
        self.username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        self.email = f"{self.username}@anl.my.id"
        self.password = custom_password
        self.first_name = random.choice(['John', 'Michael', 'David', 'James', 'Robert', 'William', 'Daniel', 'Matthew'])
        self.last_name = random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'])
        self.phone = f"08{''.join(random.choices(string.digits, k=10))}"
        self.member_id = None
        
        # Parameter dari landing page
        self.prefill_id = None
        self.client_id = None
        self.landing_page_url = "https://www.joinmarriottbonvoy.com/streamlined/agnostic_landing.aspx?ctycode=ID&promo=Mbvbb26"
        
        # 2Captcha
        self.captcha_solver = TwoCaptchaSolver(twocaptcha_api_key) if twocaptcha_api_key else None
        
        # Selenium driver
        self.driver = None
        
    def extract_params_from_landing_page(self):
        """Ekstrak parameter dari halaman landing page menggunakan requests"""
        print("📄 Mengambil parameter dari halaman landing...")
        
        try:
            # Ambil halaman landing
            response = self.session.get(self.landing_page_url)
            response.raise_for_status()
            
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            # Cari link registrasi di halaman
            # Cari di semua link
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'auth.marriott.com/enroll' in href:
                    print(f"✓ Menemukan link registrasi: {href}")
                    return self._parse_enroll_url(href)
            
            # Cari di script atau form
            for script in soup.find_all('script'):
                if script.string and 'auth.marriott.com/enroll' in script.string:
                    match = re.search(r'https://auth\.marriott\.com/enroll\?[^\s"\']+', script.string)
                    if match:
                        print(f"✓ Menemukan link registrasi di script: {match.group()}")
                        return self._parse_enroll_url(match.group())
            
            # Cari di attribute
            for elem in soup.find_all(attrs={"href": re.compile(r'auth\.marriott\.com/enroll')}):
                href = elem.get('href')
                if href:
                    print(f"✓ Menemukan link registrasi: {href}")
                    return self._parse_enroll_url(href)
            
            print("⚠️ Tidak menemukan link registrasi di landing page")
            return None
            
        except Exception as e:
            print(f"❌ Error mengambil landing page: {e}")
            return None
    
    def _parse_enroll_url(self, url):
        """Parse URL enroll untuk mendapatkan parameter"""
        params = {}
        
        # Cari prefill_id
        match = re.search(r'prefill_id=([^&]+)', url)
        if match:
            params['prefill_id'] = match.group(1)
            print(f"   ✓ prefill_id: {params['prefill_id']}")
        
        # Cari client_id
        match = re.search(r'client_id=([^&]+)', url)
        if match:
            params['client_id'] = match.group(1)
            print(f"   ✓ client_id: {params['client_id']}")
        
        # Cari locale
        match = re.search(r'locale=([^&]+)', url)
        if match:
            params['locale'] = match.group(1)
            print(f"   ✓ locale: {params['locale']}")
        
        self.prefill_id = params.get('prefill_id')
        self.client_id = params.get('client_id')
        
        return params
    
    def build_enroll_url(self):
        """Bangun URL enroll dari parameter yang didapat"""
        if self.prefill_id and self.client_id:
            return f"https://auth.marriott.com/enroll?prefill_id={self.prefill_id}&client_id={self.client_id}&locale=id-ID"
        return None
    
    def setup_selenium(self):
        """Setup Chrome driver untuk Termux"""
        options = Options()
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            chrome_driver_path = "/data/data/com.termux/files/usr/bin/chromedriver"
            
            if os.path.exists(chrome_driver_path):
                service = Service(chrome_driver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
                
            self.driver.set_window_size(1366, 768)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return True
            
        except Exception as e:
            print(f"❌ Gagal setup ChromeDriver: {e}")
            print("\n📌 SOLUSI:")
            print("1. Install ChromeDriver di Termux:")
            print("   pkg install chromium chromedriver")
            return False
    
    def access_inbox(self):
        """Akses inbox temp mail"""
        try:
            payload = {"address": self.email}
            response = requests.post(
                f"{self.temp_mail_api}/access",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                print(f"✓ Email aktif: {self.email}")
                return True
            else:
                print(f"✗ Gagal akses inbox: {response.text}")
                return False
        except Exception as e:
            print(f"Error akses inbox: {e}")
            return False
    
    def get_emails(self):
        """Ambil daftar email dari inbox"""
        try:
            response = requests.get(
                f"{self.temp_mail_api}/emails",
                params={"address": self.email}
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error mendapatkan email: {e}")
        return []
    
    def wait_for_email(self, timeout=180, check_interval=5):
        """Tunggu email verifikasi"""
        print(f"⏳ Menunggu email verifikasi... (max {timeout}s)")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            emails = self.get_emails()
            if emails and len(emails) > 0:
                print(f"✓ Menerima {len(emails)} email")
                return emails
            time.sleep(check_interval)
        
        print("✗ Timeout menunggu email")
        return None
    
    def extract_verification_code(self, emails):
        """Ekstrak kode verifikasi dari email"""
        if not emails:
            return None
        
        for email in emails:
            if 'body' in email:
                if 'html' in email['body']:
                    html_content = email['body']['html']
                    code_patterns = [
                        r'\b\d{6}\b',
                        r'verification code:?\s*(\d{6})',
                        r'kode verifikasi:?\s*(\d{6})',
                        r'OTP:?\s*(\d{6})',
                        r'code:?\s*(\d{6})'
                    ]
                    
                    for pattern in code_patterns:
                        match = re.search(pattern, html_content, re.IGNORECASE)
                        if match:
                            code = match.group(1) if match.group(1) else match.group(0)
                            print(f"✓ Kode verifikasi: {code}")
                            return code
                
                if 'text' in email['body']:
                    text = email['body']['text']
                    for pattern in code_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            code = match.group(1) if match.group(1) else match.group(0)
                            print(f"✓ Kode verifikasi: {code}")
                            return code
        
        return None
    
    def extract_member_id(self, url):
        """Ekstrak nomor keanggotaan dari halaman thanks"""
        try:
            self.driver.get(url)
            time.sleep(3)
            
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            patterns = [
                r'Nomor keanggotaan Anda adalah\s*(\d+)',
                r'member number is\s*(\d+)',
                r'MR\s*(\d+)',
                r'keanggotaan.*?(\d{9,})',
                r'member.*?(\d{9,})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    member_id = match.group(1)
                    print(f"✓ Nomor keanggotaan: {member_id}")
                    return member_id
            
            page_text = soup.get_text()
            for pattern in patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    member_id = match.group(1)
                    print(f"✓ Nomor keanggotaan: {member_id}")
                    return member_id
            
            print("⚠ Tidak dapat menemukan nomor keanggotaan")
            return None
            
        except Exception as e:
            print(f"✗ Error ekstrak member ID: {e}")
            return None
    
    def solve_captcha_with_2captcha(self):
        """Selesaikan reCAPTCHA menggunakan 2Captcha"""
        if not self.captcha_solver:
            print("⚠️ 2Captcha API key tidak tersedia. Harap selesaikan captcha manual.")
            input("Tekan ENTER setelah menyelesaikan captcha secara manual...")
            return True
        
        try:
            sitekey = None
            recaptcha_elements = self.driver.find_elements(By.CSS_SELECTOR, ".g-recaptcha, [data-sitekey]")
            
            for elem in recaptcha_elements:
                sitekey = elem.get_attribute('data-sitekey')
                if sitekey:
                    break
            
            if not sitekey:
                print("⚠️ Tidak menemukan sitekey reCAPTCHA. Coba cari di iframe...")
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    src = iframe.get_attribute('src')
                    if 'recaptcha' in src:
                        match = re.search(r'k=([^&]+)', src)
                        if match:
                            sitekey = match.group(1)
                            break
            
            if not sitekey:
                print("❌ Tidak dapat menemukan sitekey. Harap selesaikan captcha manual.")
                input("Tekan ENTER setelah menyelesaikan captcha secara manual...")
                return True
            
            print(f"🔑 Sitekey ditemukan: {sitekey}")
            
            page_url = self.driver.current_url
            token = self.captcha_solver.solve_recaptcha_v2(sitekey, page_url)
            
            if not token:
                print("❌ Gagal mendapatkan solusi dari 2Captcha. Silakan coba manual.")
                input("Tekan ENTER setelah menyelesaikan captcha secara manual...")
                return True
            
            try:
                self.driver.execute_script(f"""
                    var element = document.getElementById('g-recaptcha-response');
                    if (element) {{
                        element.style.display = 'block';
                        element.value = '{token}';
                    }}
                    
                    if (typeof ___grecaptcha_cfg !== 'undefined') {{
                        for (var i = 0; i < 10; i++) {{
                            try {{
                                var callback = ___grecaptcha_cfg.clients[i]?.aa?.l?.callback;
                                if (typeof callback === 'function') {{
                                    callback('{token}');
                                    break;
                                }}
                            }} catch(e) {{}}
                        }}
                    }}
                """)
                time.sleep(2)
                
                print("✅ Token reCAPTCHA berhasil di-inject")
                return True
                
            except Exception as e:
                print(f"⚠️ Error inject token: {e}")
                print("Silakan selesaikan captcha secara manual.")
                input("Tekan ENTER setelah selesai...")
                return True
                
        except Exception as e:
            print(f"⚠️ Error solving captcha: {e}")
            print("Silakan selesaikan captcha secara manual.")
            input("Tekan ENTER setelah selesai...")
            return True
    
    def fill_form_field(self, field_id, value, wait_time=0.5):
        """Isi field form berdasarkan ID"""
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, field_id))
            )
            element.clear()
            element.send_keys(value)
            time.sleep(wait_time)
            return True
        except Exception as e:
            print(f"⚠️ Gagal mengisi {field_id}: {e}")
            return False
    
    def register(self, account_num):
        """Proses registrasi utama"""
        print(f"\n{'='*60}")
        print(f"🚀 Membuat Akun #{account_num}")
        print(f"{'='*60}")
        
        # Step 1: Setup temp mail
        print("\n📧 Menyiapkan email sementara...")
        if not self.access_inbox():
            return False
        
        # Step 2: Ambil parameter dari landing page
        print("\n🔍 Mengambil parameter dari landing page...")
        params = self.extract_params_from_landing_page()
        
        if not params or not self.prefill_id:
            print("❌ Gagal mendapatkan parameter dari landing page")
            print("   Mencoba menggunakan URL default...")
            enroll_url = "https://auth.marriott.com/enroll?prefill_id=4e7d8ae5-b0ef-4eb7-b2df-a0fc8b4ac846&client_id=netl_auth&locale=id-ID"
        else:
            enroll_url = self.build_enroll_url()
        
        print(f"📄 URL Registrasi: {enroll_url}")
        
        # Step 3: Setup browser
        print("\n🌐 Membuka browser...")
        if not self.setup_selenium():
            return False
        
        try:
            # Step 4: Buka halaman registrasi
            print("\n📄 Membuka halaman registrasi...")
            self.driver.get(enroll_url)
            time.sleep(5)
            
            print(f"\n📝 Mengisi form registrasi...")
            print(f"   Email: {self.email}")
            print(f"   Nama: {self.first_name} {self.last_name}")
            print(f"   Telepon: {self.phone}")
            
            # Isi Nama Depan
            print("   ✓ Mengisi nama depan...")
            self.fill_form_field(":R56d6:-firstName", self.first_name)
            
            # Isi Nama Belakang
            print("   ✓ Mengisi nama belakang...")
            self.fill_form_field(":R56d6:-lastName", self.last_name)
            
            # Pilih Negara
            print("   ✓ Memilih negara...")
            try:
                country_dropdown = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "dropdownfp-country-code"))
                )
                country_dropdown.click()
                time.sleep(0.5)
                
                indonesia_option = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//li[contains(text(), 'Indonesia')]"))
                )
                indonesia_option.click()
                time.sleep(0.5)
            except Exception as e:
                print(f"   ⚠️ Gagal pilih negara: {e}")
            
            # Isi Email
            print("   ✓ Mengisi email...")
            self.fill_form_field(":R56d6:-Email", self.email)
            
            # Isi Telepon
            print("   ✓ Mengisi telepon...")
            phone_field = self.driver.find_element(By.ID, ":r0:-Dialcode")
            phone_field.clear()
            phone_field.send_keys(self.phone)
            time.sleep(0.5)
            
            # Step 5: Kirim kode verifikasi
            print("\n📨 Mengirim kode verifikasi...")
            
            try:
                email_radio = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "email"))
                )
                if not email_radio.is_selected():
                    email_radio.click()
                    time.sleep(0.5)
            except Exception as e:
                print(f"   ⚠️ Gagal pilih radio email: {e}")
            
            send_code_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='send-code-btn']"))
            )
            send_code_btn.click()
            time.sleep(3)
            
            print("   ✓ Kode verifikasi dikirim ke email")
            
            # Step 6: Tunggu kode verifikasi
            print("\n⏳ Menunggu kode verifikasi...")
            emails = self.wait_for_email(timeout=120)
            verification_code = None
            
            if emails:
                verification_code = self.extract_verification_code(emails)
                if verification_code:
                    print(f"   ✓ Kode verifikasi: {verification_code}")
                    
                    print("\n🔑 Memasukkan kode verifikasi...")
                    code_field = self.driver.find_element(By.ID, ":R56d6:-verificationCode")
                    code_field.clear()
                    code_field.send_keys(verification_code)
                    time.sleep(1)
                    time.sleep(3)
            
            # Step 7: Isi Password
            print("\n🔐 Membuat password...")
            
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            time.sleep(0.5)
            
            confirm_password_field = self.driver.find_element(By.ID, "confirmPassword")
            confirm_password_field.clear()
            confirm_password_field.send_keys(self.password)
            time.sleep(0.5)
            
            # Step 8: Selesaikan reCAPTCHA
            print("\n🤖 Menyelesaikan reCAPTCHA...")
            self.solve_captcha_with_2captcha()
            
            # Step 9: Centang semua checkbox persetujuan
            print("\n📋 Menceklis persetujuan...")
            
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            for checkbox in checkboxes:
                try:
                    if not checkbox.is_selected() and not checkbox.get_attribute('disabled'):
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                        time.sleep(0.3)
                        checkbox.click()
                        time.sleep(0.3)
                except Exception:
                    pass
            
            print("   ✓ Semua persetujuan diceklis")
            
            # Step 10: Klik "Gabung Sekarang"
            print("\n🚀 Mengirim registrasi...")
            
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            join_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='joinCta']"))
            )
            join_btn.click()
            time.sleep(5)
            
            print(f"\n✅ Registrasi berhasil dikirim!")
            
            # Step 11: Ambil nomor keanggotaan
            print("\n📋 Mengambil nomor keanggotaan...")
            thanks_url = "https://www.joinmarriottbonvoy.com/Mbvbb26/s/thanks/ID"
            self.member_id = self.extract_member_id(thanks_url)
            
            if self.member_id:
                print(f"✓ Nomor Keanggotaan: {self.member_id}")
            else:
                print("⚠️ Gagal mengambil nomor keanggotaan")
            
            print(f"\n{'='*40}")
            print(f"✅ AKUN #{account_num} BERHASIL!")
            print(f"{'='*40}")
            print(f"📧 Email: {self.email}")
            print(f"🔑 Password: {self.password}")
            print(f"📱 Telepon: {self.phone}")
            print(f"🆔 Member ID: {self.member_id or 'N/A'}")
            print(f"👤 Nama: {self.first_name} {self.last_name}")
            print(f"{'='*40}")
            
            return True
                
        except Exception as e:
            print(f"✗ Error registrasi: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if self.driver:
                time.sleep(2)
                self.driver.quit()
    
    def save_account_data(self, account_data, filename="marriott_accounts.csv"):
        """Simpan data akun ke CSV"""
        file_exists = os.path.isfile(filename)
        
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['account_num', 'first_name', 'last_name', 'email', 'phone', 'password', 'member_id', 'created_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(account_data)
        
        print(f"✓ Data tersimpan di {filename}")

# ============================================================
# FUNGSI UTAMA
# ============================================================
def get_user_input():
    """Dapatkan input dari user"""
    print(ASCII_BANNER)
    print("\n" + "="*60)
    print("🤖 MARRIOTT BONVOY AUTO REGISTRATION v3")
    print("="*60)
    
    api_key = input("\n🔑 Masukkan 2Captcha API Key (atau kosongkan untuk manual): ").strip()
    
    while True:
        password = input("\n🔑 Masukkan password (min 8 karakter, huruf besar/kecil, angka/simbol): ")
        if len(password) >= 8:
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit_or_symbol = any(c.isdigit() or c in '!@#$%^&*' for c in password)
            
            if has_upper and has_lower and has_digit_or_symbol:
                confirm = input("Konfirmasi password: ")
                if confirm == password:
                    break
                else:
                    print("❌ Password tidak cocok!")
            else:
                print("❌ Password harus mengandung huruf besar, kecil, dan angka/simbol")
        else:
            print("❌ Password minimal 8 karakter")
    
    while True:
        try:
            num_accounts = int(input("\n📊 Berapa akun yang ingin dibuat? "))
            if num_accounts > 0:
                break
            else:
                print("❌ Masukkan angka positif")
        except ValueError:
            print("❌ Masukkan angka yang valid")
    
    return api_key, password, num_accounts

def check_dependencies():
    """Cek dependensi yang dibutuhkan"""
    print("\n📌 Cek Dependensi...")
    
    try:
        from selenium import webdriver
        print("✓ Selenium terinstall")
    except ImportError:
        print("❌ Selenium tidak terinstall. Install dengan: pip install selenium")
        return False
    
    try:
        import requests
        print("✓ Requests terinstall")
    except ImportError:
        print("❌ Requests tidak terinstall. Install dengan: pip install requests")
        return False
    
    try:
        import bs4
        print("✓ BeautifulSoup4 terinstall")
    except ImportError:
        print("❌ BeautifulSoup4 tidak terinstall. Install dengan: pip install beautifulsoup4")
        return False
    
    print("\n📌 Pastikan Chromium & ChromeDriver sudah terinstall:")
    print("   pkg install chromium chromedriver")
    
    return True

def main():
    """Fungsi utama dengan loop"""
    if not check_dependencies():
        print("\n❌ Install dependensi yang kurang terlebih dahulu.")
        return
    
    api_key, password, num_accounts = get_user_input()
    
    all_accounts = []
    account_counter = 0
    
    while True:
        try:
            if account_counter >= num_accounts:
                print(f"\n✅ Semua {num_accounts} akun telah dibuat!")
                break
            
            account_counter += 1
            print(f"\n{'='*60}")
            print(f"🔄 Membuat akun {account_counter}/{num_accounts}")
            print(f"{'='*60}")
            
            register = MarriottAutoRegister(password, api_key)
            success = register.register(account_counter)
            
            if success:
                account_data = {
                    'account_num': account_counter,
                    'first_name': register.first_name,
                    'last_name': register.last_name,
                    'email': register.email,
                    'phone': register.phone,
                    'password': register.password,
                    'member_id': register.member_id or 'N/A',
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                all_accounts.append(account_data)
                register.save_account_data(account_data)
                print(f"✅ Akun {account_counter} berhasil dibuat!")
            else:
                print(f"❌ Akun {account_counter} gagal dibuat")
            
            if account_counter >= num_accounts:
                break
                
            print("\n" + "="*60)
            print("📋 Opsi:")
            print("  [1] Lanjut buat akun berikutnya")
            print("  [2] Hentikan proses")
            print("  [3] Keluar dari program")
            print("="*60)
            
            choice = input("Pilih opsi (1/2/3): ").strip()
            
            if choice == '2':
                print("\n⏹️ Proses dihentikan oleh user.")
                break
            elif choice == '3':
                print("\n👋 Keluar dari program. Sampai jumpa!")
                return
            else:
                print("\n⏳ Melanjutkan ke akun berikutnya...")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n👋 Program dihentikan oleh user. Sampai jumpa!")
            return
        except Exception as e:
            print(f"\n❌ Error tak terduga: {e}")
            choice = input("\nLanjutkan? (y/n): ").strip().lower()
            if choice != 'y':
                break
    
    print(f"\n{'='*60}")
    print("📊 RINGKASAN REGISTRASI")
    print(f"{'='*60}")
    print(f"✅ Berhasil: {len(all_accounts)}/{num_accounts} akun")
    
    if all_accounts:
        print("\n📋 Daftar Akun:")
        for acc in all_accounts:
            print(f"\n  Akun #{acc['account_num']}:")
            print(f"    Nama: {acc['first_name']} {acc['last_name']}")
            print(f"    Email: {acc['email']}")
            print(f"    Password: {acc['password']}")
            print(f"    Telepon: {acc['phone']}")
            print(f"    Member ID: {acc['member_id']}")
        
        print(f"\n💾 Data tersimpan di: marriott_accounts.csv")
    
    print(f"{'='*60}")
    
    choice = input("\n🔄 Buat akun lagi dari awal? (y/n): ").strip().lower()
    if choice == 'y':
        print("\n" + "="*60)
        print("🔄 Memulai ulang program...")
        print("="*60)
        main()
    else:
        print("\n👋 Terima kasih telah menggunakan MAK EROT v3!")
        print("© Masjjoooo 2026")

if __name__ == "__main__":
    main()
