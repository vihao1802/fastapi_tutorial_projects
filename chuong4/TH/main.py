from fastapi import FastAPI
from google import genai
from pydantic import BaseModel

client = genai.Client(api_key="AIzaSyCZdBCN6wecR-MjeUFg-0nlUxPOAnCTEPA")

class PromptRequest(BaseModel):
    text: str

app = FastAPI()

def processPrompt(content: str):
    content="Not using markdown for response just plain text. " + content
    response = client.models.generate_content(
        model="gemini-1.5-pro", contents=content
    )
    return response.text

@app.get("/")
def hello():
    return "Hello World";

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
