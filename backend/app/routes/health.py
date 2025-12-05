"""
Sağlık kontrolü route'ları
"""
from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """API sağlık kontrolü"""
    return jsonify({'status': 'ok'}), 200

