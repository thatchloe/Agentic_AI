# Test script for DirectPromptAgent class

from workflow_agents.base_agents import DirectPromptAgent, CHAT_MODEL
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load the OpenAI API key from the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the Capital of France?"

direct_agent = DirectPromptAgent(openai_api_key)
direct_agent_response = direct_agent.respond(prompt)

# Print the response from the agent
print(f"Prompt: {prompt}")
print(direct_agent_response)

# Explain the knowledge source used by the agent to generate the response
print(
    f"\nKnowledge source: the DirectPromptAgent sends the prompt to {CHAT_MODEL} as-is, with no "
    "system prompt, persona or extra knowledge, so the answer comes solely from the general "
    "knowledge the LLM learned during training."
)
