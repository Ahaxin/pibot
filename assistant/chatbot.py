# pibot/assistant/chatbot.py

import logging
import openai
from openai import OpenAI
from config import OPENAI_API_KEY

class ChatBot:
    """
    Handles conversation with OpenAI's modern Python SDK (>=1.0.0).
    """

    def __init__(self, system_prompt=None, model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.messages = []

        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})
        logging.info("🤖 ChatBot initialized with new OpenAI SDK.")

    def ask(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        logging.info(f"📨 Sending to OpenAI: {user_input}")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages
            )
            reply = response.choices[0].message.content.strip()
            self.messages.append({"role": "assistant", "content": reply})
            logging.info(f"🧠 GPT Reply: {reply}")
            return reply
        except Exception as e:
            logging.error(f"⚠️ OpenAI error: {e}")
            return "Sorry, I couldn't process that right now."
