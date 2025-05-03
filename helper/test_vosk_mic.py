# test_vosk_mic.py

import sounddevice as sd
import vosk
import sys
import queue
import json

q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

print("🧠 Loading model...")
model = vosk.Model("../models/vosk")
samplerate = 16000

print("🎙️ Listening...")
with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    rec = vosk.KaldiRecognizer(model, samplerate)
    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            print("🗣️ Result:", result.get("text", ""))
