import sqlite3
import re


def normalize_date(raw_date):
    """Нормализация даты к стандарту ГГГГ-ММ-ДД"""
    raw_date = raw_date.strip()
    
    if re.match(r"^\d{2}[\.\-]\d{2}[\.\-]\d{4}$", raw_date):
        parts = re.split(r"[\.\-]", raw_date)
        return f"{parts[2]}-{parts[1]}-{parts[0]}"
    
    elif re.match(r"^\d{4}[\/\.]\d{2}[\/\.]\d{2}$", raw_date):
        parts = re.split(r"[\/\.]", raw_date)
        return f"{parts[0]}-{parts[1]}-{parts[2]}"
    return raw_date

def run_etl():
    conn = sqlite3.connect("clean_storage.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    with open("schema.sql", "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

     raw_partners = [
        (1, "ООО 'Вектор'", "7701234567", "vector@mail.ru"),
        (2, "ИП Петров А.В.", "7802345678", "petrov@yandex.ru"),
        (3, "АО 'Технолоджис'", "5003456789", "info@techno.ru"),
        (4, "ООО 'Альфа'", "7704567890", "alpha@gmail.com"),
        (5, "ИП Сидоров И.И.", "7805678901", "sidorov@llc.ru")
    ]

    for p in raw_partners:
        cursor.execute("""
            INSERT OR IGNORE INTO partners (id, partner_name, inn, email)
            VALUES (?, ?, ?, ?);
        """, (p[0], p[1].strip(), p[2].strip(), p[3].strip()))

    raw_products = [
        (101, "Ноутбук Pro", 75000.00),
        (102, "Смартфон X", 45000.50),
        (103, "Монитор 27", 18200.00)
    ]

    for prod in raw_products:
        cursor.execute("""
            INSERT OR IGNORE INTO products (id, product_name, price)
            VALUES (?, ?, ?);
        """, (prod[0], prod[1].strip(), prod[2]))

    raw_sales = [
        (1001, 1, 101, "25.10.2023", 2, 150000.0),
        (1002, 2, 102, "2023/10/26", 1, 45000.5),
        (1003, 999, 101, "2023-10-27", 5, 375000.0),
        (1004, 4, 103, "28-10-2023", 10, 182000.0),
        (1005, 3, 102, "2023.10.29", 3, 135001.5),
        (1006, 5, 103, "2023-10-30", 1, 18200.0)
    ]

    for sale in raw_sales:
        sale_id, partner_id, product_id, raw_date, qty, amount = sale

        cursor.execute("SELECT id FROM partners WHERE id = ?;", (partner_id,))
        if not cursor.fetchone():
            continue

        norm_date = normalize_date(raw_date)

        cursor.execute("""
            INSERT OR IGNORE INTO sales_history (id, partner_id, product_id, sale_date, quantity, amount)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (sale_id, partner_id, product_id, norm_date, qty, amount))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    run_etl()
