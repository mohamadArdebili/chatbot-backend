from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI
import json

load_dotenv()

app = FastAPI(title="Chat API")

# اضافه کردن CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    stream: bool = True


@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        messages = [{"role": msg.role, "content": msg.content}
                    for msg in request.messages]

        if request.stream:
            return StreamingResponse(
                stream_response(messages),
                media_type="text/event-stream"
            )
        else:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                stream=False
            )
            return {"content": response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def stream_response(messages):
    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"

        yield "data: [DONE]\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@app.get("/", response_class=HTMLResponse)
async def serve_interface():
    with open("interface.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
