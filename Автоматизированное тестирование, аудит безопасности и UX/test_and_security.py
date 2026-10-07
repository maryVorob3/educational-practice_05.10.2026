import logging
import math
import sqlite3
import unittest
from tkinter import messagebox

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)

PRODUCT_TYPE_COEFFICIENTS = {1: 1.1, 2: 2.5, 3: 8.43}
MATERIAL_TYPE_DEFECTS = {1: 0.3, 2: 0.12}


def calculate_material_consumption(product_type_id, material_type_id, quantity, param_1, param_2):
    try:
        
        if isinstance(product_type_id, bool) or isinstance(material_type_id, bool) or isinstance(quantity, bool):
            raise ValueError("Тип bool недопустим")
        if isinstance(param_1, bool) or isinstance(param_2, bool):
            raise ValueError("Тип bool недопустим")

        if type(product_type_id) is not int or type(material_type_id) is not int or type(quantity) is not int:
            raise ValueError("ID и количество должны быть целыми числами")
        if not isinstance(param_1, (int, float)) or not isinstance(param_2, (int, float)):
            raise ValueError("Размеры должны быть числами")

        if quantity <= 0 or param_1 <= 0 or param_2 <= 0:
            raise ValueError("Параметры должны быть строго больше нуля")

        if product_type_id not in PRODUCT_TYPE_COEFFICIENTS or material_type_id not in MATERIAL_TYPE_DEFECTS:
            raise ValueError("Несуществующий ID типа в справочнике")

        coef = PRODUCT_TYPE_COEFFICIENTS[product_type_id]
        defect = MATERIAL_TYPE_DEFECTS[material_type_id]

        base = param_1 * param_2 * coef
        total_clean = base * quantity
        total_with_defect = total_clean * (1.0 + (defect / 100.0))

        return math.ceil(total_with_defect)

    except Exception as err:
        logging.error(f"Ошибка в расчете материалов: {str(err)}")
        return -1


def safe_get_partner(cursor, partner_id):
    """Безопасный параметризованный SQL-запрос"""
    query = "SELECT id, partner_name FROM partners WHERE id = ?;"
    cursor.execute(query, (partner_id,))
    return cursor.fetchone()


def show_warning_alert(msg):
    """Вызов предупреждения (Warning)"""
    messagebox.showwarning("Предупреждение", msg)


class TestMaterialCalculation(unittest.TestCase):
    def test_1_valid_calculation(self):
        """Тест 1: Корректный расчет"""
        res = calculate_material_consumption(1, 1, 10, 1.5, 2.0)
        self.assertEqual(res, 34)

    def test_2_bool_rejection(self):
        """Тест 2: Отклонение значения bool (True/False)"""
        res = calculate_material_consumption(True, 1, 10, 1.5, 2.0)
        self.assertEqual(res, -1)

    def test_3_nonexistent_id(self):
        """Тест 3: Несуществующий ID"""
        res = calculate_material_consumption(999, 1, 10, 1.5, 2.0)
        self.assertEqual(res, -1)

    def test_4_negative_params(self):
        """Тест 4: Отрицательные параметры"""
        res = calculate_material_consumption(1, 1, 10, -1.5, 2.0)
        self.assertEqual(res, -1)

    def test_5_zero_quantity(self):
        """Тест 5: Нулевое количество"""
        res = calculate_material_consumption(1, 1, 0, 1.5, 2.0)
        self.assertEqual(res, -1)


if __name__ == "__main__":
    unittest.main()
