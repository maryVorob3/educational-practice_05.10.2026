CREATE TABLE IF NOT EXISTS partner_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS partners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    director_name TEXT,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    legal_address TEXT,
    inn TEXT NOT NULL UNIQUE,
    rating INTEGER DEFAULT 0,
    FOREIGN KEY (type_id) REFERENCES partner_types(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL UNIQUE,
    min_cost DECIMAL(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS sales_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partner_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    sale_date TEXT NOT NULL,
    FOREIGN KEY (partner_id) REFERENCES partners(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);
