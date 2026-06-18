from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime

from models import Message
from database import Base, engine, get_db

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Chatbot Backend", lifespan=lifespan)

class ChatRequest(BaseModel):
    content: str

class MessageUpdate(BaseModel):
    content: str

class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

    model_config={"from_attributes": True}

class ChatResponse(BaseModel):
    user_message: MessageOut
    bot_message: MessageOut

    
def generate_reply(user_text: str) -> str:
    text = user_text.lower().strip()
    if any(w in text for w in ["안녕", "hello", "hi"]):
        return "안녕하세요! 무엇을 도와드릴까요?"
    if "이름" in text:
        return "저는 간단한 챗봇이에요."
    if "?" in text:
        return "좋은 질문이네요. 아직은 잘 모르겠어요!"
    return f'"{user_text}" 라고 하셨네요. 더 자세히 말씀해 주세요.'


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post('/chat', response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    user_msg = Message(role="user", content=req.content)
    bot_msg = Message(role='assitant', content=generate_reply(user_text=req.content))

    db.add(user_msg)
    db.add(bot_msg)
    await db.commit()
    await db.refresh(user_msg)
    await db.refresh(bot_msg)

    return {"user_message": user_msg, "bot_message": bot_msg}


@app.get("/messages", response_model=list[MessageOut])
async def list_message(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Message).order_by(Message.created_at))
    return result.scalar.all()


@app.get("/message/{message_id}", response_model=MessageOut)
async def get_message(message_id: str, db: AsyncSession = Depends(get_db)):
    msg = await db.get(Message, message_id)
    if msg is None:
        raise HTTPException(status_code=404, detail="메세지를 찾을 수 없습니다.")
    return msg


@app.put("/messages/{message_id}", response_model=MessageOut)
async def update_message(message_id: str, req: MessageUpdate, db: AsyncSession = Depends(get_db)):
    msg = await db.get(Message, message_id)
    if msg is None:
        raise HTTPException(status_code=404, detail="메세지를 찾을 수 없습니다.")
    msg['content'] = req.content
    await db.commmit()
    await db.refresh(msg)
    return msg


@app.delete('/messages/{message_id}')
async def delete_message(message_id: str, db: AsyncSession = Depends(get_db)):
    msg = await db.get(Message, message_id)
    if msg is None:
        raise HTTPException(status_code=404, detail="메세지를 찾을 수 없습니다.")
    await db.delete(msg)
    await db.commit()
    return {"deleted": message_id}