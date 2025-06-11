import os
from typing import Dict, Any
from src.tracing.async_trace import async_trace

@async_trace
async def initiate_c2b_payment(
    amount: int,
    account_number: str,
) -> Dict[str, Any]:
    """
    Generates M-Pesa Paybill payment instructions for a customer to pay manually.

    Args:
        amount (int): Amount to be paid in KES.
        account_number (str): Reference number identifying the transaction (e.g., order ID, invoice number).

    Returns:
        Dict[str, Any]: Structured instructions to complete the payment manually via M-Pesa Paybill.
    """
    shortcode = os.getenv("BUSINESS_SHORTCODE") or "601426"

    instructions = (
        f"Go to M-Pesa > Lipa na M-Pesa > Paybill > "
        f"Enter {shortcode} > Account: {account_number} > Amount: {amount}"
    )

    return {
        "shortcode": shortcode,
        "pay_with": "M-Pesa Paybill",
        "paybill_number": shortcode,
        "account_number": account_number,
        "amount": amount,
        "instructions": instructions,
    }
