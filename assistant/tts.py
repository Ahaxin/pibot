# pibot/assistant/tts.py

from gtts import gTTS
import pygame
import logging
import os
import time

class TextToSpeech:
    """
    Convert text to speech and play the result using pygame.
    """

    def __init__(self, language="en", output_path="output/reply.mp3"):
        self.language = language
        self.output_path = output_path
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    def speak(self, text):
        """
        Generate speech using gTTS and play it using pygame.
        """
        logging.info(f"🗣️ Speaking: {text}")
        tts = gTTS(text=text, lang=self.language)
        tts.save(self.output_path)

        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load(self.output_path)
        pygame.mixer.music.play()

        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.quit()
