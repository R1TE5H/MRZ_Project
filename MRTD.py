def machine_readable_zone_scanner():
    """Stub: Simulates MRZ scanning. Not implemented for this project."""
    pass


def get_data_from_db():
    """Stub: Simulates database lookup. Not implemented for this project."""
    pass


def fletcher16(data: str) -> int:
    sum1, sum2 = 0, 0
    for char in data:
        sum1 = (sum1 + ord(char)) % 255
        sum2 = (sum2 + sum1) % 255
    return (sum2 << 8) | sum1


def check_digit_calculator(value: str) -> int:
    return fletcher16(value) % 10


def checksum_matcher(data_field: str, expected_digit: str) -> bool:
    try:
        return check_digit_calculator(data_field) == int(expected_digit)
    except ValueError:
        return False


def mrz_parser(line_one: str, line_two: str) -> dict:
    data = {
        "document_type": line_one[0],
        "country_code": line_one[2:5],
    }

    name_part = line_one[5:44]
    last_name, given_name = (name_part.split("<<", 1) + [""])[:2]
    data["lastname"] = last_name.replace("<", " ").strip()
    data["given_name"] = given_name.replace("<", " ").strip()

    fields = {
        "passport_number": (line_two[0:9], line_two[9]),
        "nationality": (line_two[10:13], None),
        "date_of_birth": (line_two[13:19], line_two[19]),
        "gender": (line_two[20], None),
        "expiration_date": (line_two[21:27], line_two[27]),
        "personal_number": (line_two[28:42].replace("<", " ").strip(), line_two[43]),
    }

    for label, (value, check_digit) in fields.items():
        data[label] = value
        if check_digit and not checksum_matcher(value, check_digit):
            raise ValueError(f"{label.replace('_', ' ').title()} checksum does not match")

    return data


def viz_encoder(data: dict) -> list[str]:

    first_name = data.get("given_name", "").replace(" ", "<")
    last_name = data.get("lastname", "").replace(" ", "<")
    country = data.get("country_code", "")
    line_one = f"{data.get('document_type', '')}<{country}{last_name}<<{first_name}"
    line_one = line_one.ljust(44, "<")[:44]

    passport = data.get("passport_number", "")
    dob = data.get("date_of_birth", "")
    exp = data.get("expiration_date", "")
    gender = data.get("gender", "")
    personal = data.get("personal_number", "").replace(" ", "<")

    line_two = (
        f"{passport}{check_digit_calculator(passport)}"
        f"{country}{dob}{check_digit_calculator(dob)}"
        f"{gender}{exp}{check_digit_calculator(exp)}"
        f"{personal}"
    )
    line_two = line_two.ljust(43, "<")[:43] + str(check_digit_calculator(personal))

    return [line_one, line_two]
