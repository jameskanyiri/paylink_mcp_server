import pytest
from src.servers.mpesa.core.mpesa_express.stk_push import initiate_stk_push

# Dummy data for valid inputs, actual values don't matter for validation tests
# as long as they pass the specific validation being tested.
# We are not testing a successful API call here.
ACCESS_TOKEN = "dummy_access_token"
VALID_PHONE_NUMBER = "254700000000"
VALID_AMOUNT = 10
VALID_ACCOUNT_REFERENCE = "TestAcc"
VALID_TRANSACTION_DESC = "TestDesc"
VALID_TRANSACTION_TYPE = "CustomerPayBillOnline"


@pytest.mark.asyncio
async def test_invalid_phone_number_too_short():
    response = await initiate_stk_push(
        access_token=ACCESS_TOKEN,
        phone_number="25470000000",  # Too short
        amount=VALID_AMOUNT,
        account_reference=VALID_ACCOUNT_REFERENCE,
        transaction_desc=VALID_TRANSACTION_DESC,
        transaction_type=VALID_TRANSACTION_TYPE,
    )
    assert "error" in response
    assert response["error"] == "Invalid phone number format. Must be 254XXXXXXXXX"


@pytest.mark.asyncio
async def test_invalid_phone_number_bad_prefix():
    response = await initiate_stk_push(
        access_token=ACCESS_TOKEN,
        phone_number="070000000000",  # Doesn't start with 254
        amount=VALID_AMOUNT,
        account_reference=VALID_ACCOUNT_REFERENCE,
        transaction_desc=VALID_TRANSACTION_DESC,
        transaction_type=VALID_TRANSACTION_TYPE,
    )
    assert "error" in response
    assert response["error"] == "Invalid phone number format. Must be 254XXXXXXXXX"


@pytest.mark.asyncio
async def test_valid_phone_number_does_not_error_immediately():
    # This test only checks that the phone number validation itself passes.
    # It doesn't mock os.getenv, so it might fail on "Missing M-Pesa STK environment variables"
    # which is acceptable for this specific, simplified validation test.
    response = await initiate_stk_push(
        access_token=ACCESS_TOKEN,
        phone_number=VALID_PHONE_NUMBER,
        amount=VALID_AMOUNT,
        account_reference=VALID_ACCOUNT_REFERENCE,
        transaction_desc=VALID_TRANSACTION_DESC,
        transaction_type=VALID_TRANSACTION_TYPE,
    )
    if "error" in response:
        assert response["error"] != "Invalid phone number format. Must be 254XXXXXXXXX"
    # If no error, or a different error (like missing env vars), it passes this specific check.


@pytest.mark.asyncio
async def test_account_reference_too_long():
    response = await initiate_stk_push(
        access_token=ACCESS_TOKEN,
        phone_number=VALID_PHONE_NUMBER,
        amount=VALID_AMOUNT,
        account_reference="ThisIsWayTooLongAccountReference",  # Too long
        transaction_desc=VALID_TRANSACTION_DESC,
        transaction_type=VALID_TRANSACTION_TYPE,
    )
    assert "error" in response
    assert response["error"] == "Account reference must be ≤ 12 characters"


@pytest.mark.asyncio
async def test_valid_account_reference_does_not_error_immediately():
    response = await initiate_stk_push(
        access_token=ACCESS_TOKEN,
        phone_number=VALID_PHONE_NUMBER,
        amount=VALID_AMOUNT,
        account_reference=VALID_ACCOUNT_REFERENCE, # Valid
        transaction_desc=VALID_TRANSACTION_DESC,
        transaction_type=VALID_TRANSACTION_TYPE,
    )
    if "error" in response:
        assert response["error"] != "Account reference must be ≤ 12 characters"


@pytest.mark.asyncio
async def test_transaction_desc_too_long():
    response = await initiate_stk_push(
        access_token=ACCESS_TOKEN,
        phone_number=VALID_PHONE_NUMBER,
        amount=VALID_AMOUNT,
        account_reference=VALID_ACCOUNT_REFERENCE,
        transaction_desc="ThisIsWayTooLongTransactionDescription",  # Too long
        transaction_type=VALID_TRANSACTION_TYPE,
    )
    assert "error" in response
    assert response["error"] == "Transaction description must be ≤ 13 characters"


@pytest.mark.asyncio
async def test_valid_transaction_desc_does_not_error_immediately():
    response = await initiate_stk_push(
        access_token=ACCESS_TOKEN,
        phone_number=VALID_PHONE_NUMBER,
        amount=VALID_AMOUNT,
        account_reference=VALID_ACCOUNT_REFERENCE,
        transaction_desc=VALID_TRANSACTION_DESC, # Valid
        transaction_type=VALID_TRANSACTION_TYPE,
    )
    if "error" in response:
        assert response["error"] != "Transaction description must be ≤ 13 characters"


@pytest.mark.asyncio
async def test_invalid_transaction_type():
    response = await initiate_stk_push(
        access_token=ACCESS_TOKEN,
        phone_number=VALID_PHONE_NUMBER,
        amount=VALID_AMOUNT,
        account_reference=VALID_ACCOUNT_REFERENCE,
        transaction_desc=VALID_TRANSACTION_DESC,
        transaction_type="InvalidType",  # Invalid
    )
    assert "error" in response
    assert "Invalid transaction type" in response["error"]


@pytest.mark.asyncio
async def test_valid_transaction_type_does_not_error_immediately():
    response = await initiate_stk_push(
        access_token=ACCESS_TOKEN,
        phone_number=VALID_PHONE_NUMBER,
        amount=VALID_AMOUNT,
        account_reference=VALID_ACCOUNT_REFERENCE,
        transaction_desc=VALID_TRANSACTION_DESC,
        transaction_type=VALID_TRANSACTION_TYPE, # Valid
    )
    if "error" in response:
        assert "Invalid transaction type" not in response["error"]

# Note: The "valid" tests are simplified. A full valid test would require mocking
# os.getenv and the httpx.AsyncClient call to avoid actual HTTP requests and
# dependency on environment variables. For this subtask, we're only checking
# that specific input validation passes, not that the whole function succeeds.
# The function will likely return "Missing M-Pesa STK environment variables"
# for the "valid" cases if env vars are not set in the test environment,
# which is fine for these specific tests.
