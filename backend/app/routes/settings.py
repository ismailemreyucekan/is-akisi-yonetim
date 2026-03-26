"""
Timesheet ayarları route'ları
"""
from flask import Blueprint, request, jsonify
from app.models import db, TimesheetSetting
from app.logger import log_operation, log_error, log_success

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/timesheet-settings', methods=['GET'])
def list_settings():
    """Timesheet ayarlarını listeler (opsiyonel filtreler: setting_type, is_active)"""
    try:
        setting_type = request.args.get('setting_type')
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        try:
            query = TimesheetSetting.query
        except Exception as db_error:
            log_error(f"Veritabanı sorgu hatası: {db_error}")
            try:
                db.create_all()
                log_success("Timesheet settings tablosu oluşturuldu")
                query = TimesheetSetting.query
            except Exception as create_error:
                log_error(f"Tablo oluşturma hatası: {create_error}")
                return jsonify({
                    'success': True,
                    'settings': [],
                    'total': 0,
                    'message': 'Tablo henüz oluşturulmadı'
                }), 200
        
        if setting_type:
            query = query.filter(TimesheetSetting.setting_type == setting_type)
        
        if not include_inactive:
            query = query.filter(TimesheetSetting.is_active == True)
        
        settings = query.order_by(
            TimesheetSetting.setting_type,
            TimesheetSetting.display_order,
            TimesheetSetting.value
        ).all()
        
        log_success(f"Timesheet ayarları listelendi: {len(settings)} kayıt")
        return jsonify({
            'success': True,
            'settings': [s.to_dict() for s in settings],
            'total': len(settings)
        }), 200

    except Exception as e:
        log_error(f"Timesheet ayarları listeleme hatası: {e}")
        return jsonify({
            'success': True,
            'settings': [],
            'total': 0,
            'message': f'Ayarlar listelenirken bir hata oluştu: {str(e)}'
        }), 200


@settings_bp.route('/timesheet-settings', methods=['POST'])
def create_setting():
    """Yeni timesheet ayarı oluşturur"""
    try:
        data = request.get_json() or {}
        setting_type = data.get('setting_type')
        value = data.get('value')
        is_active = data.get('is_active', True)
        display_order = data.get('display_order', 0)

        if not setting_type or not value:
            return jsonify({
                'success': False,
                'message': 'setting_type ve value zorunludur'
            }), 400

        # Geçerli setting_type kontrolü
        valid_types = ['project', 'activity_type', 'work_mode']
        if setting_type not in valid_types:
            return jsonify({
                'success': False,
                'message': f'setting_type şunlardan biri olmalıdır: {", ".join(valid_types)}'
            }), 400

        # Aynı değerin aynı tipte olup olmadığını kontrol et
        try:
            existing = TimesheetSetting.query.filter_by(
                setting_type=setting_type,
                value=value
            ).first()
        except Exception as db_error:
            log_error(f"Veritabanı sorgu hatası: {db_error}")
            try:
                db.create_all()
                log_success("Timesheet settings tablosu oluşturuldu")
                existing = None
            except Exception as create_error:
                log_error(f"Tablo oluşturma hatası: {create_error}")
                return jsonify({
                    'success': False,
                    'message': f'Veritabanı hatası: {str(create_error)}. Lütfen veritabanı tablosunu oluşturun.'
                }), 500
        
        if existing:
            return jsonify({
                'success': False,
                'message': 'Bu ayar zaten mevcut'
            }), 400

        try:
            setting = TimesheetSetting(
                setting_type=setting_type,
                value=value,
                is_active=is_active,
                display_order=display_order
            )
            db.session.add(setting)
            db.session.commit()

            log_success(f"Timesheet ayarı oluşturuldu: {setting_type} - {value}")
            return jsonify({'success': True, 'setting': setting.to_dict()}), 201
        except Exception as commit_error:
            db.session.rollback()
            log_error(f"Commit hatası: {commit_error}")
            try:
                db.create_all()
                setting = TimesheetSetting(
                    setting_type=setting_type,
                    value=value,
                    is_active=is_active,
                    display_order=display_order
                )
                db.session.add(setting)
                db.session.commit()
                log_success(f"Tablo oluşturuldu ve timesheet ayarı eklendi: {setting_type} - {value}")
                return jsonify({'success': True, 'setting': setting.to_dict()}), 201
            except Exception as retry_error:
                log_error(f"Retry hatası: {retry_error}")
                raise

    except Exception as e:
        db.session.rollback()
        log_error(f"Timesheet ayarı oluşturma hatası: {e}")
        return jsonify({
            'success': False,
            'message': f'Ayar oluşturulurken bir hata oluştu: {str(e)}'
        }), 500


@settings_bp.route('/timesheet-settings/<int:setting_id>', methods=['PUT'])
def update_setting(setting_id):
    """Timesheet ayarını günceller"""
    try:
        data = request.get_json() or {}
        setting = TimesheetSetting.query.get_or_404(setting_id)

        if 'value' in data:
            # Aynı değerin başka bir kayıtta olup olmadığını kontrol et
            existing = TimesheetSetting.query.filter_by(
                setting_type=setting.setting_type,
                value=data['value']
            ).filter(TimesheetSetting.id != setting_id).first()
            
            if existing:
                return jsonify({
                    'success': False,
                    'message': 'Bu değer zaten mevcut'
                }), 400
            
            setting.value = data['value']
        
        if 'is_active' in data:
            setting.is_active = data['is_active']
        
        if 'display_order' in data:
            setting.display_order = data['display_order']

        db.session.commit()
        log_success(f"Timesheet ayarı güncellendi: ID {setting_id}")
        return jsonify({'success': True, 'setting': setting.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        log_error(f"Timesheet ayarı güncelleme hatası: {e}")
        return jsonify({
            'success': False,
            'message': 'Ayar güncellenirken bir hata oluştu'
        }), 500


@settings_bp.route('/timesheet-settings/<int:setting_id>', methods=['DELETE'])
def delete_setting(setting_id):
    """Timesheet ayarını siler"""
    try:
        setting = TimesheetSetting.query.get_or_404(setting_id)
        db.session.delete(setting)
        db.session.commit()
        log_success(f"Timesheet ayarı silindi: ID {setting_id}")
        return jsonify({'success': True, 'message': 'Silindi'}), 200
    except Exception as e:
        db.session.rollback()
        log_error(f"Timesheet ayarı silme hatası: {e}")
        return jsonify({
            'success': False,
            'message': 'Ayar silinirken bir hata oluştu'
        }), 500


@settings_bp.route('/timesheet-settings/grouped', methods=['GET'])
def get_grouped_settings():
    """Timesheet ayarlarını tipine göre gruplandırılmış olarak döner"""
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        query = TimesheetSetting.query
        if not include_inactive:
            query = query.filter(TimesheetSetting.is_active == True)
        
        settings = query.order_by(
            TimesheetSetting.setting_type,
            TimesheetSetting.display_order,
            TimesheetSetting.value
        ).all()
        
        # Gruplandır
        grouped = {
            'projects': [],
            'activity_types': [],
            'work_modes': []
        }
        
        for s in settings:
            if s.setting_type == 'project':
                grouped['projects'].append(s.value)
            elif s.setting_type == 'activity_type':
                grouped['activity_types'].append(s.value)
            elif s.setting_type == 'work_mode':
                grouped['work_modes'].append(s.value)
        
        log_success("Gruplandırılmış timesheet ayarları döndürüldü")
        return jsonify({
            'success': True,
            'settings': grouped
        }), 200

    except Exception as e:
        log_error(f"Gruplandırılmış ayarlar hatası: {e}")
        return jsonify({
            'success': False,
            'message': 'Ayarlar getirilirken bir hata oluştu'
        }), 500
