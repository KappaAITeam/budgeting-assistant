# import speech_recognition as sr


# def get_voice_input() -> str:
#     """
#     Captures voice input and returns the transcribed text.
#     """
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("Listening for voice input...")
#         audio = recognizer.listen(source)

#         try:
#             text = recognizer.recognize_google(audio)
#             print(f"Recognized Text: {text}")
#             return text
#         except sr.UnknownValueError:
#             return "Sorry, I could not understand the audio."
#         except sr.RequestError as e:
#             return f"Error with speech recognition service: {str(e)}"

from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from openai import OpenAI
from langchain.prompts import ChatPromptTemplate
# from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from base64 import b64decode
from pathlib import Path
import os

load_dotenv('.env')
openai = OpenAI()
# chat_model = ChatOpenAI(model="gpt-4o")
chat_history = []

app = FastAPI()
templates = Jinja2Templates(directory="templates")

OUTPUT_DIR = Path("./audio_output")
OUTPUT_DIR.mkdir(exist_ok=True)

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert financial Analyst."),
        ("human", "Give financial insight into  the following financial notes:\n\n{user_input}" \
        "Extract financial income from the insight"
        "List financial expenses from the insight"
        "List financial concerns about the financial insight")
    ]
)

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("frontend.html", {"request": request, "audio_url": None, "transcript": None})

@app.websocket("/ws/voice-to-voice")
async def voice_to_voice(websocket: WebSocket):
    print(f"websocket connection attempt from {websocket.client}")
    await websocket.accept()
    try:
        while True:
            # Receive audio data from the frontend
            audio_data = await websocket.receive_bytes()

            # Transcribe the audio
            transcription = openai.audio.transcriptions.create(
                file=("audio.webm", audio_data),
                model="whisper-1"
            )
            transcription_text = transcription.text
            chat_history.append({"role": "user", "content": transcription_text})

            # Generate AI response for both text and audio
            messages = prompt_template.format_messages(
                user_input=transcription_text) + \
            [{"role": role, "content": content} for role, content in [(message['role'], message['content']) for message in chat_history]]
            
            response = openai.chat.completions.create(
                model="gpt-4o-audio-preview",
                modalities=["text", "audio"],
                audio={"voice": "onyx", "format": "wav"},
                messages=[{'role': message['role'], 'content': message['content']} for message in messages]
            )

            # Send AI audio response back
            audio_data = b64decode(response.choices[0].message.audio.data)
            await websocket.send_bytes(audio_data)

            # Send transcript back
            audio_transcript = response.choices[0].message.audio.transcript
            chat_history.append({"role": "assistant", "content": audio_transcript})
            await websocket.send_text(audio_transcript)

    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        await websocket.close()

@app.get("/audio_output/{filename}")
async def get_audio(filename: str):
    audio_path = OUTPUT_DIR / filename
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(
        audio_path,
        media_type="audio/wav",
        headers={"Content-Disposition": "inline"}
    )

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000, ws="auto")