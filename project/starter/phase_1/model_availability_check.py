from workflow_agents.base_agents import OPENAI_BASE_URL, CHAT_MODEL
from openai import OpenAI, APIStatusError
from datetime import datetime, timezone
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise SystemExit("OPENAI_API_KEY is not set; add it to the .env file.")

# Evidence for the CHAT_MODEL substitution in base_agents.py: send the same minimal chat
# request, through the same endpoint and key the agents use, to the model the project
# specifies and to the replacement, and record the HTTP request and response for each.
client = OpenAI(base_url=OPENAI_BASE_URL, api_key=openai_api_key)
messages = [{"role": "user", "content": "Reply with the single word OK."}]

print(f"Run at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
print(f"Endpoint: {OPENAI_BASE_URL}")
print(f"API key: {openai_api_key[:6]}...{openai_api_key[-4:]} (masked)")

for model in ["gpt-3.5-turbo", CHAT_MODEL]:
    print(f"\n=== {model} ===")
    try:
        raw = client.chat.completions.with_raw_response.create(
            model=model, messages=messages, temperature=0
        )
        request, completion = raw.http_request, raw.parse()
        print(f"Request: {request.method} {request.url}")
        print(f"Request body: {request.content.decode()}")
        print(f"Response: HTTP {raw.status_code}")
        print(f"Model that answered: {completion.model}")
        print(f"Reply: {completion.choices[0].message.content}")
    except APIStatusError as e:
        request = e.response.request
        print(f"Request: {request.method} {request.url}")
        print(f"Request body: {request.content.decode()}")
        print(f"Response: HTTP {e.status_code}")
        print(f"Response body: {json.dumps(e.response.json(), indent=2)}")
