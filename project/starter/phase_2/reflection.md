# Reflection: Email Router Agentic Workflow

## Strengths

- **Reusable building blocks.** The workflow is assembled entirely from the Phase 1 agent library. Pointing it at a different product only means swapping the spec file and prompt; no agent code changes.
- **Built-in quality control.** Each specialist is paired with an EvaluationAgent, and in the recorded run every team's output was accepted within one or two rounds. The first drafts often missed the required format (for example, user personas instead of "As a … I want … so that …" stories), and the evaluation loop fixed this without human intervention.
- **Dynamic planning.** The ActionPlanningAgent turned a one-line request ("What would the development tasks for this product be?") into a seven-step plan that covers stories, features and tasks. The RoutingAgent then assigned those steps by meaning, not by hard-coded rules.
- **Robustness.** A failed step is logged and recorded, and the workflow carries on, so one API error doesn't lose the rest of the plan.

## Limitations

- **Steps share no context.** Each step is routed and answered on its own. The Program Manager does not see the stories the Product Manager wrote, and the Development Engineer does not see the features, so the three sections are generated separately from the spec rather than built on each other. Task "Related User Story" fields therefore don't always match a story in the User Stories section exactly.
- **Routing has no way to say "none of these".** The router always picks the closest description. Steps that fit no team, such as "Determine the desired outcomes for each action" (similarity 0.23) or "Compile all … into a development plan", are still sent to whichever team is nearest, which produces overlapping output.
- **The evaluator is a coarse yes/no gate.** It checks structure, not quality or coverage, and it can pass an answer that is well formatted but repetitive or incomplete.
- **Cost and latency.** Every routing call re-embeds all agent descriptions, and each evaluation round makes three LLM calls.

## Suggested improvement

**Pass completed work forward as context.** Keep a running workflow state (stories → features → tasks) and include the relevant earlier results in each step's prompt. For example, the Program Manager would receive the accepted user stories to group, and the Development Engineer would receive those stories with their IDs. That would make the plan internally consistent, let tasks reference real story IDs, and remove the need to append the full spec to every agent's knowledge. A small addition to the router would complement it: a minimum similarity threshold, below which a step is merged into its neighbour or skipped instead of being forced onto the nearest team.
