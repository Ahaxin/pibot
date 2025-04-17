# pibot/assistant/recorder.py

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from config import MIC_INPUT_AMPLIFIER
import logging
import os

class VoiceRecorder:
    """
    Records audio from the microphone and saves it as a WAV file.
    """

    def __init__(self, output_path="output/audio.wav", sample_rate=16000, duration=5,device=None):
        """
        Initialize recorder settings.
        :param output_path: Path where the audio will be saved
        :param sample_rate: Audio sampling rate in Hz
        :param duration: Recording duration in seconds
        """
        self.output_path = output_path
        self.sample_rate = sample_rate
        self.duration = duration
        self.device = device

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        logging.info(f"Voice recorder initialized. Output: {self.output_path}")

    def record(self):
        """
        Records audio and saves it as a WAV file.
        """
        logging.info("🎙️ Recording started... Speak now!")
        audio = sd.rec(int(self.duration * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype=np.int16,device=self.device)
        sd.wait()
        
        # 📈 Amplify the signal (e.g., 2x volume)
        audio = audio * MIC_INPUT_AMPLIFIER  # from config file
        # Prevent clipping: limit to int16 range
        audio = np.clip(audio, -32768, 32767).astype('int16')

        write(self.output_path, self.sample_rate, audio)
        logging.info(f"✅ Recording saved to {self.output_path}")

        return self.output_path
