import pytest
from MRTD import (
    check_digit_calculator,
    checksum_matcher,
    mrz_parser,
    viz_encoder,
)

# ---------------------------------------------------------------------
# Test Fixtures & Constants
# ---------------------------------------------------------------------

TEST_DATA = {
    "document_type": "P",
    "country_code": "CAN",
    "lastname": "DOE",
    "given_name": "JOHN MICHAEL",
    "passport_number": "AB1234567",
    "nationality": "CAN",
    "date_of_birth": "900101",
    "gender": "M",
    "expiration_date": "300101",
    "personal_number": "9876543210",
}

LINE_1_TEST = "P<CANDOE<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<<<"
LINE_2_TEST = "AB12345676CAN9001010M30010189876543210<<<<<5"

CHECK_DIGIT_CASES = [
    ("AB1234567", "6"),
    ("900101", "0"),
    ("300101", "8"),
    ("9876543210", "5"),
]


# ---------------------------------------------------------------------
# Check Digit Tests
# ---------------------------------------------------------------------

@pytest.mark.parametrize("data, expected", CHECK_DIGIT_CASES)
def test_check_digit_calculator_returns_correct_digit(data, expected):
    """Ensure Fletcher16 % 10 produces the expected single-digit result."""
    check_num = check_digit_calculator(data)
    assert check_num == int(expected), f"Expected {expected}, got {check_num}"
    assert 0 <= check_num < 10, "Check digit should be a single digit (0-9)"


@pytest.mark.parametrize("data, expected", CHECK_DIGIT_CASES)
def test_checksum_matcher_validates_correctly(data, expected):
    """Ensure checksum_matcher correctly identifies valid check digits."""
    assert checksum_matcher(data, expected), f"{data} should match {expected}"
    # Test with an incorrect check digit to ensure it fails properly
    wrong_digit = str((int(expected) + 3) % 10)
    assert not checksum_matcher(data, wrong_digit), f"{data} should fail with {wrong_digit}"


# ---------------------------------------------------------------------
# MRZ Parsing & Encoding Tests
# ---------------------------------------------------------------------

def test_mrz_parser_returns_correct_data():
    """Verify MRZ lines decode into the correct structured dictionary."""
    parsed_data = mrz_parser(LINE_1_TEST, LINE_2_TEST)
    assert parsed_data == TEST_DATA


def test_viz_encoder_roundtrip():
    """Ensure encoding the data recreates the exact MRZ lines."""
    line1, line2 = viz_encoder(TEST_DATA)
    assert line1 == LINE_1_TEST
    assert line2 == LINE_2_TEST


def test_encoder_and_parser_roundtrip_consistency():
    """Test encode -> parse -> compare equality consistency."""
    encoded_lines = viz_encoder(TEST_DATA)
    parsed_data = mrz_parser(*encoded_lines)
    assert parsed_data == TEST_DATA
