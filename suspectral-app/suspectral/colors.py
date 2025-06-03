from PySide6.QtGui import QColor


def get_color(index: int) -> QColor:
    """
    Returns a distinct QColor object from a predefined palette based on the input index.

    The function cycles through a list of 9 hardcoded HSV colors with full opacity,
    providing a consistent way to assign colors to indices. If the index `n` is
    greater than 8, it wraps around using modulo 9.

    Parameters:
        index (int): The index of the desired color.

    Returns:
        QColor: The color corresponding to the given index, chosen from a fixed HSV palette.
    """
    return [
        QColor.fromHsvF(0.000000, 0.827268, 1.000000, 1.0),
        QColor.fromHsvF(0.089250, 0.972351, 1.000000, 1.0),
        QColor.fromHsvF(0.229750, 0.769558, 0.900000, 1.0),
        QColor.fromHsvF(0.448278, 0.966674, 1.000000, 1.0),
        QColor.fromHsvF(0.532361, 0.955062, 1.000000, 1.0),
        QColor.fromHsvF(0.614472, 0.842557, 1.000000, 1.0),
        QColor.fromHsvF(0.728111, 0.755276, 1.000000, 1.0),
        QColor.fromHsvF(0.815028, 0.819898, 1.000000, 1.0),
        QColor.fromHsvF(0.925917, 0.821912, 0.800000, 1.0),
    ][index % 9]
