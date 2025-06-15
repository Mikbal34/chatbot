#!/usr/bin/env python3
"""
Path ve dosya sorunlarını düzeltme betiği
"""

import os
import sys
import shutil

def fix_env_file():
    """example.env dosyasını .env olarak kopyalar"""
    print("Çevre değişkenleri dosyası (.env) kontrol ediliyor...")
    
    if not os.path.exists(".env"):
        if os.path.exists("example.env"):
            shutil.copy("example.env", ".env")
            print("✅ example.env dosyası .env olarak kopyalandı")
        else:
            print("⚠️ example.env dosyası bulunamadı!")
            return False
    else:
        print("✅ .env dosyası zaten mevcut")
    
    return True

def fix_data_paths():
    """Veri dosyalarının var olup olmadığını kontrol eder"""
    print("\nVeri dosyaları kontrol ediliyor...")
    
    data_files = {
        "havalimani.xlsx": "data/reference/havalimani.xlsx",
        "kargo.xlsx": "data/reference/kargo.xlsx",
        "restoran-siparis.xlsx": "data/reference/restoran-siparis.xlsx",
        "restoran-rezervasyon.xlsx": "data/reference/restoran-rezervasyon.xlsx"
    }
    
    all_exist = True
    # Sadece dosyaların var olup olmadığını kontrol et
    for file_name, source_path in data_files.items():
        if os.path.exists(source_path):
            print(f"✅ {source_path} dosyası mevcut")
        else:
            print(f"⚠️ {source_path} dosyası bulunamadı!")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    print("Dosya yolu sorunlarını düzeltme işlemi başlatılıyor...\n")
    
    env_ok = fix_env_file()
    data_ok = fix_data_paths()
    
    if env_ok and data_ok:
        print("\n✅ Tüm dosya yolu sorunları giderildi! Şimdi uygulamayı çalıştırabilirsiniz.")
    else:
        print("\n⚠️ Bazı sorunlar çözülemedi. Lütfen manuel olarak kontrol edin.") 