"""
Nexus Goal Models & Tracker
============================
Pydantic-based structured goal execution system.

Provides:
- GoalState: State machine enum (IDLE → PLANNING → EXECUTING → COMPLETE)
- GoalStep: Individual step in a plan
- GoalPlan: Full structured plan with steps and completion criteria
- GoalTracker: Singleton that manages the active plan + anti-loop detection
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime


# ═══════════════════════════════════════════════════════
#  PYDANTIC MODELS
# ═══════════════════════════════════════════════════════

class GoalState(str, Enum):
    """State machine for goal execution."""
    IDLE = "idle"           # No active goal
    PLANNING = "planning"   # Decomposing goal into steps
    EXECUTING = "executing" # Working through steps
    VERIFYING = "verifying" # Checking if goal is met
    COMPLETE = "complete"   # Goal achieved
    FAILED = "failed"       # Goal failed after retries


class StepStatus(str, Enum):
    """Status of an individual step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"


class GoalStep(BaseModel):
    """A single step in a goal plan."""
    number: int = Field(description="Step number (1-indexed)")
    description: str = Field(description="What this step does")
    tool: str = Field(description="Primary tool(s) to use")
    status: StepStatus = StepStatus.PENDING
    outcome: Optional[str] = None
    attempts: int = 0


class GoalPlan(BaseModel):
    """A structured goal execution plan."""
    goal: str = Field(description="What needs to be achieved")
    steps: List[GoalStep] = Field(description="Ordered list of steps")
    done_when: str = Field(description="Specific completion criteria")
    state: GoalState = GoalState.PLANNING
    current_step: int = 1
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


class GoalCompletion(BaseModel):
    """Result of a completed goal."""
    goal: str
    success: bool
    results: str
    steps_completed: int
    steps_total: int
    suggestions: Optional[str] = None


# ═══════════════════════════════════════════════════════
#  GOAL TRACKER (Singleton)
# ═══════════════════════════════════════════════════════

class GoalTracker:
    """
    Manages goal execution state and provides anti-loop detection.
    
    Injected into the system prompt to give the model awareness of:
    - Current goal and progress
    - Which step it's on
    - Anti-loop warnings
    """
    
    def __init__(self):
        self.active_plan: Optional[GoalPlan] = None
        self.completed_goals: List[GoalCompletion] = []
        
        # Anti-loop detection
        self._recent_tool_calls: List[str] = []
        self._max_tool_history = 10
        self._consecutive_observe_count = 0
    
    def create_plan(self, goal: str, steps: List[dict], done_when: str) -> GoalPlan:
        """Create and activate a new goal plan."""
        goal_steps = []
        for i, step in enumerate(steps, 1):
            goal_steps.append(GoalStep(
                number=i,
                description=step.get("description", step.get("desc", f"Step {i}")),
                tool=step.get("tool", "unknown")
            ))
        
        self.active_plan = GoalPlan(
            goal=goal,
            steps=goal_steps,
            done_when=done_when,
            state=GoalState.EXECUTING,
            current_step=1
        )
        
        # Mark first step as in-progress
        if self.active_plan.steps:
            self.active_plan.steps[0].status = StepStatus.IN_PROGRESS
        
        # Reset anti-loop counters
        self._recent_tool_calls.clear()
        self._consecutive_observe_count = 0
        
        print(f"[GoalTracker] 🎯 New Plan: {goal} ({len(goal_steps)} steps)")
        return self.active_plan
    
    def complete_step(self, step_number: int, outcome: str = "") -> str:
        """Mark a step as complete and advance to next."""
        if not self.active_plan:
            return "No active plan. Create one first with create_goal_plan."
        
        # Find the step
        step = next((s for s in self.active_plan.steps if s.number == step_number), None)
        if not step:
            return f"Step {step_number} not found in plan."
        
        step.status = StepStatus.DONE
        step.outcome = outcome
        
        # Advance to next pending step
        next_step = next(
            (s for s in self.active_plan.steps if s.status == StepStatus.PENDING),
            None
        )
        
        if next_step:
            next_step.status = StepStatus.IN_PROGRESS
            self.active_plan.current_step = next_step.number
            msg = f"✓ Step {step_number} done. Now on step {next_step.number}: {next_step.description}"
        else:
            # All steps done!
            self.active_plan.state = GoalState.COMPLETE
            self.active_plan.completed_at = datetime.now().isoformat()
            
            completion = GoalCompletion(
                goal=self.active_plan.goal,
                success=True,
                results=outcome,
                steps_completed=len([s for s in self.active_plan.steps if s.status == StepStatus.DONE]),
                steps_total=len(self.active_plan.steps)
            )
            self.completed_goals.append(completion)
            msg = f"✅ ALL STEPS DONE! Goal '{self.active_plan.goal}' is complete."
            
        print(f"[GoalTracker] {msg}")
        return msg
    
    def fail_step(self, step_number: int, reason: str = "") -> str:
        """Mark a step as failed."""
        if not self.active_plan:
            return "No active plan."
        
        step = next((s for s in self.active_plan.steps if s.number == step_number), None)
        if not step:
            return f"Step {step_number} not found."
        
        step.attempts += 1
        
        if step.attempts >= 3:
            step.status = StepStatus.FAILED
            step.outcome = f"FAILED after {step.attempts} attempts: {reason}"
            return f"❌ Step {step_number} FAILED after {step.attempts} attempts. Move on or report to Siddi."
        else:
            return f"⚠️ Step {step_number} attempt {step.attempts}/3 failed: {reason}. Try a different approach."
    
    def record_tool_call(self, tool_name: str) -> Optional[str]:
        """
        Record a tool call and return a warning if anti-loop is triggered.
        
        Returns None if everything is fine, or a warning string if looping detected.
        """
        self._recent_tool_calls.append(tool_name)
        if len(self._recent_tool_calls) > self._max_tool_history:
            self._recent_tool_calls.pop(0)
        
        # Anti-loop: consecutive see_screen detection
        if tool_name == "see_screen":
            self._consecutive_observe_count += 1
            if self._consecutive_observe_count >= 2:
                warning = (
                    f"🔴 ANTI-LOOP WARNING: You called see_screen {self._consecutive_observe_count} times "
                    f"without acting! YOUR NEXT TOOL CALL MUST BE AN ACTION "
                    f"(click_at, type_text, press_key, scroll_wheel, shell, etc.). "
                    f"DO NOT call see_screen again."
                )
                print(f"[GoalTracker] {warning}")
                return warning
        else:
            # Non-observation tool resets the counter
            self._consecutive_observe_count = 0
        
        # Anti-loop: same tool called 5+ times in last 7 calls
        if len(self._recent_tool_calls) >= 7:
            last_7 = self._recent_tool_calls[-7:]
            most_common = max(set(last_7), key=last_7.count)
            if last_7.count(most_common) >= 5:
                warning = (
                    f"🔴 LOOP DETECTED: You've called '{most_common}' {last_7.count(most_common)} "
                    f"times in last 7 calls. STOP and try a completely different approach, "
                    f"or report the issue to Siddi."
                )
                print(f"[GoalTracker] {warning}")
                return warning
        
        return None
    
    def get_status_context(self) -> str:
        """
        Get a concise status string to inject into the system prompt.
        This gives the model awareness of its current goal state.
        """
        if not self.active_plan or self.active_plan.state in (GoalState.IDLE, GoalState.COMPLETE):
            return ""
        
        plan = self.active_plan
        lines = [
            f"\n### 🎯 ACTIVE GOAL TRACKER",
            f"**Goal:** {plan.goal}",
            f"**State:** {plan.state.value.upper()}",
            f"**Progress:**"
        ]
        
        for step in plan.steps:
            icon = {
                StepStatus.PENDING: "⬜",
                StepStatus.IN_PROGRESS: "🔷",
                StepStatus.DONE: "✅",
                StepStatus.FAILED: "❌",
                StepStatus.SKIPPED: "⏭️"
            }.get(step.status, "⬜")
            
            outcome_str = f" → {step.outcome}" if step.outcome else ""
            current = " ← YOU ARE HERE" if step.status == StepStatus.IN_PROGRESS else ""
            lines.append(f"  {icon} {step.number}. {step.description}{outcome_str}{current}")
        
        lines.append(f"**Done When:** {plan.done_when}")
        
        done_count = len([s for s in plan.steps if s.status == StepStatus.DONE])
        lines.append(f"**Completion:** {done_count}/{len(plan.steps)} steps")
        
        # Add anti-loop reminder if we've been observing
        if self._consecutive_observe_count > 0:
            lines.append(f"\n⚠️ You've observed {self._consecutive_observe_count} time(s) — ACT NOW, don't observe again!")
        
        return "\n".join(lines)
    
    def reset(self):
        """Reset tracker to idle state."""
        if self.active_plan and self.active_plan.state == GoalState.EXECUTING:
            # Save incomplete plan
            self.completed_goals.append(GoalCompletion(
                goal=self.active_plan.goal,
                success=False,
                results="Goal was reset before completion",
                steps_completed=len([s for s in self.active_plan.steps if s.status == StepStatus.DONE]),
                steps_total=len(self.active_plan.steps)
            ))
        
        self.active_plan = None
        self._recent_tool_calls.clear()
        self._consecutive_observe_count = 0


# ═══════════════════════════════════════════════════════
#  SINGLETON
# ═══════════════════════════════════════════════════════

_tracker_instance: Optional[GoalTracker] = None

def get_goal_tracker() -> GoalTracker:
    """Get the singleton GoalTracker instance."""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = GoalTracker()
    return _tracker_instance
