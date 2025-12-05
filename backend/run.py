"""
Uygulama entry point
"""
from app import create_app
from app.logger import log_success, log_operation

app = create_app()

if __name__ == '__main__':
    log_operation("Backend sunucusu başlatılıyor", "Port: 5000")
    log_success("Backend sunucusu hazır")
    app.run(debug=True, port=5000)

