# pibot/assistant/recorder.py

import pyaudio
import wave
import webrtcvad
import logging
import collections
import time
import os

class VoiceRecorder:
    def __init__(self, output_path="output/audio.wav", sample_rate=16000, max_record_seconds=10, silence_duration=1.5, pre_buffer_ms=300):
        self.output_path = output_path
        self.sample_rate = sample_rate
        self.max_record_seconds = max_record_seconds
        self.silence_duration = silence_duration
        self.frame_duration_ms = 30
        self.frame_size = int(self.sample_rate * self.frame_duration_ms / 1000)
        self.frame_bytes = self.frame_size * 2
        self.vad = webrtcvad.Vad(2)

        # Pre-buffer setup (300ms = 10 frames)
        self.pre_buffer_frames = int(pre_buffer_ms / self.frame_duration_ms)
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    def record(self, prebuffer=None):
        logging.info("🎙️ Starting VAD-based recording with pre-buffer...")

        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=self.sample_rate,
                            input=True,
                            frames_per_buffer=self.frame_size)

        frames = []
        pre_buffer = collections.deque(maxlen=self.pre_buffer_frames)
        silence_start = None
        start_time = time.time()
        triggered = False

        if prebuffer:
                frames.extend(prebuffer)
        try:
            while True:
                frame = stream.read(self.frame_size, exception_on_overflow=False)

                if len(frame) != self.frame_bytes:
                    logging.warning("⚠️ Skipping invalid frame")
                    continue

                is_speech = self.vad.is_speech(frame, self.sample_rate)

                if not triggered:
                    pre_buffer.append(frame)
                    if is_speech:
                        triggered = True
                        frames.extend(pre_buffer)
                        frames.append(frame)
                        silence_start = None
                        logging.info("🎤 Voice detected. Begin recording...")
                else:
                    frames.append(frame)
                    if is_speech:
                        silence_start = None
                    else:
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start > self.silence_duration:
                            logging.info("🛑 Silence detected. Ending recording.")
                            break

                if time.time() - start_time > self.max_record_seconds:
                    logging.info("⏳ Max recording time reached.")
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

        logging.info(f"✅ Audio saved: {self.output_path}")
        return self.output_path
