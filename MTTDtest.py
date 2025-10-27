import pytest

import MRTD
from testdata import (
    CHECK_DIGIT_CASES,
    LINE_1_TEST,
    LINE_2_TEST,
    TEST_DATA,
    make_data,
)


# ---------------------------------------------------------------------
# Stub behaviour
# ---------------------------------------------------------------------
def test_machine_readable_zone_scanner_stub():
    # Hardware stub should return None when invoked
    assert MRTD.machine_readable_zone_scanner() is None


def test_get_data_from_db_stub():
    # Database stub should return None when invoked
    assert MRTD.get_data_from_db() is None


# ---------------------------------------------------------------------
# Fletcher-16 checksum
# ---------------------------------------------------------------------
@pytest.mark.parametrize(
    "data, expected",
    [
        ("ABC", 35782),
        ("", 0),
        ("123456", 11318),
    ],
)
def test_fletcher16_exact_values(data, expected):
    # Deterministic checksum values catch arithmetic mutations
    assert MRTD.fletcher16(data) == expected


@pytest.mark.parametrize(
    "data, expected_tail",
    [
        ("MRZ", 0xE6F9),
        ("CANADA", 0xA099),
    ],
)
def test_fletcher16_bit_structure(data, expected_tail):
    # Validate the lower 16 bits to exercise both accumulators
    assert MRTD.fletcher16(data) & 0xFFFF == expected_tail


# ---------------------------------------------------------------------
# Check digit calculator
# ---------------------------------------------------------------------
@pytest.mark.parametrize("value, expected_digit", CHECK_DIGIT_CASES)
def test_check_digit_calculator_known_cases(value, expected_digit):
    # Known ICAO examples should reproduce published check digits
    digit = MRTD.check_digit_calculator(value)
    assert str(digit) == expected_digit


@pytest.mark.parametrize("data", ["123456", "", "A1B2C3"])
def test_check_digit_calculator_range(data):
    # Check digit should always be a single decimal digit
    digit = MRTD.check_digit_calculator(data)
    assert 0 <= digit < 10


@pytest.mark.parametrize("data", ["", "@#$%^", "123!@#"])
def test_check_digit_calculator_edge_cases(data):
    # Non-alphanumeric characters are still processed without error
    digit = MRTD.check_digit_calculator(data)
    assert 0 <= digit < 10


# ---------------------------------------------------------------------
# Checksum matcher
# ---------------------------------------------------------------------
@pytest.mark.parametrize(
    "data, expected",
    [
        ("123456", str(MRTD.check_digit_calculator("123456"))),
        ("ABCDEF", str(MRTD.check_digit_calculator("ABCDEF"))),
        ("", str(MRTD.check_digit_calculator(""))),
    ],
)
def test_checksum_matcher_true(data, expected):
    # Correct digits must produce a match
    assert MRTD.checksum_matcher(data, expected)


@pytest.mark.parametrize(
    "data, expected",
    [
        ("123456", str((MRTD.check_digit_calculator("123456") + 1) % 10)),
        ("ABCDEF", str((MRTD.check_digit_calculator("ABCDEF") + 2) % 10)),
    ],
)
def test_checksum_matcher_false(data, expected):
    # Incorrect digits must fail the match
    assert not MRTD.checksum_matcher(data, expected)


def test_checksum_matcher_invalid_digit():
    # Non-numeric expected digits should return False, not raise
    assert not MRTD.checksum_matcher("123456", "X")


# ---------------------------------------------------------------------
# MRZ parser and encoder
# ---------------------------------------------------------------------
def test_viz_encoder_and_parser_roundtrip():
    # Encoding then parsing should preserve the original data fields
    lines = MRTD.viz_encoder(TEST_DATA)
    parsed = MRTD.mrz_parser(*lines)
    for key, value in TEST_DATA.items():
        assert parsed[key] == value


def test_mrz_parser_invalid_checksum():
    # Tampering with a check digit must raise a ValueError
    line1 = "P<CANDOE<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<<<"
    line2 = "AB12345670CAN0190904M01303069876543210<<<<<5"  # invalid passport digit
    with pytest.raises(ValueError):
        MRTD.mrz_parser(line1, line2)


def test_viz_encoder_produces_expected_lines():
    # Regression guard for the canonical MRZ output
    lines = MRTD.viz_encoder(TEST_DATA)
    assert lines[0] == LINE_1_TEST
    assert lines[1] == LINE_2_TEST


def test_viz_encoder_embeds_valid_check_digits():
    # Ensure each check digit in line_two is derived from the correct slice
    line_one, line_two = MRTD.viz_encoder(TEST_DATA)
    assert MRTD.check_digit_calculator(line_two[0:9]) == int(line_two[9])
    assert MRTD.check_digit_calculator(line_two[13:19]) == int(line_two[19])
    assert MRTD.check_digit_calculator(line_two[21:27]) == int(line_two[27])
    personal = line_two[28:42].replace("<", " ").strip()
    assert MRTD.check_digit_calculator(personal) == int(line_two[43])


@pytest.mark.parametrize(
    "data",
    [
        {
            "document_type": "P",
            "country_code": "USA",
            "lastname": "O'NEILL",
            "given_name": "MARY-JANE",
            "passport_number": "X12345678",
            "nationality": "USA",
            "date_of_birth": "010101",
            "gender": "F",
            "expiration_date": "020202",
            "personal_number": "1234567890",
        },
        {
            "document_type": "P",
            "country_code": "GBR",
            "lastname": "SMITH!",
            "given_name": "JACK?",
            "passport_number": "Y98765432",
            "nationality": "GBR",
            "date_of_birth": "030303",
            "gender": "M",
            "expiration_date": "040404",
            "personal_number": "0987654321",
        },
    ],
)
def test_viz_encoder_punctuation(data):
    # Punctuation and spacing should normalise correctly through round-trip
    lines = MRTD.viz_encoder(data)
    parsed = MRTD.mrz_parser(*lines)
    assert parsed["lastname"].replace(" ", "") == data["lastname"].replace("'", "").replace("!", "")
    assert parsed["given_name"].replace(" ", "") == data["given_name"].replace("-", "").replace("?", "")


def test_viz_encoder_lastname_commas_removed():
    # Last-name commas separate suffixes and should be stripped entirely
    data = make_data(lastname="SMITH,JR", given_name="JANE")
    lines = MRTD.viz_encoder(data)
    parsed = MRTD.mrz_parser(*lines)
    assert parsed["lastname"] == "SMITHJR"


@pytest.mark.parametrize("country_code", ["CAN", "USA", "GBR"])
def test_country_code_validity(country_code):
    # Valid country codes should be preserved through encoder/parser
    data = TEST_DATA.copy()
    data["country_code"] = country_code
    lines = MRTD.viz_encoder(data)
    parsed = MRTD.mrz_parser(*lines)
    assert parsed["country_code"] == country_code


@pytest.mark.parametrize("doc_type", ["P", "ID", "PP"])
def test_viz_encoder_document_types(doc_type):
    # Document type field supports both single and double character codes
    data = make_data(document_type=doc_type)
    lines = MRTD.viz_encoder(data)
    parsed = MRTD.mrz_parser(*lines)
    assert parsed["document_type"] == doc_type


@pytest.mark.parametrize("gender", ["M", "F", "X", "<", "O"])
def test_viz_encoder_gender_values(gender):
    # Gender field should be returned exactly as supplied
    data = make_data(gender=gender)
    lines = MRTD.viz_encoder(data)
    parsed = MRTD.mrz_parser(*lines)
    assert parsed["gender"] == gender


@pytest.mark.parametrize("personal_number", ["", "<", "1234567890"])
def test_viz_encoder_personal_number_valid(personal_number):
    # Personal number should round-trip and remain within ICAO length rules
    data = make_data(personal_number=personal_number)
    lines = MRTD.viz_encoder(data)
    parsed = MRTD.mrz_parser(*lines)
    assert isinstance(parsed["personal_number"], str)
    assert len(parsed["personal_number"]) <= 14


@pytest.mark.parametrize("personal_number", ["A!@#<>"])
def test_viz_encoder_personal_number_invalid(personal_number):
    # Invalid characters should trigger a downstream checksum failure
    data = make_data(personal_number=personal_number)
    lines = MRTD.viz_encoder(data)
    with pytest.raises(ValueError):
        MRTD.mrz_parser(*lines)
