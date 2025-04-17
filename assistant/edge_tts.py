# pibot/assistant/edge_tts.py

import asyncio
import edge_tts
import logging
import os
import pygame

class EdgeSpeaker:
    """
    Uses Microsoft Edge TTS with SSML styles for tone.
    """

    def __init__(self, voice="en-US-JennyNeural", style="default", output_path="output/reply.mp3"):
        self.voice = voice
        self.style = style
        self.output_path = output_path
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    async def _speak_async(self, text):
        # if self.style == "default":
        #     ssml_text = text
        # else:
        #     ssml_text = (
        #         f'<speak version="1.0" xml:lang="en-US">'
        #         f'<voice name="{self.voice}">'
        #         f'<prosody rate="medium">'
        #         f'<mstts:express-as style="{self.style}">{text}</mstts:express-as>'
        #         f'</prosody>'
        #         f'</voice></speak>'
        #     )
        ssml_text = text
        communicate = edge_tts.Communicate(ssml_text, self.voice)
        await communicate.save(self.output_path)

    def speak(self, text):
        logging.info(f"🎤 Speaking with Edge TTS: {text}")
        asyncio.run(self._speak_async(text))

        # Play the audio using pygame
        pygame.mixer.init()
        pygame.mixer.music.load(self.output_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.music.unload()
        pygame.mixer.quit()



# Style | Example voice
# cheerful | en-US-JennyNeural
# sad | en-US-JennyNeural
# angry | zh-CN-XiaoxiaoNeural
# narration | en-GB-RyanNeural
# whispering | zh-CN-XiaoxiaoNeural