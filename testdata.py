# testdata.py

BASE_DATA = {
    "document_type": "P",
    "country_code": "CAN",
    "lastname": "DOE",
    "given_name": "JOHN",
    "passport_number": "AB1234567",
    "nationality": "CAN",
    "date_of_birth": "019090",
    "gender": "M",
    "expiration_date": "013030",
    "personal_number": "9876543210",
}

TEST_DATA = {
    "document_type": "P",
    "country_code": "CAN",
    "lastname": "DOE",
    "given_name": "JOHN MICHAEL",
    "passport_number": "AB1234567",
    "nationality": "CAN",
    "date_of_birth": "019090",
    "gender": "M",
    "expiration_date": "013030",
    "personal_number": "9876543210",
}

CHECK_DIGIT_CASES = [
    ("AB1234567", "6"),
    ("900101", "0"),
    ("300101", "8"),
    ("9876543210", "5"),
]

LINE_1_TEST = "P<CANDOE<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<<<"
LINE_2_TEST = "AB12345676CAN0190904M01303069876543210<<<<<5"


def make_data(**overrides):
    data = BASE_DATA.copy()
    data.update(overrides)
    return data
