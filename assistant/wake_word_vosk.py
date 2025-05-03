# pibot/assistant/wake_word_vosk.py

import os
import queue
import sounddevice as sd
import vosk
import json
import logging

class VoskWakeWordDetector:
    def __init__(self, wake_phrases, model_path="models/vosk", sample_rate=16000):
        self.sample_rate = sample_rate
        self.wake_phrases = [phrase.lower() for phrase in wake_phrases]
        self.q = queue.Queue()

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Vosk model not found at {model_path}")

        logging.info("🧠 Loading Vosk model...")
        self.model = vosk.Model(model_path)

    def _callback(self, indata, frames, time, status):
        if status:
            logging.warning(f"Vosk status: {status}")
        self.q.put(bytes(indata))

    def listen(self):
        logging.info("👂 VoskWakeWordDetector: Listening for wake word...")
        with sd.RawInputStream(samplerate=self.sample_rate, blocksize=8000, dtype="int16",
                               channels=1, callback=self._callback):
            rec = vosk.KaldiRecognizer(self.model, self.sample_rate)

            while True:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").lower()
                    logging.debug(f"🔍 Heard: {text}")

                    for phrase in self.wake_phrases:
                        if phrase in text:
                            logging.info(f"🛎️ Wake phrase detected: {phrase}")
                            return  # Wake word matched
    def close(self):
        pass    