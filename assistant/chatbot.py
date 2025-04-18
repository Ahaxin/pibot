from config import AI_PROVIDER,AI_MODEL, OPENAI_API_KEY, OPENROUTER_API_KEY, OPENROUTER_BASE_URL
import openai
import logging
import requests

class ChatBot:
    def __init__(self, system_prompt=None):
        self.model = AI_MODEL
        self.system_prompt = system_prompt
        logging.info(f"✨ Chatbot using {AI_MODEL} from AI Provider {AI_PROVIDER}")
        logging.info(f"✨ AI Init prompt: {system_prompt}")
        self.messages = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    def ask(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        logging.info(f"[CHATBOT] Asking AI....")
        if AI_PROVIDER == "openai":
            openai.api_key = OPENAI_API_KEY
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=self.model,
                messages=self.messages
            )
            reply = response.choices[0].message.content.strip()

        elif AI_PROVIDER == "openrouter":
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://your-app-name",  # optional
                "X-Title": "pibot"
            }
            body = {
                "model": self.model,
                "messages": self.messages
            }
            response = requests.post(OPENROUTER_BASE_URL + "/chat/completions", headers=headers, json=body)
            reply = response.json()["choices"][0]["message"]["content"].strip()

        else:
            reply = "Sorry, no valid model is selected."

        self.messages.append({"role": "assistant", "content": reply})
        logging.info(f"[CHATBOT] AI replies {reply}")
        return reply
