import os
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

load_dotenv()

# --------------------------------------------------
# FastAPI
# --------------------------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # you don't use cookies, so this is not needed
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Gemini client
# --------------------------------------------------

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

# Optional: a second model to try if the first one is rate limited.
# Add GEMINI_FALLBACK_MODEL in Render's Environment tab to use it.
FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL")


# --------------------------------------------------
# Request model
# --------------------------------------------------

class ChatRequest(BaseModel):
    message: str


# --------------------------------------------------
# Original Studio Digital system prompt
# --------------------------------------------------

SYSTEM_PROMPT = """
You are the virtual assistant for Studio Digital.

Studio Digital provides:

* AI product visuals
* Social media content
* Business websites
* Digital project support

Your job is to help visitors understand Studio Digital's services and encourage interested visitors to start a project.

Be friendly, professional, concise, natural, and helpful.

If someone asks about a Studio Digital service, explain it simply and clearly.

If someone wants to work with Studio Digital, start a project, make an enquiry, or speak with someone from the studio, direct them to WhatsApp:

https://wa.me/2348025096250

If you don't understand the visitor's question, or the question is outside the information you have about Studio Digital, do not guess or invent an answer.

Instead, politely tell the visitor that you don't have enough information to answer their question and direct them to Studio Digital's WhatsApp:

"Sorry, I don't have enough information to answer that. You can contact Studio Digital directly on WhatsApp here: https://wa.me/2348025096250"

Do not invent services, prices, testimonials, clients, results, guarantees, or company information that has not been provided.

If you don't know something, say so instead of making it up.
"""


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def is_rate_limit(error: Exception) -> bool:
    """True if the error looks like a Gemini 429 / quota error."""
    return getattr(error, "code", None) == 429 or "429" in str(error)


def generate(model: str, message: str) -> str:
    """Call Gemini once and log how long it took."""
    start = time.time()

    response = client.interactions.create(
        model=model,
        input=f"""
{SYSTEM_PROMPT}

Visitor's message:
{message}
""",
        generation_config={
            # Keep Gemini's reasoning minimal for faster responses
            "thinking_level": "low",

            # Prevent unnecessarily long responses
            "max_output_tokens": 500,
        },
    )

    print(f"Gemini ({model}) took {time.time() - start:.1f} seconds")

    return response.output_text.strip()


# --------------------------------------------------
# Home
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Studio Digital AI Chatbot Backend is running!"
    }


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {
        "status": "online"
    }


# --------------------------------------------------
# Chat
# --------------------------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    models = [MODEL]
    if FALLBACK_MODEL and FALLBACK_MODEL != MODEL:
        models.append(FALLBACK_MODEL)

    rate_limited = False

    for model in models:
        try:
            return {
                "reply": generate(model, message)
            }

        except Exception as error:
            print(f"Gemini error ({model}): {error}")

            if is_rate_limit(error):
                rate_limited = True
                continue  # try the fallback model if there is one

            break  # other errors: no point trying another model

    if rate_limited:
        raise HTTPException(
            status_code=429,
            detail="The assistant is busy right now. Please try again in a minute."
        )

    raise HTTPException(
        status_code=500,
        detail="Unable to generate a response right now."
    )