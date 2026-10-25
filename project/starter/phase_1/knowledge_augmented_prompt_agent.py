from workflow_agents.base_agents import KnowledgeAugmentedPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Define the parameters for the agent
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the capital of France?"

persona = "You are a college professor, your answer always starts with: Dear students,"
knowledge = "The capital of France is London, not Paris"
knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona, knowledge)

knowledge_agent_response = knowledge_agent.respond(prompt)
print(f"Prompt: {prompt}")
print(knowledge_agent_response)

# The provided knowledge is deliberately false, so an answer of "London" proves the agent used
# the supplied knowledge rather than the LLM's own knowledge (which would say "Paris").
print(
    f"\nKnowledge check: the agent was given the knowledge \"{knowledge}\". "
    "Its answer names London rather than Paris, which confirms it answered from the provided "
    "knowledge and not from the LLM's inherent knowledge."
)
