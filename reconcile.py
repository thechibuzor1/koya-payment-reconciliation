#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from datetime import datetime

def parse_ts(ts):
    """Parse UTC timestamp; fall back to datetime.min on bad input."""
    if not ts:
        return datetime.min
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except Exception:
        return datetime.min

# txn_id -> (parsed_ts, status, amount)
latest = {}

with open("payments.jsonl", encoding="utf-8", errors="ignore") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        # Ignore lines that can't be read
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Ignore events without a txn_id
        txn_id = event.get("txn_id")
        if not txn_id:
            continue

        ts = parse_ts(event.get("ts"))
        status = event.get("status")
        amount = event.get("amount", 0)

        # Only the latest attempt per txn_id counts
        if txn_id not in latest or ts > latest[txn_id][0]:
            latest[txn_id] = (ts, status, amount)

# Count and total only where the latest attempt is success
count = 0
total = 0.0
for _, (_, status, amount) in latest.items():
    if status == "success":
        count += 1
        try:
            total += float(amount)
        except (TypeError, ValueError):
            pass  # skip unparseable amounts

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")