-- =============================================================================
-- Business Billing Software — MySQL Schema (Multi-Tenant)
-- Database : hotel_billing  (legacy DB name; product is multi-business)
-- Charset  : utf8mb4 / utf8mb4_unicode_ci
-- Tables   : 53 application tables (aligned with SQLAlchemy models / Alembic)
-- Alembic head: 20260825_audit_db_hardening (after BIZ-29 serial units)
--
-- GREENFIELD / EMPTY DB ONLY. DROP + recreate. Never run on production data.
-- Upgrades: flask db upgrade  OR  scripts/apply_pending_schema.py (hosted path).
-- =============================================================================

USE hotel_billing;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Drop (safe re-run for local/dev)
DROP TABLE IF EXISTS serial_units;
DROP TABLE IF EXISTS sales_return_items;
DROP TABLE IF EXISTS order_item_addons;
DROP TABLE IF EXISTS wastage_entries;
DROP TABLE IF EXISTS recipe_ingredients;
DROP TABLE IF EXISTS kot_items;
DROP TABLE IF EXISTS item_images;
DROP TABLE IF EXISTS item_addons;
DROP TABLE IF EXISTS bill_items;
DROP TABLE IF EXISTS stock_movements;
DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS purchase_items;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS item_variants;
DROP TABLE IF EXISTS item_price_tiers;
DROP TABLE IF EXISTS item_batches;
DROP TABLE IF EXISTS item_addon_groups;
DROP TABLE IF EXISTS combo_items;
DROP TABLE IF EXISTS subscription_notices;
DROP TABLE IF EXISTS sales_returns;
DROP TABLE IF EXISTS purchases;
DROP TABLE IF EXISTS party_ledger_entries;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS kots;
DROP TABLE IF EXISTS expenses;
DROP TABLE IF EXISTS email_verification_tokens;
DROP TABLE IF EXISTS combos;
DROP TABLE IF EXISTS bill_deliveries;
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS password_reset_tokens;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS tenant_whatsapp_configs;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS subscriptions;
DROP TABLE IF EXISTS sales_return_counters;
DROP TABLE IF EXISTS registration_requests;
DROP TABLE IF EXISTS purchase_number_counters;
DROP TABLE IF EXISTS platform_audit_logs;
DROP TABLE IF EXISTS order_number_counters;
DROP TABLE IF EXISTS kot_number_counters;
DROP TABLE IF EXISTS dining_tables;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS bill_number_counters;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS bills;
DROP TABLE IF EXISTS tenants;
DROP TABLE IF EXISTS subscription_plans;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS platform_settings;
DROP TABLE IF EXISTS platform_notifications;
DROP TABLE IF EXISTS master_admins;

SET FOREIGN_KEY_CHECKS = 0;

-- tenants

CREATE TABLE tenants (
	id VARCHAR(36) NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	business_name VARCHAR(200) NOT NULL, 
	business_type VARCHAR(40) NOT NULL, 
	address VARCHAR(255), 
	city VARCHAR(100), 
	state VARCHAR(100), 
	pincode VARCHAR(20), 
	phone VARCHAR(30), 
	email VARCHAR(255), 
	gst_number VARCHAR(30), 
	fssai_number VARCHAR(50), 
	bill_number_prefix VARCHAR(20), 
	default_gst_percent DECIMAL(5, 2), 
	status VARCHAR(20) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id),
	CONSTRAINT chk_tenants_status CHECK (status IN ('ACTIVE', 'SUSPENDED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- roles

CREATE TABLE roles (
	id VARCHAR(36) NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	description VARCHAR(255), 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	UNIQUE (name),
	CONSTRAINT chk_roles_name CHECK (name IN ('OWNER', 'BILLING_USER', 'MANAGER'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- master_admins

CREATE TABLE master_admins (
	id VARCHAR(36) NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	is_active TINYINT(1) NOT NULL, 
	token_version INTEGER NOT NULL, 
	last_login_at DATETIME, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- platform_settings

CREATE TABLE platform_settings (
	id VARCHAR(36) NOT NULL, 
	trial_enabled TINYINT(1) NOT NULL, 
	trial_days INTEGER NOT NULL, 
	expiry_warning_days INTEGER NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- subscription_plans

CREATE TABLE subscription_plans (
	id VARCHAR(36) NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	description TEXT, 
	price DECIMAL(12, 2) NOT NULL, 
	currency VARCHAR(8) NOT NULL, 
	billing_cycle VARCHAR(20) NOT NULL, 
	trial_eligible TINYINT(1) NOT NULL, 
	is_public TINYINT(1) NOT NULL, 
	is_active TINYINT(1) NOT NULL, 
	display_order INTEGER NOT NULL, 
	features JSON, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- platform_notifications

CREATE TABLE platform_notifications (
	id VARCHAR(36) NOT NULL, 
	type VARCHAR(50) NOT NULL, 
	title VARCHAR(160) NOT NULL, 
	message TEXT NOT NULL, 
	entity_type VARCHAR(50), 
	entity_id VARCHAR(36), 
	is_read TINYINT(1) NOT NULL, 
	read_at DATETIME, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- users

CREATE TABLE users (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	role_id VARCHAR(36) NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	is_active TINYINT(1) NOT NULL, 
	email_verified TINYINT(1) NOT NULL, 
	email_verified_at DATETIME, 
	password_changed_at DATETIME, 
	pending_email VARCHAR(255), 
	token_version INTEGER NOT NULL, 
	last_login_at DATETIME, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_users_tenant_email UNIQUE (tenant_id, email), 
	CONSTRAINT uq_users_email UNIQUE (email), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(role_id) REFERENCES roles (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_users_tenant_id ON users (tenant_id);

-- categories

CREATE TABLE categories (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	parent_id VARCHAR(36), 
	parent_key VARCHAR(36) GENERATED ALWAYS AS (IFNULL(parent_id, '')) VIRTUAL NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	description TEXT, 
	is_active TINYINT(1) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_categories_tenant_parent_key_name UNIQUE (tenant_id, parent_key, name), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(parent_id) REFERENCES categories (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_categories_tenant_id ON categories (tenant_id);

-- customers

CREATE TABLE customers (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	phone_country_code VARCHAR(8), 
	phone_national VARCHAR(20), 
	phone_e164 VARCHAR(20), 
	email VARCHAR(255), 
	credit_limit DECIMAL(12, 2), 
	balance DECIMAL(12, 2) NOT NULL, 
	notes TEXT, 
	is_active TINYINT(1) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_customers_tenant_phone_e164 UNIQUE (tenant_id, phone_e164), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_customers_tenant_id ON customers (tenant_id);

-- suppliers

CREATE TABLE suppliers (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	phone_country_code VARCHAR(8), 
	phone_national VARCHAR(20), 
	phone_e164 VARCHAR(20), 
	gstin VARCHAR(15), 
	email VARCHAR(255), 
	address TEXT, 
	notes TEXT, 
	is_active TINYINT(1) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_suppliers_tenant_phone_e164 UNIQUE (tenant_id, phone_e164), 
	CONSTRAINT uq_suppliers_tenant_gstin UNIQUE (tenant_id, gstin), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_suppliers_tenant_id ON suppliers (tenant_id);

-- items

CREATE TABLE items (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	category_id VARCHAR(36) NOT NULL, 
	created_by VARCHAR(36), 
	name VARCHAR(200) NOT NULL, 
	sku VARCHAR(64), 
	barcode VARCHAR(64), 
	uom VARCHAR(16) NOT NULL, 
	description TEXT, 
	price DECIMAL(12, 2) NOT NULL, 
	cost_price DECIMAL(12, 2), 
	gst_percentage DECIMAL(5, 2) NOT NULL, 
	stock_quantity DECIMAL(12, 3), 
	minimum_stock_level DECIMAL(12, 3), 
	is_active TINYINT(1) NOT NULL, 
	is_menu TINYINT(1) NOT NULL, 
	is_veg BOOL, 
	tracks_batches TINYINT(1) NOT NULL, 
	block_expired_batches TINYINT(1) NOT NULL, 
	tracks_variants TINYINT(1) NOT NULL, 
	tracks_serial TINYINT(1) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_items_tenant_name UNIQUE (tenant_id, name), 
	CONSTRAINT uq_items_tenant_sku UNIQUE (tenant_id, sku), 
	CONSTRAINT uq_items_tenant_barcode UNIQUE (tenant_id, barcode), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(category_id) REFERENCES categories (id) ON DELETE RESTRICT, 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE SET NULL,
	CONSTRAINT chk_items_stock CHECK (stock_quantity IS NULL OR stock_quantity >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_items_created_by ON items (created_by);

CREATE INDEX ix_items_barcode ON items (barcode);

CREATE INDEX ix_items_tenant_id ON items (tenant_id);

-- bills

CREATE TABLE bills (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	bill_number VARCHAR(50) NOT NULL, 
	bill_sequence INTEGER NOT NULL, 
	table_number VARCHAR(30), 
	customer_name VARCHAR(120), 
	customer_phone_country_code VARCHAR(8), 
	customer_phone_national VARCHAR(20), 
	customer_phone_e164 VARCHAR(20), 
	customer_email VARCHAR(255), 
	customer_id VARCHAR(36), 
	subtotal DECIMAL(12, 2) NOT NULL, 
	discount DECIMAL(12, 2) NOT NULL, 
	taxable_amount DECIMAL(12, 2) NOT NULL, 
	cgst_amount DECIMAL(12, 2) NOT NULL, 
	sgst_amount DECIMAL(12, 2) NOT NULL, 
	gst_amount DECIMAL(12, 2) NOT NULL, 
	grand_total DECIMAL(12, 2) NOT NULL, 
	round_off DECIMAL(12, 2) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	payment_method VARCHAR(20) NOT NULL, 
	created_by VARCHAR(36) NOT NULL, 
	cancelled_by VARCHAR(36), 
	cancelled_at DATETIME, 
	cancellation_reason TEXT, 
	printed_count INTEGER NOT NULL, 
	order_id VARCHAR(36), 
	service_charge DECIMAL(12, 2) NOT NULL, 
	split_group_id VARCHAR(36), 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_bills_tenant_bill_number UNIQUE (tenant_id, bill_number), 
	CONSTRAINT uq_bills_tenant_bill_sequence UNIQUE (tenant_id, bill_sequence), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(customer_id) REFERENCES customers (id) ON DELETE SET NULL, 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE RESTRICT, 
	FOREIGN KEY(cancelled_by) REFERENCES users (id) ON DELETE RESTRICT, 
	FOREIGN KEY(order_id) REFERENCES orders (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_bills_customer_id ON bills (customer_id);

CREATE INDEX ix_bills_tenant_id ON bills (tenant_id);

CREATE INDEX ix_bills_split_group_id ON bills (split_group_id);

CREATE INDEX ix_bills_order_id ON bills (order_id);

-- orders

CREATE TABLE orders (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	order_number VARCHAR(50) NOT NULL, 
	order_sequence INTEGER NOT NULL, 
	channel VARCHAR(16) NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	dining_table_id VARCHAR(36), 
	customer_id VARCHAR(36), 
	customer_name VARCHAR(120), 
	customer_phone_country_code VARCHAR(8), 
	customer_phone_national VARCHAR(20), 
	customer_phone_e164 VARCHAR(20), 
	delivery_address TEXT, 
	notes TEXT, 
	subtotal DECIMAL(12, 2) NOT NULL, 
	gst_amount DECIMAL(12, 2) NOT NULL, 
	grand_total DECIMAL(12, 2) NOT NULL, 
	bill_id VARCHAR(36), 
	created_by VARCHAR(36) NOT NULL, 
	cancelled_by VARCHAR(36), 
	cancelled_at DATETIME, 
	cancellation_reason TEXT, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_orders_tenant_number UNIQUE (tenant_id, order_number), 
	CONSTRAINT uq_orders_tenant_sequence UNIQUE (tenant_id, order_sequence), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(dining_table_id) REFERENCES dining_tables (id) ON DELETE SET NULL, 
	FOREIGN KEY(customer_id) REFERENCES customers (id) ON DELETE SET NULL, 
	FOREIGN KEY(bill_id) REFERENCES bills (id) ON DELETE SET NULL, 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE RESTRICT, 
	FOREIGN KEY(cancelled_by) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_orders_customer_id ON orders (customer_id);

CREATE INDEX ix_orders_tenant_id ON orders (tenant_id);

CREATE INDEX ix_orders_dining_table_id ON orders (dining_table_id);

CREATE INDEX ix_orders_bill_id ON orders (bill_id);

-- bill_number_counters

CREATE TABLE bill_number_counters (
	tenant_id VARCHAR(36) NOT NULL, 
	next_value INTEGER NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (tenant_id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- order_number_counters

CREATE TABLE order_number_counters (
	tenant_id VARCHAR(36) NOT NULL, 
	next_value INTEGER NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (tenant_id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- kot_number_counters

CREATE TABLE kot_number_counters (
	tenant_id VARCHAR(36) NOT NULL, 
	next_value INTEGER NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (tenant_id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- purchase_number_counters

CREATE TABLE purchase_number_counters (
	tenant_id VARCHAR(36) NOT NULL, 
	next_value INTEGER NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (tenant_id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- sales_return_counters

CREATE TABLE sales_return_counters (
	tenant_id VARCHAR(36) NOT NULL, 
	next_value INTEGER NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (tenant_id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- dining_tables

CREATE TABLE dining_tables (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	code VARCHAR(32) NOT NULL, 
	section VARCHAR(64), 
	capacity INTEGER, 
	status VARCHAR(16) NOT NULL, 
	merged_into_id VARCHAR(36), 
	is_active TINYINT(1) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_dining_tables_tenant_code UNIQUE (tenant_id, code), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(merged_into_id) REFERENCES dining_tables (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_dining_tables_merged_into_id ON dining_tables (merged_into_id);

CREATE INDEX ix_dining_tables_tenant_id ON dining_tables (tenant_id);

-- registration_requests

CREATE TABLE registration_requests (
	id VARCHAR(36) NOT NULL, 
	business_name VARCHAR(200) NOT NULL, 
	business_type VARCHAR(40) NOT NULL, 
	owner_name VARCHAR(120) NOT NULL, 
	owner_email VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	mobile VARCHAR(30), 
	address VARCHAR(255), 
	city VARCHAR(100), 
	state VARCHAR(100), 
	country VARCHAR(80), 
	pincode VARCHAR(20), 
	gst_number VARCHAR(30), 
	fssai_number VARCHAR(50), 
	status VARCHAR(20) NOT NULL, 
	requested_at DATETIME NOT NULL, 
	approved_at DATETIME, 
	rejected_at DATETIME, 
	approved_by VARCHAR(36), 
	rejected_by VARCHAR(36), 
	rejection_reason TEXT, 
	tenant_id VARCHAR(36), 
	terms_accepted_at DATETIME, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	FOREIGN KEY(approved_by) REFERENCES master_admins (id) ON DELETE SET NULL, 
	FOREIGN KEY(rejected_by) REFERENCES master_admins (id) ON DELETE SET NULL, 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_registration_requests_owner_email ON registration_requests (owner_email);

-- subscriptions

CREATE TABLE subscriptions (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	plan_id VARCHAR(36), 
	status VARCHAR(20) NOT NULL, 
	starts_at DATETIME, 
	ends_at DATETIME, 
	trial_starts_at DATETIME, 
	trial_ends_at DATETIME, 
	price_at_purchase DECIMAL(12, 2), 
	payment_status VARCHAR(30), 
	payment_provider VARCHAR(40), 
	payment_reference VARCHAR(120), 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(plan_id) REFERENCES subscription_plans (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_subscriptions_plan_id ON subscriptions (plan_id);

CREATE INDEX ix_subscriptions_tenant_id ON subscriptions (tenant_id);

-- tenant_whatsapp_configs

CREATE TABLE tenant_whatsapp_configs (
	tenant_id VARCHAR(36) NOT NULL, 
	phone_number_id VARCHAR(64), 
	waba_id VARCHAR(64), 
	display_phone_e164 VARCHAR(20), 
	access_token_encrypted TEXT, 
	template_name VARCHAR(120), 
	template_language VARCHAR(20) NOT NULL, 
	is_enabled TINYINT(1) NOT NULL, 
	connected_at DATETIME, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (tenant_id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- password_reset_tokens

CREATE TABLE password_reset_tokens (
	id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	token_hash VARCHAR(64) NOT NULL, 
	expires_at DATETIME NOT NULL, 
	used_at DATETIME, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_password_reset_tokens_user_id ON password_reset_tokens (user_id);

CREATE UNIQUE INDEX ix_password_reset_tokens_token_hash ON password_reset_tokens (token_hash);

-- email_verification_tokens

CREATE TABLE email_verification_tokens (
	id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36) NOT NULL, 
	token_hash VARCHAR(64) NOT NULL, 
	purpose VARCHAR(40) NOT NULL, 
	new_email VARCHAR(255), 
	expires_at DATETIME NOT NULL, 
	verified_at DATETIME, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_email_verification_tokens_user_id ON email_verification_tokens (user_id);

CREATE UNIQUE INDEX ix_email_verification_tokens_token_hash ON email_verification_tokens (token_hash);

-- audit_logs

CREATE TABLE audit_logs (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36), 
	user_name VARCHAR(120), 
	action VARCHAR(50) NOT NULL, 
	entity_type VARCHAR(50) NOT NULL, 
	entity_id VARCHAR(36), 
	old_data JSON, 
	new_data JSON, 
	ip_address VARCHAR(45), 
	user_agent VARCHAR(255), 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_audit_logs_tenant_id ON audit_logs (tenant_id);

-- notifications

CREATE TABLE notifications (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	user_id VARCHAR(36), 
	type VARCHAR(50) NOT NULL, 
	title VARCHAR(160) NOT NULL, 
	message TEXT NOT NULL, 
	entity_type VARCHAR(50), 
	entity_id VARCHAR(36), 
	is_read TINYINT(1) NOT NULL, 
	read_at DATETIME, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_notifications_tenant_id ON notifications (tenant_id);

CREATE INDEX ix_notifications_user_id ON notifications (user_id);

-- stock_movements

CREATE TABLE stock_movements (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	item_id VARCHAR(36) NOT NULL, 
	delta DECIMAL(12, 3) NOT NULL, 
	quantity_after DECIMAL(12, 3) NOT NULL, 
	source VARCHAR(20) NOT NULL, 
	reason TEXT, 
	reference_type VARCHAR(20), 
	reference_id VARCHAR(36), 
	created_by VARCHAR(36), 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(item_id) REFERENCES items (id) ON DELETE RESTRICT, 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_stock_movements_item_id ON stock_movements (item_id);

CREATE INDEX ix_stock_movements_tenant_id ON stock_movements (tenant_id);

-- bill_deliveries

CREATE TABLE bill_deliveries (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	bill_id VARCHAR(36) NOT NULL, 
	delivery_method VARCHAR(20) NOT NULL, 
	recipient_phone_e164 VARCHAR(20), 
	recipient_phone_masked VARCHAR(32), 
	recipient_email VARCHAR(255), 
	recipient_email_masked VARCHAR(64), 
	status VARCHAR(20) NOT NULL, 
	provider_message_id VARCHAR(120), 
	error_message TEXT, 
	attempted_by VARCHAR(36), 
	sent_at DATETIME, 
	delivered_at DATETIME, 
	read_at DATETIME, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(bill_id) REFERENCES bills (id) ON DELETE RESTRICT, 
	FOREIGN KEY(attempted_by) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_bill_deliveries_provider_message_id ON bill_deliveries (provider_message_id);

CREATE INDEX ix_bill_deliveries_bill_id ON bill_deliveries (bill_id);

CREATE INDEX ix_bill_deliveries_tenant_id ON bill_deliveries (tenant_id);

-- expenses

CREATE TABLE expenses (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	category VARCHAR(80), 
	amount DECIMAL(12, 2) NOT NULL, 
	expense_date DATE NOT NULL, 
	notes TEXT, 
	created_by VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_expenses_expense_date ON expenses (expense_date);

CREATE INDEX ix_expenses_tenant_id ON expenses (tenant_id);

-- party_ledger_entries

CREATE TABLE party_ledger_entries (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	party_type VARCHAR(20) NOT NULL, 
	party_id VARCHAR(36) NOT NULL, 
	entry_type VARCHAR(20) NOT NULL, 
	amount DECIMAL(12, 2) NOT NULL, 
	balance_after DECIMAL(12, 2) NOT NULL, 
	reference_type VARCHAR(20), 
	reference_id VARCHAR(36), 
	notes TEXT, 
	created_by VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_party_ledger_ref_entry UNIQUE (tenant_id, reference_type, reference_id, entry_type), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_party_ledger_entries_party_type ON party_ledger_entries (party_type);

CREATE INDEX ix_party_ledger_entries_party_id ON party_ledger_entries (party_id);

CREATE INDEX ix_party_ledger_entries_tenant_id ON party_ledger_entries (tenant_id);

-- purchases

CREATE TABLE purchases (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	purchase_number VARCHAR(50) NOT NULL, 
	purchase_sequence INTEGER NOT NULL, 
	supplier_id VARCHAR(36), 
	supplier_name VARCHAR(120), 
	invoice_number VARCHAR(60), 
	notes TEXT, 
	total_amount DECIMAL(12, 2) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	created_by VARCHAR(36) NOT NULL, 
	cancelled_by VARCHAR(36), 
	cancelled_at DATETIME, 
	cancellation_reason TEXT, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_purchases_tenant_number UNIQUE (tenant_id, purchase_number), 
	CONSTRAINT uq_purchases_tenant_sequence UNIQUE (tenant_id, purchase_sequence), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id) ON DELETE SET NULL, 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE RESTRICT, 
	FOREIGN KEY(cancelled_by) REFERENCES users (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_purchases_supplier_id ON purchases (supplier_id);

CREATE INDEX ix_purchases_tenant_id ON purchases (tenant_id);

-- purchase_items

CREATE TABLE purchase_items (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	purchase_id VARCHAR(36) NOT NULL, 
	item_id VARCHAR(36) NOT NULL, 
	item_name VARCHAR(200) NOT NULL, 
	quantity DECIMAL(10, 3) NOT NULL, 
	unit_cost DECIMAL(12, 2) NOT NULL, 
	line_total DECIMAL(12, 2) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(purchase_id) REFERENCES purchases (id) ON DELETE RESTRICT, 
	FOREIGN KEY(item_id) REFERENCES items (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_purchase_items_tenant_id ON purchase_items (tenant_id);

CREATE INDEX ix_purchase_items_purchase_id ON purchase_items (purchase_id);

CREATE INDEX ix_purchase_items_item_id ON purchase_items (item_id);

-- item_price_tiers

CREATE TABLE item_price_tiers (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	item_id VARCHAR(36) NOT NULL, 
	min_quantity DECIMAL(12, 3) NOT NULL, 
	unit_price DECIMAL(12, 2) NOT NULL, 
	is_active TINYINT(1) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_item_price_tiers_tenant_item_min_qty UNIQUE (tenant_id, item_id, min_quantity), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(item_id) REFERENCES items (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_item_price_tiers_item_id ON item_price_tiers (item_id);

CREATE INDEX ix_item_price_tiers_tenant_id ON item_price_tiers (tenant_id);

-- item_batches

CREATE TABLE item_batches (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	item_id VARCHAR(36) NOT NULL, 
	batch_code VARCHAR(64), 
	expiry_date DATE, 
	quantity DECIMAL(12, 3) NOT NULL, 
	is_active TINYINT(1) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_item_batches_tenant_item_code UNIQUE (tenant_id, item_id, batch_code), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(item_id) REFERENCES items (id) ON DELETE CASCADE,
	CONSTRAINT chk_item_batches_qty CHECK (quantity >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_item_batches_expiry_date ON item_batches (expiry_date);

CREATE INDEX ix_item_batches_item_id ON item_batches (item_id);

CREATE INDEX ix_item_batches_tenant_id ON item_batches (tenant_id);

-- item_variants

CREATE TABLE item_variants (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	item_id VARCHAR(36) NOT NULL, 
	size VARCHAR(32) NOT NULL, 
	color VARCHAR(64) NOT NULL, 
	brand VARCHAR(80), 
	sku VARCHAR(64), 
	barcode VARCHAR(64), 
	stock_quantity DECIMAL(12, 3) NOT NULL, 
	is_active TINYINT(1) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_item_variants_tenant_item_size_color UNIQUE (tenant_id, item_id, size, color), 
	CONSTRAINT uq_item_variants_tenant_sku UNIQUE (tenant_id, sku), 
	CONSTRAINT uq_item_variants_tenant_barcode UNIQUE (tenant_id, barcode), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(item_id) REFERENCES items (id) ON DELETE CASCADE,
	CONSTRAINT chk_item_variants_stock CHECK (stock_quantity >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_item_variants_item_id ON item_variants (item_id);

CREATE INDEX ix_item_variants_barcode ON item_variants (barcode);

CREATE INDEX ix_item_variants_tenant_id ON item_variants (tenant_id);

-- item_images

CREATE TABLE item_images (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	item_id VARCHAR(36) NOT NULL, 
	variant_id VARCHAR(36), 
	image_url VARCHAR(500) NOT NULL, 
	storage_key VARCHAR(80), 
	alt_text VARCHAR(120), 
	sort_order INTEGER NOT NULL, 
	is_primary TINYINT(1) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(item_id) REFERENCES items (id) ON DELETE CASCADE, 
	FOREIGN KEY(variant_id) REFERENCES item_variants (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_item_images_variant_id ON item_images (variant_id);

CREATE INDEX ix_item_images_tenant_id ON item_images (tenant_id);

CREATE INDEX ix_item_images_item_id ON item_images (item_id);

-- item_addon_groups

CREATE TABLE item_addon_groups (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	menu_item_id VARCHAR(36) NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	is_required TINYINT(1) NOT NULL, 
	max_selections INTEGER, 
	sort_order INTEGER NOT NULL, 
	is_active TINYINT(1) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(menu_item_id) REFERENCES items (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_item_addon_groups_menu_item_id ON item_addon_groups (menu_item_id);

CREATE INDEX ix_item_addon_groups_tenant_id ON item_addon_groups (tenant_id);

-- item_addons

CREATE TABLE item_addons (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	group_id VARCHAR(36) NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	extra_price DECIMAL(12, 2) NOT NULL, 
	linked_item_id VARCHAR(36), 
	is_default TINYINT(1) NOT NULL, 
	sort_order INTEGER NOT NULL, 
	is_active TINYINT(1) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(group_id) REFERENCES item_addon_groups (id) ON DELETE CASCADE, 
	FOREIGN KEY(linked_item_id) REFERENCES items (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_item_addons_tenant_id ON item_addons (tenant_id);

CREATE INDEX ix_item_addons_group_id ON item_addons (group_id);

CREATE INDEX ix_item_addons_linked_item_id ON item_addons (linked_item_id);

-- combos

CREATE TABLE combos (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	description TEXT, 
	combo_price DECIMAL(12, 2) NOT NULL, 
	is_popular TINYINT(1) NOT NULL, 
	is_active TINYINT(1) NOT NULL, 
	created_by VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_combos_tenant_name UNIQUE (tenant_id, name), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_combos_tenant_id ON combos (tenant_id);

-- combo_items

CREATE TABLE combo_items (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	combo_id VARCHAR(36) NOT NULL, 
	item_id VARCHAR(36) NOT NULL, 
	item_name VARCHAR(200) NOT NULL, 
	quantity DECIMAL(10, 3) NOT NULL, 
	sort_order INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(combo_id) REFERENCES combos (id) ON DELETE CASCADE, 
	FOREIGN KEY(item_id) REFERENCES items (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_combo_items_item_id ON combo_items (item_id);

CREATE INDEX ix_combo_items_combo_id ON combo_items (combo_id);

CREATE INDEX ix_combo_items_tenant_id ON combo_items (tenant_id);

-- recipes

CREATE TABLE recipes (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	menu_item_id VARCHAR(36) NOT NULL, 
	name VARCHAR(200), 
	yield_quantity DECIMAL(10, 3) NOT NULL, 
	is_active TINYINT(1) NOT NULL, 
	created_by VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_recipes_tenant_menu_item UNIQUE (tenant_id, menu_item_id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(menu_item_id) REFERENCES items (id) ON DELETE RESTRICT, 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_recipes_tenant_id ON recipes (tenant_id);

CREATE INDEX ix_recipes_menu_item_id ON recipes (menu_item_id);

-- recipe_ingredients

CREATE TABLE recipe_ingredients (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	recipe_id VARCHAR(36) NOT NULL, 
	ingredient_item_id VARCHAR(36) NOT NULL, 
	ingredient_name VARCHAR(200) NOT NULL, 
	quantity DECIMAL(10, 3) NOT NULL, 
	uom VARCHAR(16), 
	sort_order INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_recipe_ingredients_item UNIQUE (tenant_id, recipe_id, ingredient_item_id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(recipe_id) REFERENCES recipes (id) ON DELETE CASCADE, 
	FOREIGN KEY(ingredient_item_id) REFERENCES items (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_recipe_ingredients_ingredient_item_id ON recipe_ingredients (ingredient_item_id);

CREATE INDEX ix_recipe_ingredients_tenant_id ON recipe_ingredients (tenant_id);

CREATE INDEX ix_recipe_ingredients_recipe_id ON recipe_ingredients (recipe_id);

-- kots

CREATE TABLE kots (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	kot_number VARCHAR(50) NOT NULL, 
	kot_sequence INTEGER NOT NULL, 
	order_id VARCHAR(36) NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	channel VARCHAR(16) NOT NULL, 
	dining_table_id VARCHAR(36), 
	dining_table_code VARCHAR(32), 
	order_number VARCHAR(50) NOT NULL, 
	notes TEXT, 
	print_count INTEGER NOT NULL, 
	printed_at DATETIME, 
	created_by VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_kots_tenant_number UNIQUE (tenant_id, kot_number), 
	CONSTRAINT uq_kots_tenant_sequence UNIQUE (tenant_id, kot_sequence), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(order_id) REFERENCES orders (id) ON DELETE CASCADE, 
	FOREIGN KEY(dining_table_id) REFERENCES dining_tables (id) ON DELETE SET NULL, 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_kots_dining_table_id ON kots (dining_table_id);

CREATE INDEX ix_kots_tenant_id ON kots (tenant_id);

CREATE INDEX ix_kots_order_id ON kots (order_id);

-- kot_items

CREATE TABLE kot_items (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	kot_id VARCHAR(36) NOT NULL, 
	order_item_id VARCHAR(36) NOT NULL, 
	item_id VARCHAR(36) NOT NULL, 
	item_name VARCHAR(200) NOT NULL, 
	quantity DECIMAL(10, 3) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(kot_id) REFERENCES kots (id) ON DELETE CASCADE, 
	FOREIGN KEY(order_item_id) REFERENCES order_items (id) ON DELETE CASCADE, 
	FOREIGN KEY(item_id) REFERENCES items (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_kot_items_order_item_id ON kot_items (order_item_id);

CREATE INDEX ix_kot_items_tenant_id ON kot_items (tenant_id);

CREATE INDEX ix_kot_items_kot_id ON kot_items (kot_id);

CREATE INDEX ix_kot_items_item_id ON kot_items (item_id);

-- order_items

CREATE TABLE order_items (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	order_id VARCHAR(36) NOT NULL, 
	item_id VARCHAR(36) NOT NULL, 
	item_name VARCHAR(200) NOT NULL, 
	quantity DECIMAL(10, 3) NOT NULL, 
	unit_price DECIMAL(12, 2) NOT NULL, 
	gst_percentage DECIMAL(5, 2) NOT NULL, 
	line_total DECIMAL(12, 2) NOT NULL, 
	combo_id VARCHAR(36), 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(order_id) REFERENCES orders (id) ON DELETE CASCADE, 
	FOREIGN KEY(item_id) REFERENCES items (id) ON DELETE RESTRICT, 
	FOREIGN KEY(combo_id) REFERENCES combos (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_order_items_tenant_id ON order_items (tenant_id);

CREATE INDEX ix_order_items_order_id ON order_items (order_id);

CREATE INDEX ix_order_items_combo_id ON order_items (combo_id);

CREATE INDEX ix_order_items_item_id ON order_items (item_id);

-- order_item_addons

CREATE TABLE order_item_addons (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	order_item_id VARCHAR(36) NOT NULL, 
	addon_id VARCHAR(36), 
	addon_name VARCHAR(120) NOT NULL, 
	extra_price DECIMAL(12, 2) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(order_item_id) REFERENCES order_items (id) ON DELETE CASCADE, 
	FOREIGN KEY(addon_id) REFERENCES item_addons (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_order_item_addons_addon_id ON order_item_addons (addon_id);

CREATE INDEX ix_order_item_addons_tenant_id ON order_item_addons (tenant_id);

CREATE INDEX ix_order_item_addons_order_item_id ON order_item_addons (order_item_id);

-- wastage_entries

CREATE TABLE wastage_entries (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	item_id VARCHAR(36) NOT NULL, 
	item_name VARCHAR(200) NOT NULL, 
	quantity DECIMAL(10, 3) NOT NULL, 
	reason TEXT, 
	category VARCHAR(80), 
	wastage_date DATE NOT NULL, 
	stock_movement_id VARCHAR(36), 
	created_by VARCHAR(36) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(item_id) REFERENCES items (id) ON DELETE RESTRICT, 
	FOREIGN KEY(stock_movement_id) REFERENCES stock_movements (id) ON DELETE SET NULL, 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_wastage_entries_stock_movement_id ON wastage_entries (stock_movement_id);

CREATE INDEX ix_wastage_entries_tenant_id ON wastage_entries (tenant_id);

CREATE INDEX ix_wastage_entries_item_id ON wastage_entries (item_id);

CREATE INDEX ix_wastage_entries_wastage_date ON wastage_entries (wastage_date);

-- sales_returns

CREATE TABLE sales_returns (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	bill_id VARCHAR(36) NOT NULL, 
	return_number VARCHAR(50) NOT NULL, 
	return_sequence INTEGER NOT NULL, 
	kind VARCHAR(16) NOT NULL, 
	reason TEXT NOT NULL, 
	refund_amount DECIMAL(12, 2) NOT NULL, 
	extra_payable DECIMAL(12, 2) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	created_by VARCHAR(36), 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_sales_returns_tenant_number UNIQUE (tenant_id, return_number), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(bill_id) REFERENCES bills (id) ON DELETE RESTRICT, 
	FOREIGN KEY(created_by) REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_sales_returns_bill_id ON sales_returns (bill_id);

CREATE INDEX ix_sales_returns_tenant_id ON sales_returns (tenant_id);

-- sales_return_items

CREATE TABLE sales_return_items (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	return_id VARCHAR(36) NOT NULL, 
	bill_item_id VARCHAR(36) NOT NULL, 
	item_id VARCHAR(36), 
	variant_id VARCHAR(36), 
	item_name VARCHAR(200) NOT NULL, 
	quantity DECIMAL(10, 3) NOT NULL, 
	line_refund DECIMAL(12, 2) NOT NULL, 
	exchange_item_id VARCHAR(36), 
	exchange_variant_id VARCHAR(36), 
	exchange_item_name VARCHAR(200), 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(return_id) REFERENCES sales_returns (id) ON DELETE CASCADE, 
	FOREIGN KEY(bill_item_id) REFERENCES bill_items (id) ON DELETE RESTRICT, 
	FOREIGN KEY(item_id) REFERENCES items (id) ON DELETE SET NULL, 
	FOREIGN KEY(variant_id) REFERENCES item_variants (id) ON DELETE SET NULL, 
	FOREIGN KEY(exchange_item_id) REFERENCES items (id) ON DELETE SET NULL, 
	FOREIGN KEY(exchange_variant_id) REFERENCES item_variants (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_sales_return_items_tenant_id ON sales_return_items (tenant_id);

CREATE INDEX ix_sales_return_items_return_id ON sales_return_items (return_id);

-- serial_units

CREATE TABLE serial_units (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	item_id VARCHAR(36) NOT NULL, 
	serial VARCHAR(64) NOT NULL, 
	status VARCHAR(16) NOT NULL, 
	sold_bill_id VARCHAR(36), 
	sold_bill_item_id VARCHAR(36), 
	sold_at DATETIME, 
	received_at DATETIME NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_serial_units_tenant_serial UNIQUE (tenant_id, serial), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(item_id) REFERENCES items (id) ON DELETE CASCADE, 
	FOREIGN KEY(sold_bill_id) REFERENCES bills (id) ON DELETE SET NULL, 
	FOREIGN KEY(sold_bill_item_id) REFERENCES bill_items (id) ON DELETE SET NULL,
	CONSTRAINT chk_serial_units_status CHECK (status IN ('IN_STOCK', 'SOLD'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_serial_units_item_id ON serial_units (item_id);

CREATE INDEX ix_serial_units_sold_bill_id ON serial_units (sold_bill_id);

CREATE INDEX ix_serial_units_tenant_id ON serial_units (tenant_id);

-- bill_items

CREATE TABLE bill_items (
	id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	bill_id VARCHAR(36) NOT NULL, 
	item_id VARCHAR(36), 
	variant_id VARCHAR(36), 
	serial_unit_id VARCHAR(36), 
	serial_number VARCHAR(64), 
	item_name VARCHAR(200) NOT NULL, 
	quantity DECIMAL(10, 3) NOT NULL, 
	unit_price DECIMAL(12, 2) NOT NULL, 
	gst_percentage DECIMAL(5, 2) NOT NULL, 
	discount DECIMAL(12, 2) NOT NULL, 
	taxable_amount DECIMAL(12, 2) NOT NULL, 
	cgst_amount DECIMAL(12, 2) NOT NULL, 
	sgst_amount DECIMAL(12, 2) NOT NULL, 
	total DECIMAL(12, 2) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT, 
	FOREIGN KEY(bill_id) REFERENCES bills (id) ON DELETE RESTRICT, 
	FOREIGN KEY(item_id) REFERENCES items (id) ON DELETE SET NULL, 
	FOREIGN KEY(variant_id) REFERENCES item_variants (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_bill_items_variant_id ON bill_items (variant_id);

CREATE INDEX ix_bill_items_serial_unit_id ON bill_items (serial_unit_id);

CREATE INDEX ix_bill_items_tenant_id ON bill_items (tenant_id);

-- subscription_notices

CREATE TABLE subscription_notices (
	id VARCHAR(36) NOT NULL, 
	subscription_id VARCHAR(36) NOT NULL, 
	tenant_id VARCHAR(36) NOT NULL, 
	notice_type VARCHAR(20) NOT NULL, 
	period_key VARCHAR(32) NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_subscription_notices_period UNIQUE (subscription_id, notice_type, period_key), 
	FOREIGN KEY(subscription_id) REFERENCES subscriptions (id) ON DELETE RESTRICT, 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_subscription_notices_subscription_id ON subscription_notices (subscription_id);

CREATE INDEX ix_subscription_notices_tenant_id ON subscription_notices (tenant_id);

-- platform_audit_logs

CREATE TABLE platform_audit_logs (
	id VARCHAR(36) NOT NULL, 
	actor_id VARCHAR(36), 
	actor_name VARCHAR(120), 
	actor_email VARCHAR(255), 
	action VARCHAR(50) NOT NULL, 
	entity_type VARCHAR(50) NOT NULL, 
	entity_id VARCHAR(36), 
	tenant_id VARCHAR(36), 
	old_data JSON, 
	new_data JSON, 
	ip_address VARCHAR(45), 
	user_agent VARCHAR(255), 
	created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6), 
	PRIMARY KEY (id), 
	FOREIGN KEY(actor_id) REFERENCES master_admins (id) ON DELETE SET NULL, 
	FOREIGN KEY(tenant_id) REFERENCES tenants (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX ix_platform_audit_logs_action ON platform_audit_logs (action);

CREATE INDEX ix_platform_audit_logs_created_at ON platform_audit_logs (created_at);

CREATE INDEX ix_platform_audit_logs_actor_id ON platform_audit_logs (actor_id);

CREATE INDEX ix_platform_audit_logs_tenant_id ON platform_audit_logs (tenant_id);

-- Performance / listing composites (audit hardening)
CREATE INDEX ix_serial_units_tenant_item_status ON serial_units (tenant_id, item_id, status);
CREATE INDEX ix_item_variants_tenant_item_active ON item_variants (tenant_id, item_id, is_active);
CREATE INDEX ix_item_batches_tenant_expiry_active ON item_batches (tenant_id, expiry_date, is_active);
CREATE INDEX ix_party_ledger_tenant_party_created ON party_ledger_entries (tenant_id, party_type, party_id, created_at);

SET FOREIGN_KEY_CHECKS = 1;

-- End greenfield schema.
