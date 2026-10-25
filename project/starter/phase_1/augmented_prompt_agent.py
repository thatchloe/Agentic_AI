from workflow_agents.base_agents import AugmentedPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the capital of France?"
persona = "You are a college professor; your answers always start with: 'Dear students,'"

augmented_agent = AugmentedPromptAgent(openai_api_key, persona)
augmented_agent_response = augmented_agent.respond(prompt)

# Print the agent's response
print(f"Prompt: {prompt}")
print(augmented_agent_response)

# Knowledge used: no knowledge is supplied to this agent, so the answer ("Paris") comes from
# the general knowledge the LLM (CHAT_MODEL, gpt-4o-mini) learned during training, exactly like the DirectPromptAgent.
# Persona impact: the system prompt makes the LLM answer as a college professor, so the reply
# opens with "Dear students," and takes an explanatory, teaching tone. The persona changes the
# style and framing of the answer, not the facts in it.
print(
    "\nKnowledge source: the agent's general LLM knowledge (no knowledge was provided to it)."
    "\nPersona impact: the system prompt made it answer as a college professor, starting with "
    "'Dear students,' in a teaching tone; the persona shaped the style, not the facts."
)
