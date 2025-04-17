import pvporcupine
import pyaudio
import struct
import os
import logging
from config import ACCESS_KEY  

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

class WakeWordDetector:
    """
    Wake word detector using Porcupine.
    Can be initialized with built-in keywords or custom .ppn files.
    """

    def __init__(self, keywords=None, keyword_paths=None):
        """
        Initialize the Porcupine engine and audio stream.
        :param keywords: List of built-in keyword strings (e.g., ["computer", "jarvis"])
        :param keyword_paths: List of paths to custom .ppn files for custom wake words
        """
        if keyword_paths:
            self.porcupine = pvporcupine.create(access_key=ACCESS_KEY, keyword_paths=keyword_paths)
            self.keyword_names = [os.path.basename(kp).replace(".ppn", "") for kp in keyword_paths]
            logging.info(f"Using custom wake words: {self.keyword_names}")
        elif keywords:
            self.porcupine = pvporcupine.create(access_key=ACCESS_KEY,keywords=keywords)
            self.keyword_names = keywords
            logging.info(f"Using built-in wake words: {self.keyword_names}")
        else:
            raise ValueError("You must provide either keywords or keyword_paths.")

        # Set up the audio stream for listening
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )
        logging.info("Audio stream initialized.")

    def listen(self):
        """
        Listen for wake words continuously.
        Returns the name of the detected wake word when triggered.
        """
        logging.info("🎧 Listening for wake words...")

        while True:
            pcm = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            result = self.porcupine.process(pcm)

            if result >= 0:
                detected_word = self.keyword_names[result]
                logging.info(f"👂 Wake word detected: {detected_word}")
                return detected_word

    def close(self):
        """
        Safely close the audio stream and Porcupine engine.
        """
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
        self.porcupine.delete()
        logging.info("Wake word detector closed.")
