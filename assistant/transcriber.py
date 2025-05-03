# pibot/assistant/transcriber.py

import os
import subprocess
import logging
from openai import OpenAI
from config import TRANSCRIBER_MODE,TRANSCRIBE_BACKEND, OPENAI_API_KEY
from langdetect import detect

class Transcriber:
    def __init__(self, backend=TRANSCRIBE_BACKEND, model_size=TRANSCRIBER_MODE, compute_type="int8"):
        self.backend = backend
        self.model_size = model_size
        self.compute_type = compute_type

        if backend == "faster_whisper":
            from faster_whisper import WhisperModel
            logging.info("🧠 Loading faster-whisper model...")
            self.model = WhisperModel(model_size, device="cpu", compute_type=compute_type)

        elif backend == "openai":
            logging.info("🌐 Using OpenAI Whisper API")

        elif backend == "whisper_cpp":
            logging.info("💻 Using whisper.cpp backend")
            self.cpp_binary = "./whisper.cpp/main"
            self.cpp_model_path = "./whisper.cpp/models/ggml-tiny.bin"
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def transcribe(self, audio_path):
        if self.backend == "faster_whisper":
            segments, info = self.model.transcribe(audio_path)
            text = " ".join(segment.text for segment in segments)
            return info.language, text

        elif self.backend == "openai":
            client = OpenAI(api_key=OPENAI_API_KEY)
            with open(audio_path, "rb") as f:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    response_format="verbose_json"
                )

            detected_language = response.language
            text = response.text
            return detected_language, text
        
        elif self.backend == "whisper_cpp":
            logging.info("🧠 Running whisper.cpp...")
            temp_out = "transcript.txt"
            cmd = [
                self.cpp_binary,
                "-m", self.cpp_model_path,
                "-f", audio_path,
                "-nt",
                "-of", temp_out
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL)

            try:
                with open(temp_out + ".txt", "r") as f:
                    lines = f.readlines()
                    if lines:
                        text = lines[-1].strip()
                        try:
                            language = detect(text)
                        except:
                            language = "unknown"
                        return language, text
            except Exception as e:
                logging.error(f"📜 whisper.cpp read failed: {e}")
            return "en", ""

        else:
            return "en", ""
