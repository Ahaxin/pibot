# pibot/assistant/recorder.py

import pyaudio
import wave
import webrtcvad
import logging
import collections
import time
import os
import struct

class VoiceRecorder:
    def __init__(self, output_path="output/audio.wav", sample_rate=16000, max_record_seconds=10, silence_duration=1.5):
        self.output_path = output_path
        self.sample_rate = sample_rate
        self.max_record_seconds = max_record_seconds
        self.silence_duration = silence_duration

        self.vad = webrtcvad.Vad(2)  # Moderate aggressiveness
        self.frame_duration_ms = 30
        self.frame_size = int(self.sample_rate * self.frame_duration_ms / 1000)  # samples per frame
        self.frame_bytes = self.frame_size * 2  # 2 bytes per sample

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        
    def record(self):
        logging.info("🎙️ VoiceRecorder is listening...")

        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=self.sample_rate,
                            input=True,
                            frames_per_buffer=self.frame_size)

        frames = []
        silence_start_time = None
        start_time = time.time()

        try:
            while True:
                frame = stream.read(self.frame_size, exception_on_overflow=False)

                if len(frame) != self.frame_bytes:
                    logging.warning("⚠️ Skipping invalid frame")
                    continue

                is_speech = self.vad.is_speech(frame, self.sample_rate)
                frames.append(frame)

                if is_speech:
                    silence_start_time = None
                else:
                    if silence_start_time is None:
                        silence_start_time = time.time()
                    elif time.time() - silence_start_time > self.silence_duration:
                        logging.info("🛑 Silence detected. Ending recording.")
                        break

                if time.time() - start_time > self.max_record_seconds:
                    logging.info("⏳ Max recording duration reached.")
                    break
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()

        with wave.open(self.output_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))

        logging.info(f"✅ Audio saved to: {self.output_path}")
        return self.output_path
