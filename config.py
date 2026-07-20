import os
from dotenv import load_dotenv
from groq import Groq
load_dotenv()

my_api_key=os.getenv("GROQ_API_KEY")
client=Groq(api_key=my_api_key)

model="llama-3.3-70b-versatile"