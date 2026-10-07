CREATE TABLE IF NOT EXISTS partners (
    id INTEGER PRIMARY KEY,
    partner_name TEXT NOT NULL,
    inn TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS sales_history (
    id INTEGER PRIMARY KEY,
    partner_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    sale_date TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (partner_id) REFERENCES partners(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);
