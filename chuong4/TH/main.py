from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from pathlib import Path
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_SECRET_KEY")
client = genai.Client(api_key=api_key)

class PromptRequest(BaseModel):
    text: str

app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can specify a list of allowed domains)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Serve static files
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

# routes
@app.get("/")
def root():
    return {
        "message":"Hello World",
        "docs": "http://localhost:8000/docs",
        "home": "http://localhost:8000/home"
    }

# Root endpoint serving index.html
@app.get("/home")
def read_index():
    return FileResponse("static/index.html")

def processPrompt(content: str):
    content="Not using markdown for response just plain text. " + content
    response = client.models.generate_content(
        model="gemini-1.5-pro", contents=content
    )
    return response.text

@app.post("/api/gemini/generate-essay")
async def genEssay():
    content = f"Generate an essay with a random topic for who is preparing for IELTS, TOEIC, or TOEFL writing skills and is being an intermediate level. Add the topic upon the generated essay."
    result = processPrompt(content)
    return {"response": result}


@app.post("/api/gemini")
async def promptAI(prompt: PromptRequest):
    content = f"Check grammar and give the only the improved text for the following text: {prompt.text}"
    result = processPrompt(content)
    return {"response": result}

@app.post("/api/gemini/score-text")
async def scoreText(prompt: PromptRequest):
    content = f"Evaluate the following text based on grammar, vocabulary, coherence, and fluency. Provide an overall score using IELTS (0-9), TOEIC (0-990), and TOEFL (0-120). Also, give brief feedback on areas of improvement. Just give directly the score and small feedback. Text: {prompt}"
    result = processPrompt(content)
    return {"response": result}
