from openai import OpenAI
import subprocess
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load the OpenAI key
api_key = os.getenv("OPENAI_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Generate speech and save to output.mp3
response = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input="Hello world! This is a streaming test.",
)

# Save the response to a local file
output_file = "lastest_voice_response.mp3"
response.stream_to_file(output_file)

# Play the saved MP3 file using macOS afplay command
try:
    subprocess.run(["afplay", output_file])
except FileNotFoundError:
    print("Error: 'afplay' command not found. Make sure you are using macOS.")
except Exception as e:
    print(f"Error occurred: {e}")