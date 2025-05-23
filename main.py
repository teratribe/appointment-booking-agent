from fastapi import FastAPI, Request
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv
import os
import openai
import requests

load_dotenv()
app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/voice")
async def voice_response(request: Request):
    response = VoiceResponse()
    response.say("Hello! Please tell me what you’d like to do.")
    response.record(
        action="/process_audio",
        max_length=15,
        transcribe=False,
        play_beep=True
    )
    return str(response)

@app.post("/process_audio")
async def process_audio(request: Request):
    form = await request.form()
    recording_url = form["RecordingUrl"]

    audio_response = requests.get(recording_url + ".mp3")
    with open("audio.mp3", "wb") as f:
        f.write(audio_response.content)

    audio_file = open("audio.mp3", "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    prompt = f"The user said: '{transcript['text']}'. What appointment do they want to book?"
    gpt_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a friendly appointment booking agent."},
            {"role": "user", "content": prompt}
        ]
    )
    reply_text = gpt_response['choices'][0]['message']['content']

    response = VoiceResponse()
    response.say(reply_text)
    return str(response)
