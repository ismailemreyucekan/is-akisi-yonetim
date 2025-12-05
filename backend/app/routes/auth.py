"""
Kimlik doğrulama route'ları
"""
from flask import Blueprint, request, jsonify
import bcrypt
from app.models import db, Identity
from app.logger import log_operation, log_error, log_success

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Kullanıcı veya admin girişi"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('user_type')
        
        log_operation("Login isteği", f"Email: {email}, Tip: {user_type}")
        
        if not email or not password or not user_type:
            log_error("Login başarısız - Eksik bilgi")
            return jsonify({
                'success': False,
                'message': 'E-posta, şifre ve kullanıcı tipi gereklidir'
            }), 400
        
        identity = Identity.query.filter_by(email=email, user_type=user_type).first()
        
        if not identity or not identity.is_active:
            log_error(f"Login başarısız - Kullanıcı bulunamadı veya aktif değil: {email}")
            return jsonify({
                'success': False,
                'message': 'E-posta veya şifre hatalı'
            }), 401
        
        if not bcrypt.checkpw(password.encode('utf-8'), identity.password_hash.encode('utf-8')):
            log_error(f"Login başarısız - Şifre hatalı: {email}")
            return jsonify({
                'success': False,
                'message': 'E-posta veya şifre hatalı'
            }), 401
        
        log_success(f"Login başarılı - {identity.full_name} ({email})")
        return jsonify({
            'success': True,
            'message': 'Giriş başarılı',
            'user': {
                'id': identity.id,
                'email': identity.email,
                'full_name': identity.full_name,
                'user_type': identity.user_type
            }
        }), 200
        
    except Exception as e:
        log_error(f"Login hatası: {e}")
        return jsonify({
            'success': False,
            'message': 'Bir hata oluştu'
        }), 500

