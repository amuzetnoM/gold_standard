#!/usr/bin/env python3
"""List all Discord channels in the server."""

import asyncio
import os
from pathlib import Path

import discord

# Load .env file manually
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ[key.strip()] = value.strip()


async def list_channels():
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        for guild in client.guilds:
            print(f"=== SERVER: {guild.name} ===")
            print(f"ID: {guild.id}")
            print(f"Members: {guild.member_count}")

            # List categories and their channels
            for cat in sorted(guild.categories, key=lambda c: c.position):
                print(f"\n[CATEGORY] {cat.name} (pos: {cat.position})")
                for ch in sorted(cat.text_channels, key=lambda c: c.position):
                    print(f"  #{ch.name} (id: {ch.id})")

            # List uncategorized channels
            uncategorized = [ch for ch in guild.text_channels if ch.category is None]
            if uncategorized:
                print("\n[UNCATEGORIZED]")
                for ch in uncategorized:
                    print(f"  #{ch.name} (id: {ch.id})")

            # Check for duplicates
            channel_names = [ch.name for ch in guild.text_channels]
            from collections import Counter

            duplicates = {name: count for name, count in Counter(channel_names).items() if count > 1}
            if duplicates:
                print("\n[DUPLICATES DETECTED]")
                for name, count in duplicates.items():
                    print(f"  #{name}: {count} copies")

        await client.close()

    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("ERROR: DISCORD_BOT_TOKEN not set")
        return

    await client.start(token)


if __name__ == "__main__":
    asyncio.run(list_channels())
