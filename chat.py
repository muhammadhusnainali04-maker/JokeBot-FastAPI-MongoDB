from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq

from langchain_core.prompts import ChatPromptTemplate as cpt
from pymongo import MongoClient

from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel



load_dotenv()

api_groq = os.getenv("Groq_Api_key")
uri = os.getenv("MONGO_URI")



api=FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    question: str

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)


client = MongoClient(uri)

db = client['chat_history']
collection = db['users']

prompt= cpt.from_messages(
    [
        ("system","You are a joke bot. Your only purpose is to tell jokes. When a user sends you a message, respond with a relevant, funny joke. Keep jokes clean and appropriate unless told otherwise. If asked something unrelated to jokes, steer the conversation back by responding with a joke about that topic."),
        ("placeholder","{history}"),
        ("user","{question}")
    ]
)


llm = ChatGroq(api_key = api_groq , model="openai/gpt-oss-20b")

chain = prompt | llm

# userid="user123"




def get_history(user_id):
    chats=collection.find({"user_id": user_id}).sort("timestamp", 1)
    history=[]

    for chat in chats:
        history.append((chat['role'],chat["message"]))
    return history



@api.get("/")
def home():
    return {"message": "Welcome to the Joke Bot API!"}


# Add this to your FastAPI backend script
@api.get("/history/{user_id}")
def get_user_history(user_id: str):
    # Fetch history using your existing function
    history_data = get_history(user_id)
    
    # Format it for the frontend (converting tuple to dict)
    formatted_history = []
    for role, message in history_data:
        formatted_history.append({"role": role, "content": message})
        
    return {"history": formatted_history}



@api.post("/chat")
def chat(request: ChatRequest):
    history=get_history(request.user_id)
    res=chain.invoke({"history": history, "question": request.question}) 
    collection.insert_one(
        {
            "user_id": request.user_id,
            "role": "user",
            "message": request.question,
            "timestamp": datetime.utcnow()
        }
    )

    collection.insert_one(
        {
            "user_id": request.user_id,
            "role": "assistant",
            "message": res.content,
            "timestamp": datetime.utcnow()
        }
    )

    return {"response": res.content}





# while True:
#     question=input("Ask a question ")

#     if  question.lower() == "exit":
#         break

#     history=get_history(userid)


#     res=chain.invoke({"history": history, "question": question})

#     collection.insert_one(
#         {
#             "user_id": userid,
#             "role": "user",
#             "message": question,
#             "timestamp": datetime.utcnow()
#         }
#     )

#     collection.insert_one(
#         {
#             "user_id": userid,
#             "role": "assistant",
#             "message": res.content,
#             "timestamp": datetime.utcnow()
#         }
#     )

# # res=chain.invoke("What is the capital of France?")

#     print(res.content)

