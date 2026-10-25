# agentic_workflow.py
"""
General-purpose agentic workflow for technical project management.

A TPM-style workflow prompt is broken into steps by an ActionPlanningAgent. Each step is
routed by a RoutingAgent to one of three specialist teams (Product Manager, Program Manager,
Development Engineer). Each team is a KnowledgeAugmentedPromptAgent paired with an
EvaluationAgent that iterates on the worker's answer until it meets the team's format.
The results are assembled into a single project plan for the product spec.
"""

from workflow_agents.base_agents import ActionPlanningAgent, KnowledgeAugmentedPromptAgent, EvaluationAgent, RoutingAgent

import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("agentic_workflow")
# The OpenAI client logs every HTTP request at INFO; keep only its warnings and errors.
logging.getLogger("httpx").setLevel(logging.WARNING)

# Resolve files relative to this script so the workflow can be run from any directory.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load the OpenAI key from the .env file next to this script
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise SystemExit("OPENAI_API_KEY is not set. Add it to phase_2/.env before running the workflow.")

# load the product spec
with open(os.path.join(SCRIPT_DIR, "Product-Spec-Email-Router.txt"), "r", encoding="utf-8") as spec_file:
    product_spec = spec_file.read()

# Maximum refinement rounds each EvaluationAgent may run before accepting the latest answer
MAX_EVALUATION_INTERACTIONS = 10

# Instantiate all the agents

# Action Planning Agent
knowledge_action_planning = (
    "Stories are defined from a product spec by identifying a "
    "persona, an action, and a desired outcome for each story. "
    "Each story represents a specific functionality of the product "
    "described in the specification. \n"
    "Features are defined by grouping related user stories. \n"
    "Tasks are defined for each story and represent the engineering "
    "work required to develop the product. \n"
    "A development Plan for a product contains all these components"
)
action_planning_agent = ActionPlanningAgent(openai_api_key, knowledge_action_planning)

# Product Manager - Knowledge Augmented Prompt Agent
persona_product_manager = "You are a Product Manager, you are responsible for defining the user stories for a product."
knowledge_product_manager = (
    "Stories are defined by writing sentences with a persona, an action, and a desired outcome. "
    "The sentences always start with: As a "
    "Write several stories for the product spec below, where the personas are the different users of the product. "
    f"{product_spec}"
)
product_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona_product_manager, knowledge_product_manager)

# Product Manager - Evaluation Agent
persona_product_manager_eval = "You are an evaluation agent that checks the answers of other worker agents"
evaluation_criteria_product_manager = (
    "The answer should be stories that follow the following structure: "
    "As a [type of user], I want [an action or feature] so that [benefit/value]."
)
# Positional order: api key, persona, evaluation criteria, agent_to_evaluate (worker agent), max interactions
product_manager_evaluation_agent = EvaluationAgent(
    openai_api_key,
    persona_product_manager_eval,
    evaluation_criteria_product_manager,
    product_manager_knowledge_agent,
    MAX_EVALUATION_INTERACTIONS,
)

# Program Manager - Knowledge Augmented Prompt Agent
persona_program_manager = "You are a Program Manager, you are responsible for defining the features for a product."
knowledge_program_manager = "Features of a product are defined by organizing similar user stories into cohesive groups."
# Steps reach this agent without the spec, so the spec is appended to its knowledge to keep
# the features specific to the product being planned rather than generic.
knowledge_program_manager += f"\nThese are the specifications of the product:\n{product_spec}"
program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona_program_manager, knowledge_program_manager)

# Program Manager - Evaluation Agent
persona_program_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."
evaluation_criteria_program_manager = (
    "The answer should be product features that follow the following structure: "
    "Feature Name: A clear, concise title that identifies the capability\n"
    "Description: A brief explanation of what the feature does and its purpose\n"
    "Key Functionality: The specific capabilities or actions the feature provides\n"
    "User Benefit: How this feature creates value for the user"
)
program_manager_evaluation_agent = EvaluationAgent(
    openai_api_key,
    persona_program_manager_eval,
    evaluation_criteria_program_manager,
    program_manager_knowledge_agent,
    MAX_EVALUATION_INTERACTIONS,
)

# Development Engineer - Knowledge Augmented Prompt Agent
persona_dev_engineer = "You are a Development Engineer, you are responsible for defining the development tasks for a product."
knowledge_dev_engineer = "Development tasks are defined by identifying what needs to be built to implement each user story."
# As with the Program Manager, give the engineer the spec so tasks target this product.
knowledge_dev_engineer += f"\nThese are the specifications of the product:\n{product_spec}"
development_engineer_knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona_dev_engineer, knowledge_dev_engineer)

# Development Engineer - Evaluation Agent
persona_dev_engineer_eval = "You are an evaluation agent that checks the answers of other worker agents."
evaluation_criteria_dev_engineer = (
    "The answer should be tasks following this exact structure: "
    "Task ID: A unique identifier for tracking purposes\n"
    "Task Title: Brief description of the specific development work\n"
    "Related User Story: Reference to the parent user story\n"
    "Description: Detailed explanation of the technical work required\n"
    "Acceptance Criteria: Specific requirements that must be met for completion\n"
    "Estimated Effort: Time or complexity estimation\n"
    "Dependencies: Any tasks that must be completed first"
)
development_engineer_evaluation_agent = EvaluationAgent(
    openai_api_key,
    persona_dev_engineer_eval,
    evaluation_criteria_dev_engineer,
    development_engineer_knowledge_agent,
    MAX_EVALUATION_INTERACTIONS,
)

# Results of each team as (workflow step, validated response) pairs, collected by the support
# functions so the final project plan can be printed with one labelled section per team.
project_plan = {
    "User Stories": [],
    "Product Features": [],
    "Engineering Tasks": [],
}


# Job function persona support functions
def run_team(evaluation_agent, query, section):
    """Have a team's EvaluationAgent produce a validated answer for query and record it under section."""
    result = evaluation_agent.evaluate(query)
    logger.info("%s accepted after %s iteration(s)", section, result["iterations"])
    project_plan[section].append((query, result["final_response"]))
    return result["final_response"]


def product_manager_support_function(query):
    """Produce user stories for a workflow step via the Product Manager team."""
    return run_team(product_manager_evaluation_agent, query, "User Stories")


def program_manager_support_function(query):
    """Produce product features for a workflow step via the Program Manager team."""
    return run_team(program_manager_evaluation_agent, query, "Product Features")


def development_engineer_support_function(query):
    """Produce engineering tasks for a workflow step via the Development Engineer team."""
    return run_team(development_engineer_evaluation_agent, query, "Engineering Tasks")


# Routing Agent
routing_agent = RoutingAgent(openai_api_key, [])
routing_agent.agents = [
    {
        "name": "Product Manager",
        "description": "Responsible for defining product personas and user stories only. Does not define features or tasks. Does not group stories",
        "func": lambda x: product_manager_support_function(x),
    },
    {
        "name": "Program Manager",
        "description": "Responsible for defining product features by grouping related user stories. Does not define user stories or development tasks",
        "func": lambda x: program_manager_support_function(x),
    },
    {
        "name": "Development Engineer",
        "description": "Responsible for defining the engineering and development tasks needed to implement each user story. Does not define user stories or features",
        "func": lambda x: development_engineer_support_function(x),
    },
]

# Run the workflow

print("\n*** Workflow execution started ***\n")
# Workflow Prompt
# ****
workflow_prompt = "What would the development tasks for this product be?"
# ****
print(f"Task to complete in this workflow, workflow prompt = {workflow_prompt}")

print("\nDefining workflow steps from the workflow prompt")
try:
    workflow_steps = action_planning_agent.extract_steps_from_prompt(workflow_prompt)
except Exception:
    logger.exception("The action planning agent failed to produce workflow steps")
    raise SystemExit(1)

if not workflow_steps:
    raise SystemExit("The action planning agent returned no steps; nothing to execute.")

print("Workflow steps:")
for number, step in enumerate(workflow_steps, start=1):
    print(f"  {number}. {step}")

completed_steps = []
for number, step in enumerate(workflow_steps, start=1):
    print(f"\n===== Executing step {number}/{len(workflow_steps)}: {step} =====")
    try:
        result = routing_agent.route(step)
    except Exception as error:
        # Keep going so one failed API call doesn't lose the rest of the plan.
        logger.exception("Step %s failed", number)
        result = f"[Step failed: {error}]"
    completed_steps.append(result)
    print(f"\n----- Result of step {number}: {step} -----\n{result}")

print("\n*** Workflow execution completed ***\n")

print("=" * 80)
print("EMAIL ROUTER - CONSOLIDATED PROJECT PLAN")
print("=" * 80)
for section, entries in project_plan.items():
    print(f"\n## {section}\n")
    if not entries:
        print("(No workflow step produced this section.)")
    for step, response in entries:
        print(f"### From workflow step: {step}\n")
        print(f"{response}\n")
