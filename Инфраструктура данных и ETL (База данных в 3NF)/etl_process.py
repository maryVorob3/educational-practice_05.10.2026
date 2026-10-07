import sqlite3


def run_etl():
    conn = sqlite3.connect("master_floor.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    with open("schema.sql", "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    types = ["ЗАО", "ООО", "ПАО", "ОАО", "ИП"]
    for t in types:
        cursor.execute("INSERT OR IGNORE INTO partner_types (type_name) VALUES (?);", (t,))

    raw_partners = [
        (2, "  Паркет 29  ", "Петров Петр ", "parket29@mail.ru", "+7 921 555 44 33", "г. СПб", "7801111111", 10),
        (1, "База Строитель", "Иванова Светлана", "info@stroitel.ru", "+7 223 322 22 32", "г. Москва", "7701222222", 15)
    ]

    for p in raw_partners:
        clean_name = p[1].strip()
        clean_director = p[2].strip() if p[2] else None
        clean_email = p[3].strip()
        clean_phone = p[4].strip()
        clean_inn = p[6].strip()

        cursor.execute("""
            INSERT OR IGNORE INTO partners (type_id, name, director_name, email, phone, legal_address, inn, rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (p[0], clean_name, clean_director, clean_email, clean_phone, p[5], clean_inn, p[7]))

    raw_products = [
        ("  Паркетная доска Ясень ", 2450.50),
        ("Ламинат Дуб Дублин", 1200.00)
    ]
    for prod in raw_products:
        cursor.execute("""
            INSERT OR IGNORE INTO products (product_name, min_cost)
            VALUES (?, ?);
        """, (prod[0].strip(), prod[1]))

    raw_sales = [
        (1, 1, 150, "12.08.2026"),
        (1, 2, 80, "2026-09-01"),
        (999, 1, 50, "2026-09-05")
    ]

    for s in raw_sales:
        p_id, prod_id, qty, raw_date = s

        cursor.execute("SELECT id FROM partners WHERE id = ?;", (p_id,))
        if not cursor.fetchone():
            continue

        if "." in raw_date:
            parts = raw_date.split(".")
            norm_date = f"{parts[2]}-{parts[1]:0>2}-{parts[0]:0>2}"
        else:
            norm_date = raw_date

        cursor.execute("""
            INSERT INTO sales_history (partner_id, product_id, quantity, sale_date)
            VALUES (?, ?, ?, ?);
        """, (p_id, prod_id, qty, norm_date))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    run_etl()
