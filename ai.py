import json
import os
import re
from collections import deque

import openai


MODELS = ["translate", "chatgpt"]


class ChatHistory:
    def __init__(self, msg_limit):
        self.stack = deque(maxlen=msg_limit)

    def append(self, msg):
        return self.stack.append(msg)

    def get_as_list(self):
        return list(self.stack)


class ChatModel:
    def __init__(self, model):
        assert (
            model in MODELS
        ), f"value attribute to {__class__.__name__} must be one of {MODELS}"
        self.model = model
        self.trigger = f"!{model}"
        self.api = self.get_api()

    def get_api(self):

        if self.model == "chatgpt":
            openai_api_key = os.getenv("OPENAI_API_KEY")
            openai_api_base = (
                os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1"
            )
            openai_model = os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo"
            return OpenAIAPI(
                api_key=openai_api_key, api_base=openai_api_base, model=openai_model
            )
        if self.model == "translate":
            return print("this is the translator")



class OpenAIAPI:
    def __init__(
        self, api_key, api_base, model="gpt-3.5-turbo", max_history=5, max_tokens=1024
    ):
        self.model = model
        self.history = ChatHistory(max_history)
        self.max_tokens = max_tokens
        self.api_key = api_key
        self.api_base = api_base

    async def send(self, text):
        openai.api_key = self.api_key
        openai.api_base = self.api_base

        new_message = {"role": "user", "content": text}
        self.history.append(new_message)
        messages = self.history.get_as_list()

        response = openai.ChatCompletion.create(
            model=self.model, messages=messages, max_tokens=self.max_tokens
        )

        self.history.append(response.choices[0].message)
        response = response.choices[0].message.content
        return response.strip()
