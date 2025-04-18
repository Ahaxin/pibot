# pibot/main.py (updated)

import logging
import os
from datetime import datetime, timedelta
from config import WAKE_WORDS, USE_CUSTOM_WAKE_WORDS, CUSTOM_WAKE_WORD_PATHS
from config import MIC_DEVICE,TRANSCRIBER_MODE,OPENAI_INIT_PROMPT
from config import STOP_WORDS,TIMEOUT_SECONDS,TTS_MODEL
from config import EDGE_TONE,EDGE_STYLE_MAP
from assistant.wake_word import WakeWordDetector
from assistant.recorder import VoiceRecorder
from assistant.tts import TextToSpeech
from assistant.transcriber import Transcriber
from assistant.chatbot import ChatBot
from assistant.edge_tts import EdgeSpeaker
from assistant.vad import VADListener

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)


def save_conversation_log(transcript):
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = f"logs/convo_{timestamp}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write(transcript)
    logging.info(f"📝 Conversation saved to: {path}")

def is_valid_transcription(text,info):
    """
    Filters out short, vague, or meaningless transcriptions.
    """
    if not text:
        return False

    text = text.strip().lower()

    # Block list of known noise/filler outputs
    blacklist = {"you", "yeah", "uh", "ah", "umm", "hmm", "yo", "hi", "i", "."}
    if text in blacklist:
        return False

    # Too short? (less than 2 words or 10 characters)
    if len(text) < 10 and len(text.split()) < 2:
        return False
    
    # if info.no_speech_prob > 0.5:
    #     return False

    return True

def main():
    """
    Main test loop: detect wake word, greet user, then record voice.
    """
    try:
        # Initialize modules
        if USE_CUSTOM_WAKE_WORDS:
            detector = WakeWordDetector(keyword_paths=CUSTOM_WAKE_WORD_PATHS)
        else:
            detector = WakeWordDetector(keywords=WAKE_WORDS)

        vad = VADListener()

        recorder = VoiceRecorder()
        
        if TTS_MODEL == "EDGE":
            voice, style = EDGE_STYLE_MAP.get(EDGE_TONE, ("en-US-JennyNeural", "default"))
            logging.info(f"✨ Select Edge TTS Model: Vocie = {voice}, Style = {style}")
            tts = EdgeSpeaker(voice=voice, style=style)
        else:
            tts = TextToSpeech(language="en") # Default
            logging.info(f"✨ Select the default TTS model")

        transcriber = Transcriber(model_size=TRANSCRIBER_MODE)  # Can be "tiny" for Pi
        chatbot = ChatBot(system_prompt=OPENAI_INIT_PROMPT)


        while True:
            # Wait for wake word
            # detected_word = detector.listen()
            # logging.info(f"✨ Wake word triggered: {detected_word}")

            # Greet the user
            tts.speak("Yes, what can I help you?")

            full_log = []
            is_conversing = True
            last_activity = datetime.now()

            while is_conversing:

                if not vad.wait_for_voice(timeout=10):
                    tts.speak("I didn't hear anything. Please try again.")
                    continue
                
                # Record voice
                audio_file = recorder.record()
                logging.info(f"🎧 Audio saved to: {audio_file}")

                # 📜 Transcribe
                language, text,info = transcriber.transcribe(audio_file)

                # 🧾 Log results
                logging.info(f"🔠 Detected language: {language}")
                logging.info(f"💬 You said (Transcribed text): {text}")

                # 🛡️ Validate
                if not is_valid_transcription(text,info):
                    logging.info("⚠️ Ignored: Empty or noise-only transcription.")
                    tts.speak("Sorry, I didn't catch that. Please say it again.")
                    continue

                # Add to log
                full_log.append(f"[You]: {text}")

                if any(kw in text.lower() for kw in STOP_WORDS):
                    tts.speak("Goodbye.")
                    is_conversing = False
                    break

                # 🧠 Send to GPT
                reply = chatbot.ask(text)

                # 🗣️ Speak reply (same language as input)
                tts.language = language if language in ["en", "zh", "nl"] else "en"
                tts.speak(reply)

                full_log.append(f"[Bot]: {reply}")
                last_activity = datetime.now()

                # Timeout check
                if datetime.now() - last_activity > timedelta(seconds=TIMEOUT_SECONDS):
                    tts.speak("Session timed out. Waiting for wake word.")
                    is_conversing = False
                    break

            save_conversation_log("\n".join(full_log))
            
    except KeyboardInterrupt:
        logging.info("🛑 Interrupted by user.")
    finally:
        detector.close()
        logging.info("💤 Goodbye, my Queen.")

if __name__ == "__main__":
    main()
