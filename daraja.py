import httpx, base64
import time
from datetime import datetime
from os import getenv
from dotenv import load_dotenv

load_dotenv()

SHORTCODE = getenv("DARAJA_SHORTCODE")
PASSKEY = getenv("DARAJA_PASSKEY")
CONSUMER_KEY = getenv("DARAJA_CONSUMER_KEY")
CONSUMER_SECRET = getenv("DARAJA_CONSUMER_SECRET")
CALLBACK_URL = getenv("DARAJA_CALLBACK_URL")
ENDPOINT = getenv("AUTH_ENDPOINT")

token_cache = {
    "access_token": None,
    "expires_at": 0
}

async def get_token():
    current_time = time.time()
    
    # if token is still valid, use it
    if token_cache["access_token"] and current_time < token_cache["expires_at"]:
        print(token_cache["access_token"])
        return token_cache["access_token"]
    
    # get a new token if it's invalid
    async with httpx.AsyncClient() as client:
        res = await client.get(
            ENDPOINT,
            auth=(CONSUMER_KEY,CONSUMER_SECRET)
        )
        res_data = res.json()
        access_token = res_data["access_token"]
        expires_in = res_data.get("expires_in", 3599)
        
        # save token and expiry
        token_cache["access_token"] = access_token
        token_cache["expires_at"] = current_time + expires_in - 60
        
        print(access_token)
        return access_token

async def trigger_stk_push(msisdn: str, amount: int):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((SHORTCODE + PASSKEY + timestamp).encode()).decode()
    token = await get_token()
    
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
        "TransactionDesc": "Family Biz"
        }
    
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            headers=headers,
            json=payload
        )
        return response.json()