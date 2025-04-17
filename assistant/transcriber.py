# pibot/assistant/transcriber.py

from faster_whisper import WhisperModel
import logging
import os

class Transcriber:
    """
    Transcribes speech from an audio file to text using Whisper.
    """

    def __init__(self, model_size="base", compute_type="auto"):
        """
        Initializes the Whisper model.
        :param model_size: Choose from "tiny", "base", "small", "medium", "large"
        :param compute_type: "auto", "int8", or "float16" (depends on your hardware)
        """
        logging.info("🔠 Loading Whisper model (CPU-only)...")
        self.model = WhisperModel(model_size, device="cpu", compute_type=compute_type)
        logging.info("✅ Whisper model ready.")

    def transcribe(self, audio_path):
        """
        Transcribes the audio at the given path.
        :param audio_path: Path to the .wav file
        :return: Detected language and transcription text
        """
        logging.info(f"🔍 Transcribing audio: {audio_path}")

        segments, info = self.model.transcribe(audio_path, beam_size=5)

        result_text = ""
        for segment in segments:
            result_text += segment.text + " "

        language = info.language
        logging.info(f"🈶 Language: {language}")
        logging.info(f"📝 Transcript: {result_text.strip()}")

        return language, result_text.strip(),info
