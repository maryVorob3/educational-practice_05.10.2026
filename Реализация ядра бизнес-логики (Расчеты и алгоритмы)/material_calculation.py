import math

PRODUCT_TYPE_COEFFICIENTS = {
    1: 1.1,
    2: 2.5,
    3: 8.43
}

MATERIAL_TYPE_DEFECTS = {
    1: 0.3,
    2: 0.12
}


def calculate_material_consumption(product_type_id, material_type_id, quantity, param_1, param_2):
    """
    Расчет количества сырья с учетом брака.
    Возвращает целое число или -1 при некорректных входных данных.
    """
    if isinstance(product_type_id, bool) or isinstance(material_type_id, bool) or isinstance(quantity, bool):
        return -1
    if isinstance(param_1, bool) or isinstance(param_2, bool):
        return -1

    if type(product_type_id) is not int or type(material_type_id) is not int or type(quantity) is not int:
        return -1
    if not isinstance(param_1, (int, float)) or not isinstance(param_2, (int, float)):
        return -1

    if quantity <= 0 or param_1 <= 0 or param_2 <= 0:
        return -1

    if product_type_id not in PRODUCT_TYPE_COEFFICIENTS or material_type_id not in MATERIAL_TYPE_DEFECTS:
        return -1

    coef = PRODUCT_TYPE_COEFFICIENTS[product_type_id]
    defect = MATERIAL_TYPE_DEFECTS[material_type_id]

    base = param_1 * param_2 * coef
    total = base * quantity
    total_with_defect = total * (1.0 + (defect / 100.0))

    return math.ceil(total_with_defect)


if __name__ == "__main__":
    print(calculate_material_consumption(1, 1, 10, 1.5, 2.0))
