"""
İlk kurulum için tabloyu oluşturur ve örnek verileri ekler
"""
import sys
import os
import subprocess

# Script'in bulunduğu dizini proje root'una ekle
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)
os.chdir(project_root)

def run_script(script_name):
    """Python script'ini çalıştırır"""
    try:
        result = subprocess.run([sys.executable, script_name], check=True)
        print(f"✓ {script_name} başarıyla çalıştırıldı")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {script_name} çalıştırılırken hata: {e}")
        return False

def run_module(module_name):
    """Python modülünü çalıştırır"""
    try:
        result = subprocess.run([sys.executable, "-m", module_name], check=True)
        print(f"✓ {module_name} başarıyla çalıştırıldı")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {module_name} çalıştırılırken hata: {e}")
        return False

if __name__ == "__main__":
    print("Veritabanı kurulumu başlatılıyor...\n")
    
    # Tabloyu oluştur
    print("Kimlik tablosu oluşturuluyor...")
    if not run_module("app.database"):
        sys.exit(1)
    
    print()
    
    # Örnek verileri ekle
    print("Örnek veriler ekleniyor...")
    if not run_script("scripts/seed_data.py"):
        sys.exit(1)
    
    print("\n✓ Kurulum tamamlandı!")

