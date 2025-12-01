graph LR
    %% Define Styles to match your reference image
    classDef root fill:#1f4e26,stroke:#555,stroke-width:2px,color:white,font-weight:bold;
    classDef agent fill:#34495e,stroke:#999,stroke-width:2px,color:white;
    classDef tool fill:#53565a,stroke:#fff,stroke-width:1px,color:white,rx:20,ry:20;
    classDef cluster style=fill:none,stroke:#ccc,stroke-width:1px,stroke-dasharray: 5 5;

    %% Main Orchestrator
    Predator(🤖 Predator_Sales_Orchestrator)

    %% Local Tools
    LeadScorer(🔧 score_lead)
    EmailDraft(🔧 draft_outreach <br/> <i>Human-in-the-Loop</i>)

    %% Remote A2A Agent Subgraph
    subgraph "Remote Vendor Service (A2A)"
        MarketOracle(🤖 market_oracle)
        PriceTool(🔧 get_competitor_pricing)
    end

    %% Connections
    Predator ==>|Delegates Task| MarketOracle
    Predator -->|Calls| LeadScorer
    Predator -->|Calls| EmailDraft
    MarketOracle -->|Uses| PriceTool

    %% Apply Styles
    class Predator root;
    class MarketOracle agent;
    class LeadScorer,EmailDraft,PriceTool tool;
