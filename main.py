from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from openai_utils import get_response


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message")
    resp_id = data.get("resp_id")
    print(f"Mensaje recibido del frontend: {user_input}")
    response_text, resp_id = get_response(user_input, resp_id)
    return JSONResponse(content={"response": response_text, "response_id": resp_id})

