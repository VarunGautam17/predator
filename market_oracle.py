import os
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini
from google.genai import types

# 1. Configure Model
retry_config = types.HttpRetryOptions(attempts=5, exp_base=7, initial_delay=1)
model = Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config)

# 2. Define Tool
def get_competitor_pricing(service_type: str) -> str:
    """Returns current market rates for a specific service."""
    rates = {
        "crm": "Market Avg: $60,000/yr. Top Competitor: Salesforce ($75k).",
        "cloud storage": "Market Avg: $200/TB. Top Competitor: AWS ($210).",
        "consulting": "Market Avg: $250/hr. Top Competitor: McKinsey ($500)."
    }
    for key, val in rates.items():
        if key in service_type.lower(): return val
    return "Service type not found in market database."

# 3. Create Agent
oracle_agent = LlmAgent(
    name="market_oracle",
    model=model,
    description="External market intelligence provider.",
    instruction="You provide real-time competitor pricing. Use `get_competitor_pricing` to answer queries.",
    tools=[get_competitor_pricing]
)

# 4. Expose via A2A (Port 8001)
app = to_a2a(oracle_agent, port=8001)

if __name__ == "__main__":
    import uvicorn
    print("🔮 Market Oracle is live on Port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
