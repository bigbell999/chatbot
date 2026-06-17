from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from datetime import datetime, timezone
from uuid import UUID, uuid4


app = FastAPI(title="Chatbot Backend")
messages: dict[str, dict] = {}

class ChatRequest(BaseModel):
    content: str

class MessageUpdate(BaseModel):
    content: str

def generate_reply(user_text: str) -> str:
    text = user_text.lower().strip()
    if any(w in text for w in ["안녕", "hello", "hi"]):
        return "안녕하세요! 무엇을 도와드릴까요?"
    if "이름" in text:
        return "저는 간단한 챗봇이에요."
    if "?" in text:
        return "좋은 질문이네요. 아직은 잘 모르겠어요!"
    return f'"{user_text}" 라고 하셨네요. 더 자세히 말씀해 주세요.'


def save_message(role: str, content: str) -> dict:
    msg_id = str(uuid4())
    msg = {
        "id": msg_id,
        "role": role,
        "content": content,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    messages[msg_id] = msg
    return msg


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post('/chat')
def chat(req: ChatRequest):
    user_msg = save_message("user", req.content)
    reply = generate_reply(req.content)
    bot_msg = save_message("assistant", reply)
    return {"user_message": user_msg, 
            "bot_message": bot_msg
            }

@app.get("/messages")
def list_message():
    return list(messages.values())

@app.get("/message/{message_id}")
def get_message(message_id: str):
    msg = messages.get(message_id)
    if msg is None:
        raise HTTPException(status_code=404, detail="메세지를 찾을 수 없습니다.")
    
    return msg

@app.put("/messages/{message_id}")
def update_message(message_id: str, req:MessageUpdate):
    msg = messages.get(message_id)
    if msg is None:
        raise HTTPException(status_code=404, detail="메세지를 찾을 수 없습니다.")
    msg['content'] = req.content
    return msg


@app.delete('/messages/{message_id}')
def delete_message(message_id: str):
    if message_id not in messages:
        raise HTTPException(status_code=404, detail="메세지를 찾을 수 없습니다.")
    del messages[message_id]
    return {"deleted": message_id}