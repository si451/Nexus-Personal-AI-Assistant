"""
Goal Management Tools
======================
LangChain tools that Nexus calls to manage its own goal execution.

These tools let the model:
- Create structured plans before executing
- Track step completion
- Report failures
- Check its own progress
"""

from langchain_core.tools import tool
from models.goal import get_goal_tracker


@tool
def create_goal_plan(goal: str, steps: str, done_when: str) -> str:
    """
    Create a structured goal execution plan BEFORE starting any complex task.
    Call this FIRST when given a multi-step task (3+ steps).
    
    Args:
        goal: What needs to be achieved (e.g., "Find 3 leads on LinkedIn and send connection requests")
        steps: Steps as a semicolon-separated list. Each step format: "description|tool" 
               Example: "Open LinkedIn search|open_chrome_at; Search for marketing managers|type_text; Click first profile|click_at"
        done_when: Specific completion criteria (e.g., "3 connection requests sent with personalized messages")
    
    Returns:
        Formatted plan confirmation with step list
    """
    tracker = get_goal_tracker()
    
    # Parse steps from semicolon-separated string
    parsed_steps = []
    for step_str in steps.split(";"):
        step_str = step_str.strip()
        if not step_str:
            continue
        
        if "|" in step_str:
            desc, tool_name = step_str.rsplit("|", 1)
            parsed_steps.append({"description": desc.strip(), "tool": tool_name.strip()})
        else:
            parsed_steps.append({"description": step_str, "tool": "auto"})
    
    if not parsed_steps:
        return "⚠️ No valid steps provided. Format: 'description|tool; description|tool; ...'"
    
    plan = tracker.create_plan(goal, parsed_steps, done_when)
    
    # Format nice output
    lines = [
        f"🎯 PLAN CREATED: {plan.goal}",
        f"📋 {len(plan.steps)} Steps:"
    ]
    for step in plan.steps:
        icon = "🔷" if step.number == 1 else "⬜"
        lines.append(f"  {icon} {step.number}. {step.description} → {step.tool}")
    lines.append(f"✅ Done when: {plan.done_when}")
    lines.append(f"\n▶️ START with Step 1: {plan.steps[0].description}")
    
    return "\n".join(lines)


@tool
def complete_step(step_number: int, outcome: str = "Done") -> str:
    """
    Mark a goal step as complete and advance to the next step.
    Call this AFTER successfully completing each step in your plan.
    
    Args:
        step_number: The step number to mark as complete (1-indexed)
        outcome: Brief description of what was accomplished (e.g., "Opened LinkedIn search page")
    
    Returns:
        Status update with next step information
    """
    tracker = get_goal_tracker()
    return tracker.complete_step(step_number, outcome)


@tool
def fail_step(step_number: int, reason: str) -> str:
    """
    Report that a step failed. The system will track attempts and suggest alternatives.
    Call this when an action doesn't work as expected.
    
    Max 3 attempts per step — after 3 failures, the step is permanently marked failed.
    
    Args:
        step_number: The step number that failed
        reason: Why it failed (e.g., "Button not found at expected coordinates")
    
    Returns:
        Guidance on whether to retry or move on
    """
    tracker = get_goal_tracker()
    return tracker.fail_step(step_number, reason)


@tool
def get_current_plan() -> str:
    """
    Check the current goal plan status and progress.
    Use this to review your own plan and see what step you're on.
    
    Returns:
        Current plan with step statuses, or "No active plan" if idle
    """
    tracker = get_goal_tracker()
    status = tracker.get_status_context()
    
    if not status:
        return "📋 No active plan. Create one with create_goal_plan for complex tasks."
    
    return status


# Export
GOAL_TOOLS = [create_goal_plan, complete_step, fail_step, get_current_plan]
