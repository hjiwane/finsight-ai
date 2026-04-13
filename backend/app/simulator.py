# import asyncio, random, uuid
# from datetime import datetime
# from app.agent.tools import add_transaction
# from app.websocket.manager import ws_manager
# from app.core.config import settings

# MERCHANTS = [
#     ("Swiggy",        "food"),
#     ("Zomato",        "food"),
#     ("Amazon",        "shopping"),
#     ("Flipkart",      "shopping"),
#     ("Netflix",       "entertainment"),
#     ("BookMyShow",    "entertainment"),
#     ("Ola",           "transport"),
#     ("Rapido",        "transport"),
#     ("PharmEasy",     "health"),
#     ("Unknown Merch", "shopping"),     # triggers suspicious flag
# ]


# def generate_transaction() -> dict:
#     merchant, category = random.choice(MERCHANTS)
#     amount = round(random.uniform(50, 4000), 2)

#     # 10% chance of suspicious large transaction
#     if random.random() < 0.10:
#         amount = round(random.uniform(16000, 40000), 2)

#     return {
#         "id":        str(uuid.uuid4())[:8],
#         "merchant":  merchant,
#         "category":  category,
#         "amount":    amount,
#         "timestamp": datetime.utcnow().isoformat(),
#         "upi_ref":   f"UPI{random.randint(10**11, 10**12 - 1)}",
#         "flagged":   False,
#     }


# async def analyze_transaction(txn: dict):
#     """Run the ReAct agent on a transaction and push the insight."""
#     from app.agent.agent import run_reactive
#     try:
#         insight = await run_reactive(txn)
#         await ws_manager.broadcast({
#             "type":           "agent_insight",
#             "transaction_id": txn["id"],
#             "message":        insight,
#         })
#     except Exception as e:
#         print(f"[Agent error] {e}")

# async def run_simulator():
#     """
#     Generates a fake UPI transaction every N seconds.
#     Broadcasts it immediately, then runs agent analysis in background.
#     """
#     await asyncio.sleep(2)
#     print("[Simulator] Starting UPI transaction stream...", flush=True)

#     while True:
#         txn = generate_transaction()
#         add_transaction(txn)
#         # 1. Push raw transaction to frontend immediately
#         await ws_manager.broadcast({"type": "transaction", "data": txn})
#         print(f"[Simulator] ₹{txn['amount']} @ {txn['merchant']}", flush=True)

#         # 2. Agent analysis runs in background — doesn't block the loop
#         try:
#             asyncio.create_task(analyze_transaction(txn))
#         except Exception as e:
#             print(f"[Analyze error] {e}", flush=True)

#         await asyncio.sleep(settings.SIMULATOR_INTERVAL_SECONDS)
import asyncio
import random
import uuid
from datetime import datetime, timezone

from app.agent.tools import add_transaction, get_transaction_by_id
from app.websocket.manager import ws_manager
from app.core.config import settings


MERCHANTS = [
    ("Swiggy", "food"),
    ("Zomato", "food"),
    ("Amazon", "shopping"),
    ("Flipkart", "shopping"),
    ("Netflix", "entertainment"),
    ("BookMyShow", "entertainment"),
    ("Ola", "transport"),
    ("Rapido", "transport"),
    ("PharmEasy", "health"),
    ("Unknown Merch", "shopping"),
]


def generate_transaction() -> dict:
    """Generate a fake UPI transaction."""
    merchant, category = random.choice(MERCHANTS)
    amount = round(random.uniform(50, 4000), 2)

    # 10% chance of a suspicious large transaction
    if random.random() < 0.10:
        amount = round(random.uniform(16000, 40000), 2)

    return {
        "id": str(uuid.uuid4())[:8],
        "merchant": merchant,
        "category": category,
        "amount": amount,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "upi_ref": f"UPI{random.randint(10**11, 10**12 - 1)}",
        "flagged": False,
    }


async def analyze_transaction(txn: dict) -> None:
    """Analyze a transaction and broadcast any resulting updates and run the ReAct agent on a transaction."""
    from app.agent.agent import run_reactive

    try:
        insight = await run_reactive(txn)

        # Re-fetch the transaction in case a tool updated its flagged state
        latest_txn = get_transaction_by_id(txn["id"])
        if latest_txn:
            await ws_manager.broadcast({
                "type": "transaction",
                "data": latest_txn,
            })

        if insight:
            await ws_manager.broadcast({
                "type": "agent_insight",
                "transaction_id": txn["id"],
                "message": insight,
            })

    except Exception as e:
        print(f"[Agent error] {e}", flush=True)


async def run_simulator() -> None:
    """Generate fake UPI transactions and broadcast them at a fixed interval."""
    await asyncio.sleep(2)
    print("[Simulator] Starting UPI transaction stream...", flush=True)

    while True:
        try:
            txn = generate_transaction()
            add_transaction(txn)

            # Broadcast the raw transaction immediately
            await ws_manager.broadcast({
                "type": "transaction",
                "data": txn,
            })
            print(f"[Simulator] ₹{txn['amount']} @ {txn['merchant']}", flush=True)

            # Only analyze suspicious / high-value transactions
            if txn["amount"] > 15000 or txn["merchant"] == "Unknown Merch":
                asyncio.create_task(analyze_transaction(txn))

        except Exception as e:
            print(f"[Simulator ERROR] {e}", flush=True)

        await asyncio.sleep(settings.SIMULATOR_INTERVAL_SECONDS)