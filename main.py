from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from daraja import trigger_stk_push, DarajaAPIError
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PaymentRequest(BaseModel):
    msisdn: str
    amount: int

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    return """
    <html>
        <head>
            <title>Natujenge Daraja API 💸⚡</title>
        </head>
        <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
            <h1>Hello there! 🙋🏽‍♂️🙋🏽‍♀️</h1>
            <p>Welcome to the STK Push API powered by FastAPI.</p>
            <p>Need to send money? Hit up <code>/stkpush</code> with your payload.</p>
        </body>
    </html>
    """

@app.post("/stkpush")
async def stk_push(data: PaymentRequest):
    try:
        response = await trigger_stk_push(data.msisdn, data.amount)
        return response
    except DarajaAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
