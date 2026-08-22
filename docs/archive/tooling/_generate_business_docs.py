# Generate business-wise documentation packs (docs only).
# Run from repo root: python docs/_generate_business_docs.py

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent / "05-businesses"

COMMON_MODULES = [
    "Authentication",
    "Authorization",
    "Billing Engine",
    "Customers",
    "Payments",
    "Inventory (generic)",
    "Categories / Products",
    "Reports (common)",
    "Notifications",
    "Audit Logs",
    "Printing / PDF",
    "WhatsApp (optional)",
    "AI Assistant (optional)",
    "Settings",
]

COMMON_TABLES = [
    "Tenant",
    "User",
    "Role",
    "Category",
    "Product / Item",
    "Customer",
    "Bill",
    "BillItem",
    "Payment",
    "StockMovement",
    "Notification",
    "AuditLog",
    "BusinessSettings",
]

BUSINESSES = [
    {
        "folder": "01-hotels-restaurants",
        "name": "Hotels / Restaurants",
        "code": "hotel_restaurant",
        "prefix": "REST",
        "slug": "restaurant",
        "api_ns": "restaurant",
        "users": "Owner, Manager, Billing User; future Waiter / Kitchen User",
        "billing_type": "Product (menu) + optional service charge; dine-in / takeaway / delivery",
        "inventory": "Finished menu items + optional recipe/ingredient stock",
        "characteristics": "Table-driven service, kitchen production, GST F&B billing",
        "specific": [
            "Table Management (Available / Occupied / Reserved)",
            "KOT",
            "Kitchen Dashboard",
            "Waiter Management",
            "Split Bill",
            "Merge Tables",
            "Recipes / Ingredient Stock",
            "Food Wastage",
            "Service Charge",
        ],
        "entities": [
            ("RestaurantTable", "Floor tables with status"),
            ("DiningOrder", "Order linked to table/session"),
            ("KOT", "Kitchen order ticket header"),
            ("KOTItem", "Lines on a KOT"),
            ("KitchenTicket", "Kitchen queue view state"),
            ("WaiterAssignment", "Optional waiter on table/order"),
            ("Recipe", "Finished item → recipe"),
            ("RecipeIngredient", "Ingredient quantities"),
            ("WastageEntry", "Food wastage log"),
        ],
        "workflow": """```
Customer
  → Table Selection
  → Order
  → KOT
  → Kitchen
  → Food Preparation
  → Billing
  → Payment
  → Invoice
  → Stock / Recipe Deduction
  → Sales Report
```""",
        "pages": [
            "Restaurant Dashboard",
            "Tables",
            "Orders",
            "KOT",
            "Kitchen Dashboard",
            "Menu / Products",
            "Recipes",
            "Wastage",
            "Billing (common)",
            "Reports",
        ],
        "reports": [
            "Daily sales",
            "Food / menu sales",
            "Table sales",
            "KOT report",
            "Wastage",
            "Ingredient usage",
            "Top-selling food",
        ],
        "apis": [
            ("GET/POST", "/restaurant/tables", "List/create tables"),
            ("PUT", "/restaurant/tables/{id}", "Update status / merge"),
            ("POST", "/restaurant/orders", "Create dining order"),
            ("POST", "/restaurant/kot", "Generate KOT"),
            ("GET", "/restaurant/kitchen", "Kitchen queue"),
            ("POST", "/restaurant/wastage", "Record wastage"),
            ("GET/POST", "/restaurant/recipes", "Recipe CRUD"),
        ],
        "tests": [
            ("Create table", "Table appears Available"),
            ("Occupy table", "Status Occupied"),
            ("Create KOT", "Kitchen receives ticket"),
            ("Complete order → bill", "Bill created from order"),
            ("Inventory deduction", "Recipe/stock reduced"),
            ("Prevent negative stock", "Bill blocked if insufficient"),
            ("Split bill", "Two invoices from one order"),
            ("Merge tables", "Orders combined"),
            ("Track wastage", "Wastage entry + stock impact"),
            ("Cross-tenant table ID", "403/404"),
        ],
        "roadmap": [
            "Restaurant DB entities",
            "Table management",
            "KOT",
            "Kitchen dashboard",
            "Billing integration",
            "Recipe inventory",
            "Restaurant reports",
            "Testing & hardening",
        ],
    },
    {
        "folder": "02-cafes-tea-shops",
        "name": "Cafes / Tea Shops",
        "code": "cafe_tea",
        "prefix": "CAFE",
        "slug": "cafe",
        "api_ns": "cafe",
        "users": "Owner, Manager, Billing User",
        "billing_type": "Quick POS + takeaway; optional dine-in tables",
        "inventory": "Menu items + ingredient stock; combos/add-ons",
        "characteristics": "High-speed counter billing, popular-item focus",
        "specific": [
            "Optional Tables / KOT",
            "Add-ons",
            "Combo offers",
            "Discount / coupon",
            "Popular-item report",
            "Ingredient stock",
        ],
        "entities": [
            ("MenuAddOn", "Add-on options for menu items"),
            ("ComboOffer", "Bundled pricing"),
            ("Coupon", "Optional discount codes"),
            ("CafeTable", "Optional small table set"),
            ("CafeKOT", "Optional quick KOT"),
        ],
        "workflow": """```
Customer
  → Menu / Quick Select
  → Add-ons / Combo (optional)
  → Billing
  → Payment
  → Invoice
  → Stock Deduction
  → Sales Report
```""",
        "pages": [
            "Cafe Dashboard",
            "Quick Billing",
            "Menu",
            "Combos / Add-ons",
            "Optional Tables / KOT",
            "Reports",
        ],
        "reports": [
            "Daily sales",
            "Popular menu items",
            "Ingredient usage",
            "Takeaway vs dine-in",
            "Low stock",
        ],
        "apis": [
            ("GET/POST", "/cafe/add-ons", "Add-on catalog"),
            ("GET/POST", "/cafe/combos", "Combo offers"),
            ("POST", "/cafe/quick-bill", "Fast bill helper (or use common /bills)"),
            ("GET", "/cafe/popular-items", "Popular item metrics"),
        ],
        "tests": [
            ("Quick bill with add-on", "Line totals correct"),
            ("Combo pricing", "Bundle price applied"),
            ("Coupon discount", "Validation rules"),
            ("Stock deduction", "Ingredients/items reduced"),
            ("Insufficient stock", "Blocked with available qty"),
            ("Optional KOT", "Appears when enabled"),
            ("Cross-tenant", "403/404"),
        ],
        "roadmap": [
            "Cafe feature flags",
            "Add-ons / combos",
            "Quick billing UX",
            "Optional KOT/tables",
            "Popular-item reports",
            "Testing",
        ],
    },
    {
        "folder": "03-grocery-kirana",
        "name": "Grocery Stores / Kirana",
        "code": "grocery_kirana",
        "prefix": "GROC",
        "slug": "grocery",
        "api_ns": "grocery",
        "users": "Owner, Manager, Billing User",
        "billing_type": "Fast POS product billing; barcode-driven",
        "inventory": "Units (kg/g/L/piece), batch/expiry, low-stock",
        "characteristics": "High SKU count, credit/udhari, bulk pricing",
        "specific": [
            "Barcode scanner flow",
            "Unit management (kg, g, L, piece)",
            "Low-stock alerts",
            "Stock adjustment",
            "Customer credit / Udhari",
            "Customer payment history",
            "Bulk pricing",
            "Expiry tracking (generic inventory)",
            "Fast POS billing",
        ],
        "entities": [
            ("CustomerCreditAccount", "Udhari balance"),
            ("CustomerCreditLedger", "Credit/payment history"),
            ("BulkPriceTier", "Qty-based pricing"),
            ("ProductBarcode", "Barcode → product map"),
        ],
        "workflow": """```
Customer
  → Product Selection (scan/search)
  → Cart
  → Billing
  → Payment (cash / credit)
  → Invoice
  → Stock Deduction
  → Sales Report
```""",
        "pages": [
            "Grocery Dashboard",
            "Fast POS",
            "Products / Units",
            "Customers / Credit",
            "Suppliers / Purchase (common)",
            "Expiry / Low Stock",
            "Reports",
        ],
        "reports": [
            "Daily sales",
            "Fast-moving products",
            "Low stock",
            "Expiry / near-expiry",
            "Customer credit outstanding",
            "Purchase vs sales",
        ],
        "apis": [
            ("GET", "/grocery/products/by-barcode/{code}", "Barcode lookup"),
            ("GET/POST", "/grocery/credit/{customer_id}", "Credit balance / charge"),
            ("POST", "/grocery/credit/{customer_id}/pay", "Settle credit"),
            ("GET", "/grocery/expiry", "Near-expiry batches"),
        ],
        "tests": [
            ("Barcode lookup", "Correct product"),
            ("Sell by kg", "Qty/unit correct"),
            ("Credit sale", "Ledger updated"),
            ("Credit payment", "Balance reduces"),
            ("Insufficient stock", "Blocked"),
            ("Expiry listing", "Shows near-expiry"),
            ("Bulk price tier", "Unit price changes"),
            ("Cross-tenant", "403/404"),
        ],
        "roadmap": [
            "Units + barcode",
            "Fast POS UX",
            "Credit / udhari",
            "Expiry alerts",
            "Grocery reports",
            "Testing",
        ],
    },
    {
        "folder": "04-clothing",
        "name": "Clothing Shops",
        "code": "clothing",
        "prefix": "CLTH",
        "slug": "clothing",
        "api_ns": "clothing",
        "users": "Owner, Manager, Billing User",
        "billing_type": "Variant-based product billing (size/color)",
        "inventory": "Size-wise and color-wise stock; SKU/barcode",
        "characteristics": "Fashion variants, brand analytics, exchange/return",
        "specific": [
            "Size management (S–XXL)",
            "Color management",
            "Brand management",
            "Barcode / SKU",
            "Product images",
            "Size-wise / color-wise stock",
            "Exchange / Return",
            "Sales by brand / category",
            "Customer purchase history",
        ],
        "entities": [
            ("Size", "Size master"),
            ("Color", "Color master"),
            ("Brand", "Brand master"),
            ("ProductVariant", "Size+color+SKU stock"),
            ("ProductImage", "Image refs"),
            ("ExchangeReturn", "Exchange/return header"),
        ],
        "workflow": """```
Customer
  → Product
  → Size / Color Selection
  → Billing
  → Payment
  → Invoice
  → Variant Inventory Update
  → (optional) Exchange / Return
```""",
        "pages": [
            "Clothing Dashboard",
            "Products / Variants",
            "Sizes / Colors / Brands",
            "Billing",
            "Exchange / Return",
            "Reports",
        ],
        "reports": [
            "Sales by brand",
            "Sales by size",
            "Sales by color",
            "Sales by category",
            "Variant stock",
            "Returns",
        ],
        "apis": [
            ("GET/POST", "/clothing/sizes", "Size master"),
            ("GET/POST", "/clothing/colors", "Color master"),
            ("GET/POST", "/clothing/brands", "Brand master"),
            ("GET/POST", "/clothing/variants", "Variant stock"),
            ("POST", "/clothing/returns", "Exchange/return"),
        ],
        "tests": [
            ("Create variant", "Size+color stock row"),
            ("Sell variant", "Only that stock reduces"),
            ("Wrong size blocked", "Validation"),
            ("Exchange", "Stock in/out correct"),
            ("Brand report", "Totals match"),
            ("Cross-tenant SKU", "403/404"),
        ],
        "roadmap": [
            "Size/color/brand masters",
            "Variants + stock",
            "Billing variant lines",
            "Exchange/return",
            "Clothing reports",
            "Testing",
        ],
    },
    {
        "folder": "05-mobile-shops",
        "name": "Mobile Shops",
        "code": "mobile",
        "prefix": "MOBL",
        "slug": "mobile",
        "api_ns": "mobile",
        "users": "Owner, Manager, Billing User",
        "billing_type": "Serialized product billing (IMEI) + accessories",
        "inventory": "IMEI/serial unique stock; accessories qty stock",
        "characteristics": "Warranty, exchange, repair/service tracking",
        "specific": [
            "IMEI number",
            "Serial number",
            "Mobile model / brand",
            "Warranty tracking",
            "Accessories management",
            "Mobile exchange",
            "Repair / service tracking",
            "Customer purchase history",
            "Stock by IMEI",
        ],
        "entities": [
            ("SerialUnit", "IMEI/serial instance"),
            ("Warranty", "Warranty period / status"),
            ("RepairTicket", "Repair/service job"),
            ("AccessoryLink", "Optional accessory kits"),
        ],
        "workflow": """```
Customer
  → Select Model
  → Select IMEI / Serial
  → Billing
  → Payment
  → Invoice + Warranty
  → Serial marked Sold
```""",
        "pages": [
            "Mobile Dashboard",
            "IMEI Stock",
            "Models / Brands",
            "Accessories",
            "Billing",
            "Warranty / Repair",
            "Reports",
        ],
        "reports": [
            "IMEI stock",
            "Sold serials",
            "Warranty due",
            "Repair status",
            "Accessory sales",
        ],
        "apis": [
            ("GET/POST", "/mobile/serials", "IMEI inventory"),
            ("POST", "/mobile/serials/{id}/sell", "Attach to bill"),
            ("GET/POST", "/mobile/warranties", "Warranty records"),
            ("GET/POST", "/mobile/repairs", "Repair tickets"),
        ],
        "tests": [
            ("Register IMEI", "Unique per tenant"),
            ("Duplicate IMEI rejected", "Validation"),
            ("Sell IMEI", "Status Sold"),
            ("Cannot resell same IMEI", "Blocked"),
            ("Warranty created", "Dates correct"),
            ("Repair ticket", "Lifecycle"),
            ("Cross-tenant IMEI", "403/404"),
        ],
        "roadmap": [
            "SerialUnit model",
            "IMEI billing integration",
            "Warranty",
            "Repair module",
            "Reports",
            "Testing",
        ],
    },
    {
        "folder": "06-hardware",
        "name": "Hardware Stores",
        "code": "hardware",
        "prefix": "HARD",
        "slug": "hardware",
        "api_ns": "hardware",
        "users": "Owner, Manager, Billing User",
        "billing_type": "Unit/weight/length based product billing",
        "inventory": "Multi-unit stock; bulk quantity; brand variants",
        "characteristics": "Trade counters, credit, price history",
        "specific": [
            "Unit management",
            "Weight / length based products",
            "Bulk quantity",
            "Brand management",
            "Product variants",
            "Low-stock alerts",
            "Customer / supplier credit",
            "Price history",
        ],
        "entities": [
            ("UnitOfMeasure", "piece, kg, m, …"),
            ("PriceHistory", "Historical unit prices"),
            ("CreditAccount", "Customer/supplier credit"),
        ],
        "workflow": """```
Customer
  → Product + Unit / Qty (e.g. 10 pipes × ₹450)
  → Billing
  → Payment / Credit
  → Invoice
  → Stock Deduction
```""",
        "pages": [
            "Hardware Dashboard",
            "Products / Units",
            "Billing",
            "Credit",
            "Price History",
            "Reports",
        ],
        "reports": [
            "Sales by unit",
            "Low stock",
            "Credit outstanding",
            "Price history",
            "Top SKUs",
        ],
        "apis": [
            ("GET/POST", "/hardware/units", "UOM master"),
            ("GET", "/hardware/products/{id}/price-history", "Price history"),
            ("GET/POST", "/hardware/credit", "Credit accounts"),
        ],
        "tests": [
            ("Bill 10×450", "Line total 4500"),
            ("Unit conversion", "Stock correct"),
            ("Credit sale", "Ledger"),
            ("Low stock alert", "Notification"),
            ("Cross-tenant", "403/404"),
        ],
        "roadmap": [
            "UOM + bulk qty",
            "Billing with units",
            "Credit",
            "Price history",
            "Reports / testing",
        ],
    },
    {
        "folder": "07-bakery-sweet-shops",
        "name": "Bakery / Sweet Shops",
        "code": "bakery_sweets",
        "prefix": "BAKE",
        "slug": "bakery",
        "api_ns": "bakery",
        "users": "Owner, Manager, Billing User",
        "billing_type": "Retail POS + custom cake orders with advance",
        "inventory": "Ingredients, production batches, expiry, wastage",
        "characteristics": "Production planning, custom orders, delivery slots",
        "specific": [
            "Product production",
            "Ingredient inventory",
            "Batch management",
            "Expiry tracking",
            "Custom cake orders (size/flavor)",
            "Advance / remaining payment",
            "Delivery date/time",
            "Order status",
            "Wastage tracking",
        ],
        "entities": [
            ("ProductionBatch", "Bake batch"),
            ("CakeOrder", "Custom order"),
            ("CakeOrderItem", "Size/flavor lines"),
            ("WastageEntry", "Production wastage"),
        ],
        "workflow": """```
Walk-in: Product → Billing → Payment → Stock
Custom: Customer → Cake Order → Advance → Production → Delivery → Balance → Invoice
```""",
        "pages": [
            "Bakery Dashboard",
            "POS Billing",
            "Production / Batches",
            "Custom Cake Orders",
            "Ingredients",
            "Wastage",
            "Reports",
        ],
        "reports": [
            "Daily sales",
            "Production vs sales",
            "Custom orders due",
            "Wastage",
            "Ingredient low stock",
        ],
        "apis": [
            ("GET/POST", "/bakery/batches", "Production batches"),
            ("GET/POST", "/bakery/cake-orders", "Custom orders"),
            ("POST", "/bakery/cake-orders/{id}/advance", "Advance payment"),
            ("POST", "/bakery/wastage", "Wastage"),
        ],
        "tests": [
            ("Create batch", "Stock increases"),
            ("Custom order advance", "Balance due"),
            ("Complete delivery", "Status + invoice"),
            ("Wastage reduces stock", "Correct qty"),
            ("Expiry on batch", "Listed"),
            ("Cross-tenant", "403/404"),
        ],
        "roadmap": [
            "Batches / ingredients",
            "Custom cake orders",
            "Advances",
            "Wastage",
            "Reports / testing",
        ],
    },
    {
        "folder": "08-stationery",
        "name": "Stationery Shops",
        "code": "stationery",
        "prefix": "STAT",
        "slug": "stationery",
        "api_ns": "stationery",
        "users": "Owner, Manager, Billing User",
        "billing_type": "Fast POS with barcode/SKU",
        "inventory": "High SKU, brand/category, low-stock, bulk pricing",
        "characteristics": "Retail counter, search-heavy catalog",
        "specific": [
            "Barcode / SKU",
            "Brand management",
            "Category management",
            "Bulk pricing",
            "Low-stock alerts",
            "Customer credit",
            "Fast POS billing",
            "Product search",
        ],
        "entities": [
            ("Brand", "Brand master"),
            ("BulkPriceTier", "Qty pricing"),
            ("ProductBarcode", "Barcode map"),
        ],
        "workflow": """```
Customer
  → Search / Scan Product
  → Cart
  → Billing
  → Payment
  → Invoice
  → Stock Deduction
```""",
        "pages": [
            "Stationery Dashboard",
            "Fast POS",
            "Products / Brands",
            "Credit",
            "Reports",
        ],
        "reports": [
            "Daily sales",
            "Top categories",
            "Low stock",
            "Credit outstanding",
        ],
        "apis": [
            ("GET", "/stationery/products/search", "Fast search"),
            ("GET", "/stationery/products/by-barcode/{code}", "Barcode"),
            ("GET/POST", "/stationery/brands", "Brands"),
        ],
        "tests": [
            ("Search product", "Relevant hits"),
            ("Barcode bill", "Correct item"),
            ("Bulk price", "Tier applied"),
            ("Low stock alert", "Fires"),
            ("Cross-tenant", "403/404"),
        ],
        "roadmap": [
            "Search + barcode POS",
            "Brands / bulk price",
            "Credit",
            "Reports / testing",
        ],
    },
    {
        "folder": "09-electronics",
        "name": "Electronics Shops",
        "code": "electronics",
        "prefix": "ELEC",
        "slug": "electronics",
        "api_ns": "electronics",
        "users": "Owner, Manager, Billing User",
        "billing_type": "Serialized + standard product billing",
        "inventory": "Serial/warranty items + accessory qty",
        "characteristics": "Warranty, installation, repair, exchange/return",
        "specific": [
            "Serial number",
            "Warranty tracking",
            "Product model / brand",
            "Barcode",
            "Exchange / Return",
            "Repair / service",
            "Installation tracking",
            "Customer purchase history",
        ],
        "entities": [
            ("SerialUnit", "Serial instance"),
            ("Warranty", "Warranty record"),
            ("RepairTicket", "Service job"),
            ("InstallationJob", "Install scheduling"),
            ("ExchangeReturn", "Returns"),
        ],
        "workflow": """```
Customer
  → Product / Serial
  → Billing
  → Payment
  → Invoice + Warranty
  → Optional Installation / Repair later
```""",
        "pages": [
            "Electronics Dashboard",
            "Serial Stock",
            "Billing",
            "Warranty / Repair / Install",
            "Returns",
            "Reports",
        ],
        "reports": [
            "Serial stock",
            "Warranty due",
            "Repair backlog",
            "Installation schedule",
            "Returns",
        ],
        "apis": [
            ("GET/POST", "/electronics/serials", "Serial inventory"),
            ("GET/POST", "/electronics/warranties", "Warranties"),
            ("GET/POST", "/electronics/repairs", "Repairs"),
            ("GET/POST", "/electronics/installations", "Install jobs"),
        ],
        "tests": [
            ("Sell serial", "Marked sold"),
            ("Warranty auto-create", "OK"),
            ("Install job", "Status flow"),
            ("Return serial", "Restock rules"),
            ("Cross-tenant", "403/404"),
        ],
        "roadmap": [
            "Serial + warranty",
            "Repair / install",
            "Returns",
            "Reports / testing",
        ],
    },
    {
        "folder": "10-furniture",
        "name": "Furniture Shops",
        "code": "furniture",
        "prefix": "FURN",
        "slug": "furniture",
        "api_ns": "furniture",
        "users": "Owner, Manager, Billing User",
        "billing_type": "Showroom sales + custom orders with advances",
        "inventory": "Finished goods + materials; delivery/install jobs",
        "characteristics": "Dimensions, custom work, delivery/install",
        "specific": [
            "Product dimensions / material / color",
            "Custom furniture orders",
            "Advance / remaining payment",
            "Delivery management",
            "Installation tracking",
            "Order status",
            "Customer quotation",
        ],
        "entities": [
            ("FurnitureSpec", "Dims/material/color"),
            ("CustomOrder", "Custom job"),
            ("Quotation", "Customer quote"),
            ("DeliveryJob", "Delivery"),
            ("InstallationJob", "Install"),
        ],
        "workflow": """```
Showroom: Product → Bill → Payment → Delivery
Custom: Quote → Advance → Production → Delivery/Install → Balance → Invoice
```""",
        "pages": [
            "Furniture Dashboard",
            "Catalog / Specs",
            "Quotations",
            "Custom Orders",
            "Deliveries / Install",
            "Billing",
            "Reports",
        ],
        "reports": [
            "Sales",
            "Custom orders pipeline",
            "Pending balances",
            "Deliveries due",
            "Installations",
        ],
        "apis": [
            ("GET/POST", "/furniture/quotations", "Quotes"),
            ("GET/POST", "/furniture/custom-orders", "Custom orders"),
            ("POST", "/furniture/custom-orders/{id}/advance", "Advance"),
            ("GET/POST", "/furniture/deliveries", "Deliveries"),
        ],
        "tests": [
            ("Create quotation", "Totals"),
            ("Convert to order", "Linked"),
            ("Advance payment", "Balance due"),
            ("Delivery complete", "Status"),
            ("Cross-tenant", "403/404"),
        ],
        "roadmap": [
            "Specs + quotes",
            "Custom orders + advances",
            "Delivery/install",
            "Reports / testing",
        ],
    },
    {
        "folder": "11-building-material",
        "name": "Hardware / Building Material",
        "code": "building_material",
        "prefix": "BLDM",
        "slug": "building-material",
        "api_ns": "building-material",
        "users": "Owner, Manager, Billing User",
        "billing_type": "Measured/bulk trade billing + transport charges",
        "inventory": "Multi-unit, warehouse stock, transfers",
        "characteristics": "Quotations, challans, credit, transport",
        "specific": [
            "Multiple units",
            "Weight / length / area",
            "Bulk pricing",
            "Quotation",
            "Delivery challan",
            "Customer / supplier credit",
            "Transport charges",
            "Delivery management",
            "Warehouse stock",
            "Price history",
        ],
        "entities": [
            ("Warehouse", "Location"),
            ("StockTransfer", "Inter-warehouse"),
            ("Quotation", "Trade quote"),
            ("DeliveryChallan", "Challan"),
            ("TransportCharge", "Freight line/fee"),
            ("CreditAccount", "Credit"),
            ("PriceHistory", "Prices"),
        ],
        "workflow": """```
Enquiry → Quotation → Order/Bill → Challan / Delivery → Payment/Credit → Stock
```""",
        "pages": [
            "Building Material Dashboard",
            "Warehouses",
            "Quotations",
            "Billing / Challans",
            "Credit",
            "Transfers",
            "Reports",
        ],
        "reports": [
            "Warehouse stock",
            "Customer/supplier credit",
            "Quotations pipeline",
            "Challan register",
            "Price history",
        ],
        "apis": [
            ("GET/POST", "/building-material/warehouses", "Warehouses"),
            ("POST", "/building-material/transfers", "Stock transfer"),
            ("GET/POST", "/building-material/quotations", "Quotes"),
            ("GET/POST", "/building-material/challans", "Challans"),
        ],
        "tests": [
            ("Transfer stock", "Balances move"),
            ("Quotation → bill", "Linked"),
            ("Challan print", "OK"),
            ("Transport fee on bill", "Total correct"),
            ("Cross-tenant warehouse", "403/404"),
        ],
        "roadmap": [
            "Warehouses + UOM",
            "Quotes / challans",
            "Credit + transport",
            "Reports / testing",
        ],
    },
    {
        "folder": "12-book-stores",
        "name": "Book Stores",
        "code": "bookstore",
        "prefix": "BOOK",
        "slug": "books",
        "api_ns": "books",
        "users": "Owner, Manager, Billing User",
        "billing_type": "Product POS with ISBN metadata",
        "inventory": "ISBN/title stock, returns, bulk pricing",
        "characteristics": "Publisher/author catalog, barcode",
        "specific": [
            "ISBN",
            "Author / Publisher / Edition",
            "Barcode",
            "Book category",
            "Stock management",
            "Bulk pricing",
            "Customer purchase history",
            "Return management",
        ],
        "entities": [
            ("BookMetadata", "ISBN, author, publisher, edition"),
            ("BookReturn", "Returns"),
        ],
        "workflow": """```
Customer
  → Search ISBN / Title
  → Billing
  → Payment
  → Invoice
  → Stock Update
  → Optional Return
```""",
        "pages": [
            "Bookstore Dashboard",
            "Catalog (ISBN)",
            "POS Billing",
            "Returns",
            "Reports",
        ],
        "reports": [
            "Top titles",
            "Publisher sales",
            "Low stock",
            "Returns",
            "Customer history",
        ],
        "apis": [
            ("GET/POST", "/books/catalog", "Book metadata"),
            ("GET", "/books/by-isbn/{isbn}", "ISBN lookup"),
            ("POST", "/books/returns", "Returns"),
        ],
        "tests": [
            ("ISBN unique", "Per tenant"),
            ("Sell by ISBN", "Stock--"),
            ("Return", "Stock++"),
            ("Cross-tenant", "403/404"),
        ],
        "roadmap": [
            "BookMetadata",
            "ISBN POS",
            "Returns",
            "Reports / testing",
        ],
    },
    {
        "folder": "13-wholesale",
        "name": "Wholesale Shops",
        "code": "wholesale",
        "prefix": "WHOL",
        "slug": "wholesale",
        "api_ns": "wholesale",
        "users": "Owner, Manager, Billing User",
        "billing_type": "B2B wholesale/retail/customer-wise pricing",
        "inventory": "Multi-warehouse, transfers, bulk qty",
        "characteristics": "Credit, PO/SO, quotations, challans, outstanding",
        "specific": [
            "Wholesale / retail / customer-wise pricing",
            "Bulk quantity",
            "Credit / Udhari",
            "Payment tracking",
            "Outstanding reports",
            "Multiple warehouses",
            "Stock transfer",
            "Purchase order / Sales order",
            "Quotation / Delivery challan",
            "Barcode",
            "GST invoice",
        ],
        "entities": [
            ("Warehouse", "Location"),
            ("StockTransfer", "Transfer"),
            ("CustomerPriceList", "Customer-wise prices"),
            ("PurchaseOrder", "PO"),
            ("SalesOrder", "SO"),
            ("Quotation", "Quote"),
            ("DeliveryChallan", "Challan"),
            ("CreditAccount", "Credit"),
        ],
        "workflow": """```
Enquiry → Quotation → Sales Order → Challan / Invoice → Payment/Credit → Warehouse Stock
Purchase: PO → Receive → Stock
```""",
        "pages": [
            "Wholesale Dashboard",
            "Price Lists",
            "Quotations / SO / PO",
            "Warehouses / Transfers",
            "Billing / Challans",
            "Outstanding",
            "Reports",
        ],
        "reports": [
            "Customer outstanding",
            "Supplier outstanding",
            "Warehouse stock",
            "Wholesale sales",
            "Customer-wise sales",
            "Top products",
        ],
        "apis": [
            ("GET/POST", "/wholesale/price-lists", "Pricing"),
            ("GET/POST", "/wholesale/sales-orders", "SO"),
            ("GET/POST", "/wholesale/purchase-orders", "PO"),
            ("GET/POST", "/wholesale/warehouses", "Warehouses"),
            ("POST", "/wholesale/transfers", "Transfers"),
            ("GET", "/wholesale/outstanding", "Outstanding"),
        ],
        "tests": [
            ("Customer price applied", "Correct rate"),
            ("SO → invoice", "Stock move"),
            ("Warehouse transfer", "Balances"),
            ("Outstanding report", "Matches ledger"),
            ("Cross-tenant", "403/404"),
        ],
        "roadmap": [
            "Price lists + credit",
            "PO/SO/quotes/challans",
            "Warehouses",
            "Outstanding reports",
            "Testing",
        ],
    },
    {
        "folder": "14-travel-agencies",
        "name": "Travel Agencies",
        "code": "travel_agency",
        "prefix": "TRVL",
        "slug": "travel",
        "api_ns": "travel",
        "users": "Owner, Manager, Billing User / Agent",
        "billing_type": "Service-first (packages/bookings); mixed product optional",
        "inventory": "Usually none; optional merchandise light stock",
        "characteristics": "Bookings, advances, itineraries, commissions — not traditional inventory POS",
        "specific": [
            "Tour package management",
            "Package pricing",
            "Booking management",
            "Advance / remaining payment",
            "Booking status",
            "Hotel / vehicle / ticket details",
            "Customer documents",
            "Travel itinerary",
            "Agent / commission management",
        ],
        "entities": [
            ("TourPackage", "Sellable package/service"),
            ("Booking", "Customer booking"),
            ("Itinerary", "Trip plan"),
            ("TravelDocument", "Passport etc. refs"),
            ("BookingComponent", "Hotel/vehicle/ticket lines"),
            ("Agent", "Travel agent"),
            ("AgentCommission", "Commission entries"),
        ],
        "workflow": """```
Customer
  → Package Selection
  → Booking
  → Advance Payment
  → Remaining Payment(s)
  → Invoice (service)
  → Booking Completion
  → Commission (if agent)
```""",
        "pages": [
            "Travel Dashboard",
            "Packages",
            "Bookings",
            "Itineraries / Documents",
            "Payments / Invoices",
            "Agents / Commission",
            "Reports",
        ],
        "reports": [
            "Booking report",
            "Package sales",
            "Pending payments",
            "Agent commission",
            "Revenue",
            "Upcoming trips",
        ],
        "apis": [
            ("GET/POST", "/travel/packages", "Packages"),
            ("GET/POST", "/travel/bookings", "Bookings"),
            ("POST", "/travel/bookings/{id}/payments", "Advance/balance"),
            ("GET/POST", "/travel/agents", "Agents"),
            ("GET", "/travel/commissions", "Commissions"),
        ],
        "tests": [
            ("Create package", "Service catalog"),
            ("Booking + advance", "Balance due"),
            ("Complete booking", "Status"),
            ("Commission calc", "Correct"),
            ("Service invoice", "No stock move"),
            ("Cross-tenant booking", "403/404"),
        ],
        "roadmap": [
            "Packages + bookings",
            "Advances / invoices",
            "Itinerary / documents",
            "Commission",
            "Reports / testing",
        ],
    },
]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def overview(b: dict) -> str:
    specific = "\n".join(f"- {x}" for x in b["specific"])
    common = "\n".join(f"- {x}" for x in COMMON_MODULES)
    return f"""# {b['name']} — Overview

**Business code:** `{b['code']}`  
**Documentation pack:** `docs/05-businesses/{b['folder']}/`  
**Medical Store:** Not applicable (permanently out of product scope)

## Purpose

Enable {b['name']} tenants on Prabha Billing SaaS using the **Common Core** plus this industry pack.

## Target users

{b['users']}

## Business characteristics

{b['characteristics']}

| Aspect | Detail |
|--------|--------|
| Billing type | {b['billing_type']} |
| Inventory | {b['inventory']} |

## Typical workflow

See [workflow.md](./workflow.md).

## Common modules reused

{common}

> Billing details live in [`../../04-common-modules/billing.md`](../../04-common-modules/billing.md). This pack only documents **extensions**.

## Industry-specific modules / features

{specific}

## Traceability

Requirements → Features → Modules → DB → API → UI → Tests → Roadmap phases in this folder.  
Global concept: [`../../00-overview/requirements-traceability.md`](../../00-overview/requirements-traceability.md).
"""


def requirements(b: dict) -> str:
    lines = [
        f"# {b['name']} — Requirements",
        "",
        "IDs are stable for traceability. Priority: **P0** must-have for pack MVP, **P1** next, **P2** later.",
        "",
        "| ID | Requirement | Priority | Module | Dependencies |",
        "|----|-------------|----------|--------|--------------|",
    ]
    reqs = [
        (f"{b['prefix']}-REQ-001", f"Owner can configure {b['name']}-specific catalog/settings for the tenant.", "P0", "Settings / Catalog", "Common tenant"),
        (f"{b['prefix']}-REQ-002", "Billing users can create bills using common billing engine with industry line extensions where needed.", "P0", "Billing", "Common billing"),
        (f"{b['prefix']}-REQ-003", "System shall prevent completing product sale when available stock is insufficient (unless negative stock allowed).", "P0", "Inventory", "Common inventory"),
        (f"{b['prefix']}-REQ-004", f"System shall support industry features: {', '.join(b['specific'][:3])}.", "P0", "Industry pack", "Feature flags"),
        (f"{b['prefix']}-REQ-005", "All industry data is tenant-scoped; cross-tenant IDs return 403/404.", "P0", "Security", "AuthZ"),
        (f"{b['prefix']}-REQ-006", "Owner can view audit/activity for staff billing and catalog actions.", "P0", "Audit", "Common audit"),
        (f"{b['prefix']}-REQ-007", f"Dashboard shows {b['name']}-relevant widgets when business type is enabled.", "P1", "Dashboard", "Module registry"),
        (f"{b['prefix']}-REQ-008", "Industry reports listed in reports.md are available to authorized roles.", "P1", "Reports", "Common reports"),
        (f"{b['prefix']}-REQ-009", "Optional WhatsApp/PDF invoice flows reuse common integrations.", "P1", "WhatsApp/PDF", "Common modules"),
        (f"{b['prefix']}-REQ-010", "Feature flags disable unused cross-industry capabilities (e.g. IMEI for restaurants).", "P0", "Config", "BusinessType matrix"),
    ]
    # add a few specific
    for i, feat in enumerate(b["specific"][:5], start=11):
        lines.append(
            f"| {b['prefix']}-REQ-{i:03d} | The system shall support: **{feat}**. | P0 | Industry | Pack entities |"
        )
    for row in reqs:
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |")
    lines.append("")
    lines.append("Common billing/inventory requirements are **not** duplicated here — see common-module docs.")
    return "\n".join(lines)


def features(b: dict) -> str:
    common = "\n".join(f"- {x}" for x in ["Billing", "Customer Management", "Payments", "Reports", "Notifications", "Audit", "Printing/PDF", "Settings"])
    specific = "\n".join(f"- {x}" for x in b["specific"])
    return f"""# {b['name']} — Features

## COMMON FEATURES (reused)

{common}

Uses: [`../../04-common-modules/billing.md`](../../04-common-modules/billing.md), inventory, customers, etc.

## BUSINESS-SPECIFIC FEATURES

{specific}

## Explicitly NOT enabled (examples)

Features belonging to other industries stay **off** via configuration (see feature matrix).  
**Medical Store / medicine / prescription features are never enabled.**
"""


def workflow(b: dict) -> str:
    return f"""# {b['name']} — Workflow

## Primary flow

{b['workflow']}

## Notes

- Tenant isolation applies at every step.
- Product stock movements use the **common inventory engine** when lines are PRODUCT.
- Service-oriented steps (especially Travel) may skip stock deduction.
- Payments/invoices reuse the **common billing engine**.

## Mermaid

```mermaid
flowchart TD
  A[Start] --> B[Industry entry steps]
  B --> C[Common Billing]
  C --> D[Payment]
  D --> E[Invoice / PDF / WhatsApp]
  E --> F[Inventory if product]
  F --> G[Reports / Audit]
```
"""


def modules(b: dict) -> str:
    rows = [
        "| Module | Type | Priority | Dependencies |",
        "|--------|------|----------|--------------|",
        "| Billing | Common | High | Auth, Products |",
        "| Inventory | Common | High* | Products (*light/none for Travel) |",
        "| Customers | Common | High | Tenant |",
        "| Payments | Common | High | Billing |",
        "| Reports | Common | High | Billing data |",
    ]
    for feat in b["specific"]:
        rows.append(f"| {feat} | Industry | High | Common core + pack |")
    return f"""# {b['name']} — Modules

| Module | Type | Priority | Dependencies |
|--------|------|----------|--------------|
""" + "\n".join(rows[2:]) + f"""

## Purpose summary

This pack activates only when `business_type = {b['code']}`.  
Implementation lives under backend/frontend `modules/{b['slug']}/` (conceptual — not created yet).
"""


def database(b: dict) -> str:
    common = "\n".join(f"| {t} | COMMON ENTITY | Reused |" for t in COMMON_TABLES)
    specific = "\n".join(f"| {e} | BUSINESS-SPECIFIC | {d} |" for e, d in b["entities"])
    return f"""# {b['name']} — Database

> Conceptual only. No tables created in documentation phase.

## COMMON ENTITIES reused

| Entity | Class | Notes |
|--------|-------|-------|
{common}

## BUSINESS-SPECIFIC ENTITIES

| Entity | Class | Purpose |
|--------|-------|---------|
{specific}

## Relationships (summary)

- All specific entities carry `tenant_id` (RESTRICT to Tenant).
- Prefer FK to `Bill` / `Product` / `Customer` rather than duplicating money columns.
- Serial/IMEI uniqueness is **per tenant**.

## See also

[`../../06-database/business-specific-tables.md`](../../06-database/business-specific-tables.md) · [`../../06-database/common-tables.md`](../../06-database/common-tables.md)
"""


def api(b: dict) -> str:
    lines = [
        f"# {b['name']} — API",
        "",
        f"Namespace: `/api/v1/{b['api_ns']}/...`",
        "",
        "Do **not** re-document common `/bills`, `/customers`, `/items` here — use those.",
        "",
        "| Method | Endpoint | Purpose | Auth | Permission | Tenant |",
        "|--------|----------|---------|------|------------|--------|",
    ]
    for method, path, purpose in b["apis"]:
        lines.append(
            f"| {method} | `/api/v1{path}` | {purpose} | JWT | industry + role | Yes |"
        )
    lines += [
        "",
        "## Contract notes",
        "",
        "- **Authentication:** Bearer JWT (business user).",
        "- **Tenant scope:** from JWT only.",
        "- **Validation:** 400 on bad payload; 409 on unique conflicts (e.g. IMEI).",
        "- **Errors:** 401 / 403 / 404 / 402 (subscription).",
        "",
        "### Example response envelope",
        "",
        "```json",
        '{ "success": true, "data": {}, "meta": {}, "error": null }',
        "```",
    ]
    return "\n".join(lines)


def frontend(b: dict) -> str:
    pages = "\n".join(
        f"| {p} | {b['name']} ops | Owner / Manager / Billing (as permitted) | MUI tables/forms | Pack APIs + common | Responsive |"
        for p in b["pages"]
    )
    return f"""# {b['name']} — Frontend

Conceptual routes under `modules/{b['slug']}/` (not implemented yet).

| Page | Purpose | Roles | Components | API deps | UX |
|------|---------|-------|------------|----------|-----|
{pages}

## Shared UI

Reuse common Billing, Customers, Reports pages. Industry nav items appear only when the module is enabled.

## Responsive

All pages: mobile + desktop; dark mode via existing theme.
"""


def reports(b: dict) -> str:
    items = "\n".join(f"- {r}" for r in b["reports"])
    return f"""# {b['name']} — Reports

## Industry reports

{items}

## Common reports reused

- Today's / weekly / monthly sales  
- Payment report  
- GST report (where applicable)  

See [`../../04-common-modules/reports.md`](../../04-common-modules/reports.md).
"""


def permissions(b: dict) -> str:
    return f"""# {b['name']} — Permissions

| Capability | Owner | Manager | Billing User |
|------------|-------|---------|--------------|
| Configure industry settings | Yes | Limited | No |
| View dashboard widgets | Yes | Yes | Limited |
| Create bills | Yes | Yes | Yes |
| Cancel bills | Yes | Yes | Policy |
| Manage industry masters | Yes | Yes | No* |
| Inventory adjustments | Yes | Yes | If permitted |
| Reports | Yes | Yes | Limited |
| View audit / item activity | Yes | Limited | No |

\\* Billing User may edit products/items only if tenant permission allows — **all such actions are audited**.

Master Admin is platform-only and not a shop role.
"""


def testing(b: dict) -> str:
    lines = [
        f"# {b['name']} — Testing",
        "",
        "| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |",
        "|---------|---------|--------------|-----------------|----------|----------|",
    ]
    for i, (purpose, expected) in enumerate(b["tests"], start=1):
        tid = f"TEST-{b['prefix']}-{i:03d}"
        lines.append(
            f"| {tid} | {purpose} | Tenant type={b['code']}; user logged in | Execute {purpose.lower()} | {expected} | P0 |"
        )
    lines += [
        "",
        "## Isolation",
        "",
        f"| TEST-{b['prefix']}-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |",
        "",
        "Do not run destructive tests on production data.",
    ]
    return "\n".join(lines)


def roadmap_section(b: dict) -> str:
    phases = "\n".join(f"{i}. {p}" for i, p in enumerate(b["roadmap"], start=1))
    return f"""# {b['name']} — Development roadmap (documentation only)

Do **not** start these phases until documentation is approved and the corresponding program sprint begins.

{phases}

Related program plan: [`../../12-sprints/sprint-overview.md`](../../12-sprints/sprint-overview.md).
"""


def main() -> None:
    for b in BUSINESSES:
        base = ROOT / b["folder"]
        write(base / "overview.md", overview(b))
        write(base / "requirements.md", requirements(b))
        write(base / "features.md", features(b))
        write(base / "workflow.md", workflow(b))
        write(base / "modules.md", modules(b))
        write(base / "database.md", database(b))
        write(base / "api.md", api(b))
        write(base / "frontend.md", frontend(b))
        write(base / "reports.md", reports(b))
        write(base / "permissions.md", permissions(b))
        write(base / "testing.md", testing(b))
        write(base / "roadmap.md", roadmap_section(b))
    print(f"Generated {len(BUSINESSES)} business packs under {ROOT}")


if __name__ == "__main__":
    main()
