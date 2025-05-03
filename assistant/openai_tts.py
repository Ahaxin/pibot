# pibot/assistant/openai_tts.py

import openai
import tempfile
import os
import pygame
import logging
from config import OPENAI_API_KEY
import time

class OpenAITTS:
    def __init__(self, voice="alloy"):
        self.voice = voice
        openai.api_key = OPENAI_API_KEY

    def speak(self, text):
        logging.info(f"🗣️ Speaking with OpenAI TTS (voice: {self.voice}): {text}")

        response = openai.audio.speech.create(
            model="tts-1-hd",
            voice=self.voice,
            input=text
        )

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tmpfile.write(response.read())
            tmpfile_path = tmpfile.name

        # Play it with pygame
        pygame.mixer.init()
        pygame.mixer.music.load(tmpfile_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue

        for _ in range(5):
            try:
                os.remove(tmpfile_path)
                break
            except PermissionError:
                time.sleep(0.2)
