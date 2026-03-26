"""
Route kayıt modülü
"""
from app.routes.auth import auth_bp
from app.routes.health import health_bp
from app.routes.users import users_bp
from app.routes.timesheets import timesheets_bp
from app.routes.settings import settings_bp
from app.routes.timesheet_analysis import timesheet_analysis_bp

def register_routes(app):
    """Tüm route'ları uygulamaya kaydeder"""
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(timesheets_bp, url_prefix='/api')
    app.register_blueprint(settings_bp, url_prefix='/api')
    app.register_blueprint(timesheet_analysis_bp, url_prefix='/api')

