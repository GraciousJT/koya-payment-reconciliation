#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json

latest = {}  # txn_id -> latest event

with open("payments.jsonl", encoding="utf-8") as f:
    for line in f:
        # Skip lines that can't be read
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue

        # Skip events without a txn_id
        txn_id = event.get("txn_id")
        if not txn_id:
            continue

        # Only the latest attempt per txn_id counts (file order is not chronological)
        prev = latest.get(txn_id)
        if prev is None or event["ts"] > prev["ts"]:
            latest[txn_id] = event


def to_number(value):
    # Some amounts are strings with thousands separators, e.g. "4,804.15"
    if isinstance(value, str):
        value = value.replace(",", "")
    return float(value)


total = 0.0
count = 0
for event in latest.values():
    if event["status"] == "success":
        total += to_number(event["amount"])
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
