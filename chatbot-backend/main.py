import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = FastAPI()

# Allow the portfolio frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


class ChatRequest(BaseModel):
    message: str


SYSTEM_PROMPT = """
You are the virtual assistant for Studio Digital.

Studio Digital provides:
- AI product visuals
- Social media content
- Business websites
- Digital project support

Your job is to help visitors understand Studio Digital's services
and encourage interested visitors to start a project.

Be friendly, professional, concise and natural.

If someone asks about a service, explain it simply.

If someone wants to work with Studio Digital, tell them they can
contact the studio through WhatsApp.

Do not invent services, prices, testimonials, clients or results
that are not provided.

If you don't know something, say so instead of making it up.
"""


@app.get("/")
def home():
    return {
        "message": "Studio Digital AI Chatbot Backend is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "online"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    prompt = f"""
{SYSTEM_PROMPT}

Visitor's message:
{request.message}
"""

    response = client.interactions.create(
        model=MODEL,
        input=prompt,
    )

    return {
        "reply": response.output_text
    }