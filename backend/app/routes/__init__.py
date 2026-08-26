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
from app.routes.recipe_routes import recipes_bp
from app.routes.report_routes import reports_bp
from app.routes.stock_movement_routes import stock_movements_bp
from app.routes.customer_routes import customers_bp
from app.routes.expense_routes import expenses_bp
from app.routes.purchase_routes import purchases_bp
from app.routes.supplier_routes import suppliers_bp
from app.routes.menu_routes import menu_bp
from app.routes.mobile_routes import mobile_bp
from app.routes.combo_routes import combos_bp
from app.routes.cafe_routes import cafe_bp
from app.routes.kot_routes import kots_bp
from app.routes.order_routes import orders_bp
from app.routes.table_routes import tables_bp
from app.routes.module_stub_routes import variants_bp
from app.routes.tenant_routes import tenants_bp
from app.routes.whatsapp_webhook_routes import whatsapp_webhook_bp
from app.routes.grocery_routes import grocery_bp
from app.routes.hardware_routes import hardware_bp
from app.routes.clothing_routes import clothing_bp
from app.routes.installation_routes import installations_bp
from app.routes.item_image_routes import item_images_bp
from app.routes.batch_routes import batches_bp
from app.routes.sales_return_routes import returns_bp
from app.routes.repair_routes import repairs_bp
from app.routes.quotation_routes import quotations_bp
from app.routes.challan_routes import challans_bp
from app.routes.warehouse_routes import stock_transfers_bp, warehouses_bp
from app.routes.serial_unit_routes import serial_units_bp
from app.routes.wastage_routes import wastage_bp
from app.routes.production_routes import productions_bp
from app.routes.bakery_routes import bakery_bp
from app.routes.custom_order_routes import custom_orders_bp
from app.routes.delivery_routes import deliveries_bp
from app.routes.price_list_routes import price_lists_bp
from app.routes.wholesale_routes import wholesale_bp
from app.routes.sales_order_routes import sales_orders_bp
from app.routes.purchase_order_routes import purchase_orders_bp
from app.routes.furniture_routes import furniture_bp
from app.routes.stationery_routes import stationery_bp
from app.routes.books_routes import books_bp
from app.routes.user_routes import users_bp
from app.routes.tour_package_routes import tour_packages_bp, travel_bp
from app.routes.travel_booking_routes import travel_bookings_bp
from app.routes.travel_agent_routes import commissions_bp, travel_agents_bp


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
    api_v1.register_blueprint(customers_bp)
    api_v1.register_blueprint(suppliers_bp)
    api_v1.register_blueprint(purchases_bp)
    api_v1.register_blueprint(expenses_bp)
    api_v1.register_blueprint(items_bp)
    api_v1.register_blueprint(bills_bp)
    api_v1.register_blueprint(reports_bp)
    api_v1.register_blueprint(audit_logs_bp)
    api_v1.register_blueprint(ai_bp)
    api_v1.register_blueprint(notifications_bp)
    api_v1.register_blueprint(whatsapp_webhook_bp)
    api_v1.register_blueprint(stock_movements_bp)
    api_v1.register_blueprint(menu_bp)
    api_v1.register_blueprint(combos_bp)
    api_v1.register_blueprint(cafe_bp)
    api_v1.register_blueprint(wastage_bp)
    api_v1.register_blueprint(productions_bp)
    api_v1.register_blueprint(bakery_bp)
    api_v1.register_blueprint(custom_orders_bp)
    api_v1.register_blueprint(deliveries_bp)
    api_v1.register_blueprint(furniture_bp)
    api_v1.register_blueprint(wholesale_bp)
    api_v1.register_blueprint(tour_packages_bp)
    api_v1.register_blueprint(travel_bp)
    api_v1.register_blueprint(travel_bookings_bp)
    api_v1.register_blueprint(travel_agents_bp)
    api_v1.register_blueprint(commissions_bp)
    api_v1.register_blueprint(price_lists_bp)
    api_v1.register_blueprint(sales_orders_bp)
    api_v1.register_blueprint(purchase_orders_bp)
    api_v1.register_blueprint(stationery_bp)
    api_v1.register_blueprint(books_bp)
    api_v1.register_blueprint(grocery_bp)
    api_v1.register_blueprint(hardware_bp)
    api_v1.register_blueprint(clothing_bp)
    api_v1.register_blueprint(mobile_bp)
    api_v1.register_blueprint(returns_bp)
    api_v1.register_blueprint(repairs_bp)
    api_v1.register_blueprint(quotations_bp)
    api_v1.register_blueprint(challans_bp)
    api_v1.register_blueprint(warehouses_bp)
    api_v1.register_blueprint(stock_transfers_bp)
    api_v1.register_blueprint(installations_bp)
    api_v1.register_blueprint(serial_units_bp)
    api_v1.register_blueprint(item_images_bp)
    api_v1.register_blueprint(batches_bp)
    api_v1.register_blueprint(orders_bp)
    api_v1.register_blueprint(kots_bp)
    api_v1.register_blueprint(recipes_bp)
    api_v1.register_blueprint(tables_bp)
    api_v1.register_blueprint(variants_bp)
    app.register_blueprint(api_v1)
