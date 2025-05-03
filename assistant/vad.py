# pibot/assistant/vad.py

import webrtcvad
import pyaudio
import logging
import collections
import time
import wave

class VADListener:
    def __init__(self, aggressiveness=1):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = 16000
        self.frame_duration_ms = 30
        self.frame_size = int(self.sample_rate * self.frame_duration_ms / 1000)  # samples
        self.frame_bytes = self.frame_size * 2  # 2 bytes per sample (16-bit)
        self.audio = pyaudio.PyAudio()

    # debug function    
    def save_prebuffer_as_wav(self, prebuffer, path="output/prebuffer.wav", sample_rate=16000):
        with wave.open(path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # paInt16 = 2 bytes
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(prebuffer))

    def wait_for_voice(self, timeout=10):
        logging.info("🎧 Waiting for real speech...")
        stream = self.audio.open(format=pyaudio.paInt16,
                                 channels=1,
                                 rate=self.sample_rate,
                                 input=True,
                                 frames_per_buffer=self.frame_size)


        triggered = False
        start_time = time.time()
        prebuffer = collections.deque(maxlen=10)  # store 300ms of audio
        try:
            while time.time() - start_time < timeout:
                frame = stream.read(self.frame_size, exception_on_overflow=False)
                prebuffer.append(frame)

                if len(frame) != self.frame_bytes:
                    logging.warning("⚠️ Invalid frame length")
                    continue

                is_speech = self.vad.is_speech(frame, self.sample_rate)

                if (is_speech ):
                    logging.info("🗣️ Voice detected. Begin recording...")
                    #self.save_prebuffer_as_wav(prebuffer, "output/prebuffer.wav", self.sample_rate)
                    return list(prebuffer)

        except Exception as e:
            logging.error(f"💥 VAD error: {e}")
        finally:
            stream.stop_stream()
            stream.close()

        logging.info("⏱️ No voice detected within timeout.")
        return False
