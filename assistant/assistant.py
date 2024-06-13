import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Load the OpenAI key
api_key = os.getenv("OPENAI_KEY")

class Assistant:
    def __init__(self):
        # OpenAI Client
        self.client = OpenAI(api_key=api_key)
        
        # Array that will hold the history of messages
        self.messages = []
        
        # Set the system prompt and append it to the message
        system_prompt = """
        You are an AI assistant specialized in Nike Air Jordan products. Your goal is to provide helpful and accurate information to users about Air Jordans. Here's how you should act:
        Your role is to assist users in navigating the world of Nike Air Jordan products with ease and confidence. Stay knowledgeable, responsive, and friendly in all interactions.
        """

        # Add the system prompt to the messages
        self.messages.append({"role": "system", "content": system_prompt})
    
    
    def add_user_message(self, message):
        self.messages.append({"role": "user", "content": message})
        
    def stream_response(self, message):
        # Add user message
        self.add_user_message(message)
        
        # Start the streaming completion
        stream = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            stream=True,  # Set stream to True to receive messages in chunks
            messages=self.messages,
        )

        # Iterate over the messages as they are streamed
        print("\n")
        print("Air Jordans AI Assistant: ")
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")

