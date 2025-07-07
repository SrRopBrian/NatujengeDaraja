import httpx, base64
from datetime import datetime
from os import getenv
from dotenv import load_dotenv

load_dotenv()

SHORTCODE = getenv("DARAJA_SHORTCODE")
PASSKEY = getenv("DARAJA_PASSKEY")
CONSUMER_KEY = getenv("DARAJA_CONSUMER_KEY")
CONSUMER_SECRET = getenv("DARAJA_CONSUMER_SECRET")
CALLBACK_URL = getenv("DARAJA_CALLBACK_URL")

async def get_token():
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
            auth=(CONSUMER_KEY,CONSUMER_SECRET)
        )
        return res.json()["access_token"]

async def trigger_stk_puch(msisdn: str, amount: int):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((SHORTCODE + PASSKEY + timestamp).encode()).decode
    token = await get_token
    
    payload = {
        "BusinessShortCode": SHORTCODE,    
        "Password": password,    
        "Timestamp": timestamp,    
        "TransactionType": "CustomerPayBillOnline",    
        "Amount": amount,    
        "PartyA": msisdn,    
        "PartyB": SHORTCODE,    
        "PhoneNumber": msisdn,    
        "CallBackURL": CALLBACK_URL,    
        "AccountReference": "Rop n Sons",    
        "TransactionDesc": "The Family Business"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            headers=headers,
            json=payload
        )
        return response.json