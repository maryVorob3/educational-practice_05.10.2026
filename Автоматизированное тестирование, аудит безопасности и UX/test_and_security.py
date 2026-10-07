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
            raise ValueError("Параметры не могут быть типа bool")
        if isinstance(param_1, bool) or isinstance(param_2, bool):
            raise ValueError("Параметры не могут быть типа bool")

        if type(product_type_id) is not int or type(material_type_id) is not int or type(quantity) is not int:
            raise ValueError("ID типов и количество должны быть целыми числами")
        if not isinstance(param_1, (int, float)) or not isinstance(param_2, (int, float)):
            raise ValueError("Параметры размеров должны быть числами")

        if quantity <= 0 or param_1 <= 0 or param_2 <= 0:
            raise ValueError("Параметры должны быть положительными")

        if product_type_id not in PRODUCT_TYPE_COEFFICIENTS or material_type_id not in MATERIAL_TYPE_DEFECTS:
            raise ValueError("Несуществующий тип продукции или материала")

        coef = PRODUCT_TYPE_COEFFICIENTS[product_type_id]
        defect = MATERIAL_TYPE_DEFECTS[material_type_id]

        base = param_1 * param_2 * coef
        total = base * quantity
        total_with_defect = total * (1.0 + (defect / 100.0))

        return math.ceil(total_with_defect)

    except Exception as err:
        logging.error(f"Ошибка вычисления: {str(err)}")
        return -1


def safe_get_partner(cursor, partner_id):
    """Безопасный параметризованный SQL-запрос"""
    query = "SELECT id, name FROM partners WHERE id = ?;"
    cursor.execute(query, (partner_id,))
    return cursor.fetchone()


def show_warning_notification(message):
    """Использование окна Предупреждения (Warning)"""
    messagebox.showwarning("Предупреждение", message)


class TestMaterialCalculation(unittest.TestCase):
    def test_1_valid_calculation(self):
        """Корректный расчет"""
        res = calculate_material_consumption(1, 1, 10, 1.5, 2.0)
        self.assertEqual(res, 34)

    def test_2_bool_input_rejection(self):
        """Проверка исправления: bool (True/False) отклоняется"""
        res = calculate_material_consumption(True, 1, 10, 1.5, 2.0)
        self.assertEqual(res, -1)

    def test_3_nonexistent_type(self):
        """Несуществующий тип"""
        res = calculate_material_consumption(99, 1, 10, 1.5, 2.0)
        self.assertEqual(res, -1)

    def test_4_negative_params(self):
        """Отрицательные параметры"""
        res = calculate_material_consumption(1, 1, 10, -1.5, 2.0)
        self.assertEqual(res, -1)

    def test_5_zero_quantity(self):
        """Нулевое количество"""
        res = calculate_material_consumption(1, 1, 0, 1.5, 2.0)
        self.assertEqual(res, -1)


if __name__ == "__main__":
    unittest.main()
