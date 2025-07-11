import httpx, base64, logging, time
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

class DarajaAPIError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

token_cache = {
    "access_token": None,
    "expires_at": 0
}

logging.basicConfig(level=logging.INFO)

async def get_token():
    current_time = time.time()
    
    # if token is still valid, use it
    if token_cache["access_token"] and current_time < token_cache["expires_at"]:
        return token_cache["access_token"]
    
    try:
        # get a new token if it's invalid
       async with httpx.AsyncClient() as client:
           res = await client.get(
               ENDPOINT,
               auth=(CONSUMER_KEY,CONSUMER_SECRET)
           )
           res.raise_for_status() # raise HTTPStatusError if error code is not 2xx
           
           res_data = res.json()
           access_token = res_data["access_token"]
           
           if not access_token:
               raise DarajaAPIError("Missing acess token in response.")
           
           expires_in_string = res_data.get("expires_in", 3599)
           expires_in = float(expires_in_string)
           
           # save token and expiry
           token_cache["access_token"] = access_token
           token_cache["expires_at"] = current_time + (expires_in - 60)
           
           logging.info("Access token successfully obtained.")
           return access_token
       
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error during token request: {e.response.status_code}")
        raise DarajaAPIError(f"Failed to get access token: {e.response.text}", e.response.status_code)
    
    except httpx.RequestError as e:
        logging.error(f"Network error during token request: {e}")
        raise DarajaAPIError("Network error while fetching access token.")

    except Exception as e:
        logging.exception("Unexpected error during token fetching")
        raise DarajaAPIError("Unexpected error during token fetching.")
    
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
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            res_data = response.json()
            
            # Check for Daraja-level errors
            if res_data.get("ResponseCode") != "0":
                error_message = res_data.get("errorMessage") or res_data.get("ResponseDescription")
                raise DarajaAPIError(f"Daraja STK Push error: {error_message}")
            
            logging.info("STK Push initiated successfully.")
            return res_data
        
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error during STK Push: {e.response.status_code}")
        raise DarajaAPIError(f"STK Push HTTP Error: {e.response.text}", e.response.status_code)

    except httpx.RequestError as e:
        logging.error(f"Network error during STK Push: {e}")
        raise DarajaAPIError("Network error during STK Push.")

    except Exception as e:
        logging.exception("Unexpected error during STK Push")
        raise DarajaAPIError("Unexpected error during STK Push.")