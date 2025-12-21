#!/usr/bin/env python3
from __future__ import annotations
import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("DISCORD_BOT_TOKEN not set in .env")
    raise SystemExit(1)

headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}

# Get guilds
r = requests.get("https://discord.com/api/v10/users/@me/guilds", headers=headers)
r.raise_for_status()
# If multiple guilds, pick the first
guild = r.json()[0]
guild_id = guild["id"]
print("Using guild:", guild_id, "-", guild["name"])

# Get roles
roles = requests.get(f"https://discord.com/api/v10/guilds/{guild_id}/roles", headers=headers)
roles.raise_for_status()
role_id = None
for role in roles.json():
    if role["name"] == "Bot Admin":
        role_id = role["id"]
        break

if not role_id:
    print("Role 'Bot Admin' not found. Please ensure role exists.")
    raise SystemExit(1)

# Get channels to find admin category id and check if channel exists
ch = requests.get(f"https://discord.com/api/v10/guilds/{guild_id}/channels", headers=headers)
ch.raise_for_status()
channels = ch.json()
admin_cat_id = None
existing = [c for c in channels if c["name"] == "🔧-service"]
if existing:
    print("Channel '🔧-service' already exists, id:", existing[0]["id"])
    raise SystemExit(0)

for c in channels:
    if c["type"] == 4 and c["name"] == "⚙️ ADMIN":
        admin_cat_id = c["id"]
        break

if not admin_cat_id:
    print("Admin category '⚙️ ADMIN' not found; will create channel at top level.")

# Permission bits
VIEW_CHANNEL = 1024
SEND_MESSAGES = 2048

# Overwrites
overwrites = []
# Deny @everyone view
overwrites.append({"id": guild_id, "type": 0, "deny": str(VIEW_CHANNEL)})
# Allow Bot Admin view & send
overwrites.append({"id": role_id, "type": 0, "allow": str(VIEW_CHANNEL + SEND_MESSAGES)})

payload = {
    "name": "🔧-service",
    "type": 0,
    "permission_overwrites": overwrites,
}
if admin_cat_id:
    payload["parent_id"] = admin_cat_id

print("Creating channel with payload:", payload)
res = requests.post(f"https://discord.com/api/v10/guilds/{guild_id}/channels", headers=headers, json=payload)
if res.status_code in (200, 201):
    print("Channel created:", res.json()["id"])
else:
    print("Failed to create channel", res.status_code, res.text)
    res.raise_for_status()
