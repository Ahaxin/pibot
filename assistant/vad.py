# pibot/assistant/vad.py

import webrtcvad
import pyaudio
import logging
import collections
import time

class VADListener:
    def __init__(self, aggressiveness=2):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = 16000
        self.frame_duration_ms = 30
        self.frame_size = int(self.sample_rate * self.frame_duration_ms / 1000)  # samples
        self.frame_bytes = self.frame_size * 2  # 2 bytes per sample (16-bit)
        self.audio = pyaudio.PyAudio()

    def wait_for_voice(self, timeout=10):
        logging.info("🎧 Waiting for real speech...")
        stream = self.audio.open(format=pyaudio.paInt16,
                                 channels=1,
                                 rate=self.sample_rate,
                                 input=True,
                                 frames_per_buffer=self.frame_size)

        ring_buffer = collections.deque(maxlen=10)
        triggered = False
        start_time = time.time()

        try:
            while time.time() - start_time < timeout:
                frame = stream.read(self.frame_size, exception_on_overflow=False)

                if len(frame) != self.frame_bytes:
                    logging.warning("⚠️ Invalid frame length")
                    continue

                is_speech = self.vad.is_speech(frame, self.sample_rate)
                ring_buffer.append(is_speech)

                if sum(ring_buffer) > 6:
                    logging.info("🗣️ Voice detected. Begin recording...")
                    return True
        except Exception as e:
            logging.error(f"💥 VAD error: {e}")
        finally:
            stream.stop_stream()
            stream.close()

        logging.info("⏱️ No voice detected within timeout.")
        return False
