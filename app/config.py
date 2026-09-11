import os
import sys
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
response_format = {
    "type": "json_object"
}
my_api_key = os.getenv("GROQ_API_KEY")
if not my_api_key:
    raise ValueError(
        "GROQ_API_KEY is not set. Please create a .env file with GROQ_API_KEY=your_key "
        "or set the environment variable."
    )

client = Groq(api_key=my_api_key)
model="openai/gpt-oss-120b"
