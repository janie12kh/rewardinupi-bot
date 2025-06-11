import requests
from config import RAZORPAYX_AUTH, RAZORPAYX_ACCOUNT

def send_upi_payout(upi_id, amount, user_ref):
    url = "https://api.razorpay.com/v1/payouts"
    payload = {
        "account_number": RAZORPAYX_ACCOUNT,
        "fund_account": {
            "account_type": "vpa",
            "vpa": {"address": upi_id},
            "contact": {
                "name": user_ref,
                "type": "employee",
                "reference_id": user_ref,
                "email": f"{user_ref}@example.com"
            }
        },
        "amount": amount * 100,
        "currency": "INR",
        "mode": "UPI",
        "purpose": "payout",
        "queue_if_low_balance": True,
        "reference_id": user_ref,
        "narration": "RewardINUPI Bot Payout"
    }
    response = requests.post(url, auth=RAZORPAYX_AUTH, json=payload)
    return response.json()
