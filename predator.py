import os
import asyncio
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.tools import ToolContext
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.genai import types

# --- CONFIG ---
model = Gemini(model="gemini-2.5-flash-lite")

# --- TOOL 1: Business Logic (Lead Scorer) ---
def score_lead(budget: int, urgency: str) -> dict:
    """Calculates win probability (0-100) based on budget and urgency."""
    score = 50 # Base score
    if budget >= 50000: score += 30
    if urgency.lower() in ["high", "asap", "now"]: score += 20
    return {
        "score": score,
        "priority": "CRITICAL" if score >= 90 else "NORMAL",
        "recommendation": "Close immediately" if score >= 90 else "Nurture"
    }

# --- TOOL 2: Safety (Human-in-the-Loop Email) ---
def draft_outreach(recipient: str, strategy: str, tool_context: ToolContext) -> dict:
    """Drafts an email but PAUSES for human approval before 'sending'."""
    
    # RESUME CASE: User has already approved/rejected
    if tool_context.tool_confirmation:
        if tool_context.tool_confirmation.confirmed:
            return {"status": "SENT", "info": f"Email sent to {recipient}."}
        else:
            return {"status": "REJECTED", "info": "User blocked the email."}

    # FIRST RUN: Pause and ask for permission
    tool_context.request_confirmation(
        hint=f"🛑 SAFETY CHECK: Approve email to {recipient} using strategy '{strategy}'?",
        payload={"recipient": recipient, "strategy": strategy}
    )
    return {"status": "PENDING", "info": "Waiting for human authorization."}

# --- COMPONENTS ---

# 1. The A2A Connection (Hands)
# Connects to the 'market_oracle.py' you are running locally
market_oracle = RemoteA2aAgent(
    name="market_oracle",
    description="Fetches competitor pricing from external vendor.",
    agent_card="http://localhost:8001/.well-known/agent-card.json"
)

# 2. The Predator Agent (Brain)
predator = LlmAgent(
    name="Predator_Sales_Orchestrator",
    model=model,
    instruction="""
    You are Predator, an autonomous sales agent.
    
    YOUR PLAYBOOK:
    1. Analyze the lead. Use `score_lead` to determine priority.
    2. If priority is CRITICAL, ask `market_oracle` for competitor pricing.
    3. Use `draft_outreach` to prepare a deal. 
    
    CRITICAL: You cannot send emails without human approval.
    """,
    tools=[score_lead, draft_outreach],
    sub_agents=[market_oracle] 
)

# 3. The Application Wrapper (Memory & Ops)
app = App(
    name="predator_app",
    root_agent=predator,
    # Day 3: Context Compaction (Summarizes history to save tokens)
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=4,
        overlap_size=1
    )
)

# 4. Execution (Observability)
async def main():
    runner = Runner(
        app=app, 
        session_service=InMemorySessionService(),
        plugins=[LoggingPlugin()] # Day 4: "Glass Box" Logs
    )
    
    print("🦅 Predator is watching...")
    
    # SIMULATED SCENARIO
    query = "New Lead: Acme Corp. Budget: $60,000. Urgency: ASAP. They need a CRM."
    print(f"\nUSER: {query}\n")
    
    async for event in runner.run_async(user_id="admin", session_id="demo", new_message=query):
        # Handle the "Pause" for Human Approval
        if hasattr(event, 'actions') and event.actions and event.actions.requested_tool_confirmations:
            print("\n⚠️  PREDATOR PAUSED: APPROVAL REQUIRED")
            approval = input(">> Type 'yes' to approve email, 'no' to reject: ")
            
            # Resume with human decision
            resume_msg = types.FunctionResponse(
                id=list(event.actions.requested_tool_confirmations.keys())[0],
                name="adk_request_confirmation",
                response={"confirmed": (approval.lower() == 'yes')}
            )
            async for resume_event in runner.run_async(
                user_id="admin", session_id="demo", 
                new_message=types.Content(parts=[types.Part(function_response=resume_msg)]),
                invocation_id=event.invocation_id
            ):
                if resume_event.is_final_response():
                    print(f"\n🦅 PREDATOR: {resume_event.content.parts[0].text}")
                    
        elif event.is_final_response():
            print(f"\n🦅 PREDATOR: {event.content.parts[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
