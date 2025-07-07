from fastapi import FastAPI
from pydantic import BaseModel
from daraja import trigger_stk_push

app = FastAPI()

class PaymentRequest(BaseModel):
    msisdn: str
    amount: int

@app.post("/stkpush")
async def stk_push(data: PaymentRequest):
    response = await trigger_stk_push(data.msisdn, data.amount)
    return response