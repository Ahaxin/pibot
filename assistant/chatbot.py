from config import AI_PROVIDER,AI_MODEL, AI_API_KEY
import openai
import google.generativeai as genai
import logging
import requests

class ChatBot:
    def __init__(self, system_prompt=None):
        self.model = AI_MODEL
        self.system_prompt = system_prompt
        logging.info(f"✨ Chatbot using {AI_MODEL} from AI Provider {AI_PROVIDER}")
        logging.info(f"✨ AI Init prompt: {system_prompt}")
        if AI_PROVIDER == "gemini":
            genai.configure(api_key=AI_API_KEY)
            self.model = genai.GenerativeModel(AI_MODEL)
            self.chat = self.model.start_chat(history=[
                {"role": "user", "parts": [self.system_prompt]}
            ])
            logging.info("🤖 Gemini chatbot initialized.")
        elif AI_PROVIDER == "openai":    
            logging.info("🤖 OpenAI chatbot initialized.")
        elif AI_PROVIDER == "openrouter":
            from config import OPENROUTER_BASE_URL
            logging.info("🤖 Openrouter chatbot initialized.")
        else:
            raise ValueError(f"Unsupported chatbot engine: {AI_PROVIDER}")
        self.messages = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    def ask(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        logging.info(f"[CHATBOT] Asking AI....")
        if AI_PROVIDER == "openai":
            openai.api_key = AI_API_KEY
            client = openai.OpenAI(api_key=AI_API_KEY)
            response = client.chat.completions.create(
                model=self.model,
                messages=self.messages
            )
            reply = response.choices[0].message.content.strip()

        elif AI_PROVIDER == "openrouter":
            headers = {
                "Authorization": f"Bearer {AI_API_KEY}",
                "HTTP-Referer": "https://your-app-name",  # optional
                "X-Title": "pibot"
            }
            body = {
                "model": self.model,
                "messages": self.messages
            }
            response = requests.post(OPENROUTER_BASE_URL + "/chat/completions", headers=headers, json=body)
            reply = response.json()["choices"][0]["message"]["content"].strip()
        elif AI_PROVIDER == "gemini":
            response = self.chat.send_message(user_input)
            reply = response.text.strip()           
        else:
            reply = "Sorry, no valid model is selected."

        self.messages.append({"role": "assistant", "content": reply})
        logging.info(f"[CHATBOT] AI replies {reply}")
        return reply
