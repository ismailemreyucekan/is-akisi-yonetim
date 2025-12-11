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

if __name__ == "__main__":
    print("Veritabanı kurulumu başlatılıyor...\n")
    
    # Önce yeni migration'ları oluştur (model değişiklikleri varsa)
    print("Model değişiklikleri kontrol ediliyor ve migration oluşturuluyor...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", "auto_migration"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            if "No changes" not in result.stdout and "Can't locate revision" not in result.stderr:
                print("✓ Yeni migration oluşturuldu")
            elif "Can't locate revision" in result.stderr:
                print("⚠ Migration geçmişi hatası tespit edildi. Lütfen scripts/fix_alembic_version.py çalıştırın.")
            else:
                print("✓ Model değişikliği yok, migration gerekmiyor")
        else:
            if "Can't locate revision" in result.stderr:
                print("⚠ Migration geçmişi hatası. Lütfen scripts/fix_alembic_version.py çalıştırın.")
            else:
                print(f"⚠ Migration oluşturma uyarısı: {result.stderr}")
    except Exception as e:
        print(f"⚠ Migration oluşturma hatası (devam ediliyor): {e}")
    
    print()
    
    # Alembic migration'larını uygula
    print("Alembic migration'ları uygulanıyor...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            check=True,
            cwd=project_root
        )
        print("✓ Migration'lar başarıyla uygulandı")
    except subprocess.CalledProcessError as e:
        print(f"✗ Migration uygulanırken hata: {e}")
        sys.exit(1)
    
    print()
    
    # Örnek verileri ekle
    print("Örnek veriler ekleniyor...")
    if not run_script("scripts/seed_data.py"):
        sys.exit(1)
    
    print("\n✓ Kurulum tamamlandı!")

