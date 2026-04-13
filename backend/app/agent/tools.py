from langchain_core.tools import tool
from datetime import datetime, timedelta, timezone
import json

# IN-MEMORY STORE  (replace with Postgres later)

TRANSACTIONS: list[dict] = []
MAX_TRANSACTIONS = 5000

BUDGETS: dict[str, dict] = {
    "food":          {"limit": 5000,  "spent": 0},
    "shopping":      {"limit": 8000,  "spent": 0},
    "entertainment": {"limit": 3000,  "spent": 0},
    "transport":     {"limit": 2000,  "spent": 0},
    "health":        {"limit": 4000,  "spent": 0},
}


def add_transaction(txn: dict):
    """Called by simulator when a new transaction arrives."""
    # 1. Update budget for the new transaction
    cat = txn.get("category")
    if cat and cat in BUDGETS:
        BUDGETS[cat]["spent"] += txn.get("amount", 0)

    # 2. Add it
    TRANSACTIONS.append(txn)

    # 3. If over cap, remove oldest and reverse its budget impact
    if len(TRANSACTIONS) > MAX_TRANSACTIONS:
        removed = TRANSACTIONS.pop(0)
        removed_cat = removed.get("category")
        if removed_cat and removed_cat in BUDGETS:
            BUDGETS[removed_cat]["spent"] = max(
                0,
                BUDGETS[removed_cat]["spent"] - removed.get("amount", 0)
            )

def get_transaction_by_id(transaction_id: str) -> dict | None:
    for t in TRANSACTIONS:
        if t["id"] == transaction_id:
            return t
    return None


# TOOLS

@tool
def get_recent_transactions(limit: str = "10", category: str = "") -> str:
    """
    Get recent UPI transactions. Optionally filter by category.
    Categories: food, shopping, entertainment, transport, health.
    Leave category empty to get all transactions.
    """
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 10

    txns = TRANSACTIONS[-50:]
    if category:   # empty string is falsy, so this still works
        txns = [t for t in txns if t.get("category") == category]
    txns = txns[-limit:]
    if not txns:
        return "No transactions found."
    return json.dumps(txns, indent=2)


@tool
def get_budget_status(category: str) -> str:
    """
    Get budget limit and current spending for a category.
    Categories: food, shopping, entertainment, transport, health
    """
    if category not in BUDGETS:
        return f"No budget set for '{category}'. Valid: {list(BUDGETS.keys())}"
    b = BUDGETS[category]
    pct = round((b["spent"] / b["limit"]) * 100, 1) if b["limit"] else 0
    return json.dumps({
        "category": category,
        "limit_inr": b["limit"],
        "spent_inr": round(b["spent"], 2),
        "remaining": round(b["limit"] - b["spent"], 2),
        "percent_used": pct,
        "status": "over budget" if b["spent"] > b["limit"] else
                  "warning" if pct > 80 else "ok"
    })


@tool
def set_budget(category: str, amount_inr: float) -> str:
    """
    Set a monthly spending budget for a category.
    Categories: food, shopping, entertainment, transport, health
    """
    if category not in BUDGETS:
        return f"Invalid category '{category}'. Valid: {list(BUDGETS.keys())}"
    if amount_inr <= 0:
        return "Budget amount must be greater than 0."
    BUDGETS[category]["limit"] = amount_inr
    return f"Budget for '{category}' set to ₹{amount_inr:.0f}"


@tool
def get_spending_summary(days: str = "7") -> str:
    """
    Get total spending per category over the last N days.
    """
    try:
        days = int(days)
    except (ValueError, TypeError):
        days = 7

    since = datetime.now(timezone.utc) - timedelta(days=days)
    totals: dict[str, float] = {}

    for t in TRANSACTIONS:
        try:
            ts = datetime.fromisoformat(t["timestamp"])
        except (KeyError, ValueError):
            continue

        if ts < since:
            continue

        cat = t.get("category", "other")
        totals[cat] = round(totals.get(cat, 0) + t["amount"], 2)

    if not totals:
        return "No transactions in this period."

    sorted_totals = dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))
    return json.dumps({
        "period_days": days,
        "by_category": {k: f"₹{v:.2f}" for k, v in sorted_totals.items()},
        "total": f"₹{sum(totals.values()):.2f}"
    }, indent=2)


@tool
def flag_suspicious_transaction(transaction_id: str, reason: str) -> str:
    """
    Flag a transaction as suspicious with a reason.
    Use when: amount > ₹15,000, merchant is unknown, or timing is odd.
    """
    for t in TRANSACTIONS:
        if t["id"] == transaction_id:
            t["flagged"] = True
            t["flag_reason"] = reason
            return f"Transaction {transaction_id} flagged: {reason}"
    return f"Transaction {transaction_id} not found."


tools = [
    get_recent_transactions,
    get_budget_status,
    set_budget,
    get_spending_summary,
    flag_suspicious_transaction,
]