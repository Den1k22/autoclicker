

def float_seconds_to_int_ms(float_seconds):
    if float_seconds:
        return int(float_seconds * 1000)
    return None

def int_ms_to_float_seconds(int_ms) -> float:
    return float(int_ms) / 1000

def are_all_strings_are_convertable_to_int(numbers):
    for number in numbers:
        if (not number.isnumeric()):
            return False
    else:
        return True
