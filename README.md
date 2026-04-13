# FinSight AI

> Real-time UPI transaction monitoring system with an agentic AI layer powered by LangGraph and Groq.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square&logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-ReAct-purple?style=flat-square)
![React](https://img.shields.io/badge/React-TypeScript-blue?style=flat-square&logo=react)
![Groq](https://img.shields.io/badge/LLM-Groq%20Llama3-orange?style=flat-square)

![FinSight AI Demo](demo.gif)

---

## What it does

FinSight AI monitors a live UPI transaction stream and provides two modes of AI interaction:

- **Reactive mode** — automatically detects suspicious transactions (large amounts, unknown merchants, odd hours) and flags them in real time without any user input
- **Conversational mode** — a natural language chat interface where users can ask questions about their spending, set budgets, and get insights

---

## Architecture

```
[Transaction Simulator]
        │
        ▼
[FastAPI Backend] ──── WebSocket /ws/feed ────▶ [React Frontend]
        │                                              │
        ▼                                         Live feed +
[LangGraph ReAct Agent]                          Chart + Chat UI
        │
   [5 LangChain Tools]
   ├── get_recent_transactions
   ├── get_spending_summary
   ├── get_budget_status
   ├── set_budget
   └── flag_suspicious_transaction
```

The transaction feed updates **immediately** when a transaction arrives. Agent analysis follows asynchronously — the user sees the data first, AI insight appears shortly after. This was a deliberate UX decision to avoid perceived latency.

---

## Tech stack

| Layer | Tech |
|---|---|
| Backend | FastAPI, Python 3.11 |
| Agent | LangGraph (ReAct pattern), LangChain |
| LLM | Llama 3.3 70B via Groq API |
| Real-time | WebSockets, asyncio |
| Frontend | React, TypeScript, Recharts |
| Config | Pydantic Settings |

---

## Key design decisions

**Why LangGraph over a simple chain?**
The agent needs to loop - call a tool, get a result, decide whether to call another tool or respond. LangGraph's ReAct pattern handles this naturally with conditional edges. A linear chain can't loop.

**Why two separate WebSocket channels?**
`/ws/feed` is passive (frontend only listens) and receives transaction events. `/ws/chat` is bidirectional for the conversational agent. Keeping them separate means transaction broadcasts never go to chat clients and vice versa.

**Why Python-level suspicious detection before the LLM?**
Deterministic rules (amount > ₹15,000, unknown merchant, odd hours) are enforced in Python first. The LLM is only called to flag and describe, not to decide. Financial rules should be auditable and consistent, not probabilistic.

**Why a semaphore on agent calls?**
The reactive agent and the conversational agent share the same Groq API quota. Without a semaphore, a chat message and a suspicious transaction arriving simultaneously would cause both to fail with a 429. The semaphore serializes them if the agent is busy, reactive analysis is skipped silently.

---

## Project structure

```
finsight/
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   ├── agent.py        # LangGraph ReAct graph + public API
│   │   │   └── tools.py        # 5 LangChain tools + in-memory store
│   │   ├── api/
│   │   │   └── routes.py       # REST endpoints (/budgets, /transactions)
│   │   ├── core/
│   │   │   └── config.py       # Pydantic settings
│   │   ├── websocket/
│   │   │   ├── manager.py      # WebSocketManager (separate feed/chat lists)
│   │   │   ├── feed.py         # /ws/feed route
│   │   │   └── chat.py         # /ws/chat route
│   │   ├── main.py             # FastAPI app + lifespan
│   │   └── simulator.py        # Fake UPI transaction generator
│   └── requirements.txt
└── frontend/
    └── src/
        ├── components/         # TransactionFeed, SpendingChart, ChatPanel
        ├── hooks/              # useFeedSocket, useChatSocket
        ├── types/              # TypeScript interfaces
        └── App.tsx
```

---

## Running locally

**Backend**
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# create .env with your Groq API key (free at console.groq.com)
echo "GROQ_API_KEY=gsk_your_key_here" > .env

uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The transaction simulator starts automatically and generates a new UPI transaction every 15 seconds.

---

## Example chat queries

```
Give me a spending summary for this week
What's my food budget status?
Set my entertainment budget to ₹5000
How many suspicious transactions were there?
Show me my recent transport transactions
```

---


