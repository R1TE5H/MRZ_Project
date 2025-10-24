from MRTD import viz_encoder


TEST_DATA = {
    "document_type": "P<",
    "country_code": "CAN",
    "lastname": "DOE",
    "given_name": "JOHN MICHAEL",
    "passport_number": "AB1234567",
    "nationality": "CAN",
    "date_of_birth": "900101", 
    "gender": "M",
    "expiration_date": "300101",
    "personal_number": "9876543210"
}

LINE_1_TEST = "P<<CANDOE<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<<"
LINE_2_TEST = "AB12345676CAN9001010M30010189876543210<<<<<5"