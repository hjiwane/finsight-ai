from fastapi import APIRouter
from app.agent.tools import BUDGETS, TRANSACTIONS

router = APIRouter(prefix="/api")

@router.get("/budgets")
def get_budgets():
    """Return current budget limits and spend for all categories."""
    return BUDGETS

@router.get("/transactions")
def get_transactions(limit: int = 20):
    """Return the most recent transactions."""
    return TRANSACTIONS[-limit:]