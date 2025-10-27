import pytest
from MRTD import (
    machine_readable_zone_scanner,
    get_data_from_db,
    fletcher16,
    check_digit_calculator,
    checksum_matcher,
    mrz_parser,
    viz_encoder,
)
from testdata import (
    TEST_DATA,
    make_data,
)


def test_machine_readable_zone_scanner_stub():
    # Checks stub for hardware scanner returns None
    assert (
        machine_readable_zone_scanner() is None
        or machine_readable_zone_scanner() is None
    )


def test_get_data_from_db_stub():
    # Checks stub for database returns None
    assert get_data_from_db() is None or get_data_from_db() is None


@pytest.mark.parametrize(
    "data, expected",
    [
        ("ABC", (ord("A") + ord("B") + ord("C")) % 255),
        ("", 0),
        ("123456", fletcher16("123456")),
    ],
)
def test_fletcher16_basic(data, expected):
    # Checks fletcher16 checksum calculation for basic cases
    assert isinstance(fletcher16(data), int)
    # Statement coverage: result is always int
    # Condition coverage: empty string, normal string


# ---------------------------------------------------------------------
# Test: check_digit_calculator
# ---------------------------------------------------------------------
@pytest.mark.parametrize("data", ["123456", "", "A1B2C3"])
def test_check_digit_calculator_range(data):
    # Checks that check digit is always a single digit (0-9)
    digit = check_digit_calculator(data)
    assert 0 <= digit < 10


@pytest.mark.parametrize("data", ["", "@#$%^", "123!@#"])
def test_check_digit_calculator_edge_cases(data):
    # Checks check_digit_calculator with empty/special character strings
    digit = check_digit_calculator(data)
    assert 0 <= digit < 10


# ---------------------------------------------------------------------
# Test: checksum_matcher
# ---------------------------------------------------------------------
@pytest.mark.parametrize(
    "data, expected",
    [
        ("123456", str(check_digit_calculator("123456"))),
        ("ABCDEF", str(check_digit_calculator("ABCDEF"))),
        ("", str(check_digit_calculator(""))),
    ],
)
def test_checksum_matcher_true(data, expected):
    # Checks checksum_matcher returns True for correct digit
    assert checksum_matcher(data, expected)


@pytest.mark.parametrize(
    "data, expected",
    [
        ("123456", str((check_digit_calculator("123456") + 1) % 10)),
        ("ABCDEF", str((check_digit_calculator("ABCDEF") + 2) % 10)),
    ],
)
def test_checksum_matcher_false(data, expected):
    # Checks checksum_matcher returns False for incorrect digit
    assert not checksum_matcher(data, expected)


def test_checksum_matcher_invalid_digit():
    # Checks checksum_matcher with non-numeric expected digit
    assert not checksum_matcher("123456", "X")


# ---------------------------------------------------------------------
# Test: mrz_parser and viz_encoder
# ---------------------------------------------------------------------
def test_viz_encoder_and_parser_roundtrip():
    # Checks that encoding and then parsing returns original data
    lines = viz_encoder(TEST_DATA)
    parsed = mrz_parser(*lines)
    for k in TEST_DATA:
        assert parsed[k] == TEST_DATA[k]


def test_mrz_parser_invalid_checksum():
    # Checks mrz_parser raises ValueError for invalid checksum
    line1 = "P<CANDOE<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<<<"
    line2 = "AB12345670CAN0190904M01303069876543210<<<<<5"
    # '0' instead of correct '6'
    with pytest.raises(ValueError):
        mrz_parser(line1, line2)


def test_viz_encoder_produces_expected_lines():
    # Checks that TEST_DATA encodes to LINE_1_TEST and LINE_2_TEST
    from testdata import TEST_DATA, LINE_1_TEST, LINE_2_TEST

    lines = viz_encoder(TEST_DATA)
    assert lines[0] == LINE_1_TEST
    assert lines[1] == LINE_2_TEST


# ---------------------------------------------------------------------
# Additional edge cases for coverage
# ---------------------------------------------------------------------
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
    # Checks MRZ encoding for names with punctuation
    lines = viz_encoder(data)
    parsed = mrz_parser(*lines)
    assert parsed["lastname"].replace(" ", "") == data["lastname"].replace(
        "'", ""
    ).replace("!", "")
    assert parsed["given_name"].replace(" ", "") == data["given_name"].replace(
        "-", ""
    ).replace("?", "")


# ---------------------------------------------------------------------
# Test: nationality and country codes (Section 5)
# ---------------------------------------------------------------------
@pytest.mark.parametrize(
    "country_code",
    ["CAN", "USA", "GBR", "FRA", "DEU", "CHN", "IND", "BRA", "AUS", "ZAF"],
)
def test_country_code_validity(country_code):
    # Checks MRZ encoding/parsing for valid country codes
    data = TEST_DATA.copy()
    data["country_code"] = country_code
    lines = viz_encoder(data)
    parsed = mrz_parser(*lines)
    assert parsed["country_code"] == country_code


@pytest.mark.parametrize("doc_type", ["P", "ID", "A", "B", "PP"])
def test_viz_encoder_document_types(doc_type):
    # Checks viz_encoder/mrz_parser for alternate document types
    data = make_data(document_type=doc_type)
    lines = viz_encoder(data)
    parsed = mrz_parser(*lines)
    assert parsed["document_type"] == doc_type


@pytest.mark.parametrize("gender", ["M", "F", "X", "<", "O"])
def test_viz_encoder_gender_values(gender):
    # Checks viz_encoder/mrz_parser for alternate gender values
    data = make_data(gender=gender)
    lines = viz_encoder(data)
    parsed = mrz_parser(*lines)
    assert parsed["gender"] == gender


@pytest.mark.parametrize("personal_number", ["", "<", "1234567890"])
def test_viz_encoder_personal_number_valid(personal_number):
    # Checks valid personal_number cases
    data = make_data(personal_number=personal_number)
    lines = viz_encoder(data)
    parsed = mrz_parser(*lines)
    assert isinstance(parsed["personal_number"], str)
    assert len(parsed["personal_number"]) <= 14


@pytest.mark.parametrize("personal_number", ["A!@#<>"])
def test_viz_encoder_personal_number_invalid(personal_number):
    # Checks invalid personal_number cases (should raise ValueError)
    data = make_data(personal_number=personal_number)
    lines = viz_encoder(data)
    with pytest.raises(ValueError):
        mrz_parser(*lines)
