
import sys
import os
import subprocess

def run_migrations():
    """Alembic migration'larını çalıştırır"""
    try:
        # Backend dizinine geç
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(backend_dir)
        
        print("Alembic migration'ları çalıştırılıyor...")
        result = subprocess.run(
            ["python", "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Migration'lar başarıyla uygulandı!")
            print(result.stdout)
        else:
            print(f"Hata: {result.stderr}")
            return False
            
        return True
        
    except Exception as e:
        print(f"Hata: {e}")
        return False

if __name__ == "__main__":
    run_migrations()

