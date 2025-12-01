# predator
An enterprise-grade multi-agent system that automates lead research, scoring and outreach with human-in-the-loop safety.
# Predator: The Autonomous Sales Orchestrator 🦅

**Winner of the "Enterprise Agents" Track Strategy**

## 📖 Overview
Predator is an enterprise-grade AI agent built with the Google ADK. It automates the "research-to-outreach" sales loop by using a multi-agent architecture to score leads, check competitor pricing (via A2A), and draft emails that require human approval (Human-in-the-Loop).

## 🏗️ Architecture
* **Brain:** Gemini 2.5 Flash-Lite
* **Framework:** Google Agent Development Kit (ADK)
* **Protocol:** Agent-to-Agent (A2A) for market data
* **Deployment:** Vertex AI Agent Engine / Cloud Run

## 🚀 Key Features (Course Concepts Applied)
1.  **Multi-Agent System:** Orchestrator delegates to a 'Market Oracle' agent.
2.  **A2A Communication:** Uses `RemoteA2aAgent` to query external services.
3.  **Safety First:** Implements `tool_context.request_confirmation` for email tools.
4.  **Memory Management:** Uses `EventsCompactionConfig` to summarize long context.

## 🛠️ How to Run
1.  Clone the repo.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Start the Market Oracle (A2A Service):
    ```bash
    python market_oracle.py
    ```
4.  Run Predator:
    ```bash
    python predator.py
    ```

## 📊 Deployment
This agent is configured for deployment on **Google Cloud Vertex AI Agent Engine**.
See `.agent_engine_config.json` for resource limits.
