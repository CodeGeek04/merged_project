import speech_recognition as sr
from interpreter.interpreter import Interpreter
import json
import pyttsx3
import wave
import audioop
import pyaudio
import requests, os

elevenlabs_key = 'ELEVENLABS_KEY'
voice_id = '21m00Tcm4TlvDq8ikWAM'

interpreter = Interpreter(auto_run = True, debug_mode = False)

from playsound import playsound

def speak(text):
    # Convert text to speech and get the audio URL
    tts_audio_url = text_to_speech(text)
    
    # Convert the URL to a local file path
    audio_file_path = os.path.join('static', tts_audio_url.lstrip('/'))
    
    # Save a copy as response.mp3
    import shutil
    shutil.copy(audio_file_path, 'response.mp3')
    
    # Play the audio
    playsound('response.mp3')


def text_to_speech(text):
    api_url = 'https://api.elevenlabs.io/v1/text-to-speech/' + voice_id
    headers = {
        'accept': 'audio/mpeg',
        'xi-api-key': elevenlabs_key,
        'Content-Type': 'application/json'
    }
    payload = {
        'text': text,
        'voice_settings': {
            'stability': '.6',
            'similarity_boost': 0
        }
    }
    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 200:
        file_name = f"tts_{hash(text)}.mp3"
        audio_directory = 'static/audio'
        os.makedirs(audio_directory, exist_ok=True)
        audio_path = os.path.join(audio_directory, file_name)

        with open(audio_path, 'wb') as f:
            f.write(response.content)

        tts_audio_url = f"/audio/{file_name}"
        return tts_audio_url
    else:
        print("Eleven Labs TTS API response:", response.json())
        raise Exception(f"Eleven Labs TTS API request failed with status code: {response.status_code}")

def speak_last_content(response):
    # Reverse iterate through the response to find the last assistant content
    for item in reversed(response):
        if item["role"] == "assistant" and item["content"]:
            speak(item["content"])
            break

def listen_microphone():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    try:
        print("Recognizing...")
        text = r.recognize_google(audio)
        # text = "MAKE A FILE HELLO WORLD.PY"
        print(f"Text: {text}")
        resp = interpreter.chat(str(text), return_messages = True)
        speak_last_content(resp)
        with open('response.txt', 'w') as f:
            f.write(json.dumps(resp))
        
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Error: {e}")

while True:
    listen_microphone()