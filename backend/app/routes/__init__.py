"""API blueprint registration."""

from flask import Blueprint

from app.routes.ai_routes import ai_bp
from app.routes.audit_log_routes import audit_logs_bp
from app.routes.auth_routes import auth_bp
from app.routes.bill_routes import bills_bp
from app.routes.category_routes import categories_bp
from app.routes.health_routes import health_bp
from app.routes.item_routes import items_bp
from app.routes.master_routes import master_bp
from app.routes.notification_routes import notifications_bp
from app.routes.profile_routes import profile_bp
from app.routes.public_routes import public_bp
from app.routes.report_routes import reports_bp
from app.routes.stock_movement_routes import stock_movements_bp
from app.routes.tenant_routes import tenants_bp
from app.routes.whatsapp_webhook_routes import whatsapp_webhook_bp
from app.routes.user_routes import users_bp


def register_blueprints(app):
    api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")
    api_v1.register_blueprint(health_bp)
    api_v1.register_blueprint(auth_bp)
    api_v1.register_blueprint(public_bp)
    api_v1.register_blueprint(master_bp)
    api_v1.register_blueprint(profile_bp)
    api_v1.register_blueprint(users_bp)
    api_v1.register_blueprint(tenants_bp)
    api_v1.register_blueprint(categories_bp)
    api_v1.register_blueprint(items_bp)
    api_v1.register_blueprint(bills_bp)
    api_v1.register_blueprint(reports_bp)
    api_v1.register_blueprint(audit_logs_bp)
    api_v1.register_blueprint(ai_bp)
    api_v1.register_blueprint(notifications_bp)
    api_v1.register_blueprint(whatsapp_webhook_bp)
    api_v1.register_blueprint(stock_movements_bp)
    app.register_blueprint(api_v1)
