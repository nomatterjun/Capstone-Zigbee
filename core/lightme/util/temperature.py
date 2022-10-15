"""Temperature functions"""

def convert(
    temperature: float, from_unit: str, to_unit: str
) -> float:
    """Convert temperature unit from another"""

    if from_unit == to_unit:
        return temperature

    return temperature
