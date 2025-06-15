#!/usr/bin/env python3
"""
Müşteri Hizmetleri Chatbot Ana Başlatma Betiği
"""

import sys
import os
import subprocess
import time

def run_command(command):
    """Komutu çalıştırır ve çıktıyı ekrana yazdırır"""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        shell=True
    )
    
    # Çıktıyı canlı olarak yazdır
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    return process.returncode

def main():
    # Proje kök dizinini belirle
    project_root = os.path.abspath(os.path.dirname(__file__))
    os.chdir(project_root)
    
    print("=" * 60)
    print("🤖 Müşteri Hizmetleri ChatBot Başlatılıyor...")
    print("=" * 60)
    
    # Dosya yollarını düzelt
    print("\n[1/2] Dosya yolları düzeltiliyor...")
    run_command("python fix_paths.py")
    
    # Web uygulamasını başlat
    print("\n[2/2] Web uygulaması başlatılıyor...\n")
    print("Web arayüzüne erişmek için tarayıcınızda http://localhost:5000 adresini açın")
    print("Uygulamayı durdurmak için CTRL+C tuşlarına basın\n")
    print("=" * 60 + "\n")
    
    # Web uygulamasını başlat
    run_command("python run_web.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program kapatılıyor... İyi günler!")
        sys.exit(0)
    except Exception as e:
        print(f"\n⛔ Kritik hata: {str(e)}")
        sys.exit(1) 