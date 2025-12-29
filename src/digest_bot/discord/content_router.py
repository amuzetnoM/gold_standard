#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════
#  Digest Bot - Content Router
#  Copyright (c) 2025 SIRIUS Alpha
# ══════════════════════════════════════════════════════════════════════════════
"""
Content routing system for Discord channel selection.

This module provides explicit, configurable routing of different content types
to their appropriate Discord channels. It separates:
- Market intelligence (digests, premarket, journal) → Market channels
- System notifications (errors, health, alerts) → Admin/ops channels
- Bot logs and status → Bot log channels

This prevents the common issue of market reports being sent to admin channels
and vice versa.
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    import discord

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# CONTENT TYPES
# ══════════════════════════════════════════════════════════════════════════════


class ContentType(Enum):
    """Types of content that can be posted to Discord."""

    # Market Intelligence (public-facing, valuable content)
    DIGEST = "digest"  # Daily market digests
    PREMARKET = "premarket"  # Pre-market analysis plans
    JOURNAL = "journal"  # Trading journal entries
    RESEARCH = "research"  # Research reports
    CHART = "chart"  # Chart images and analysis
    ALERT = "alert"  # Market alerts (price, news)

    # System Notifications (admin/ops)
    SYSTEM_ERROR = "system_error"  # Error notifications
    SYSTEM_HEALTH = "system_health"  # Health check results
    SYSTEM_REPORT = "system_report"  # Generated reports (for review)
    AUDIT = "audit"  # Audit logs

    # Bot Operations (internal)
    BOT_LOG = "bot_log"  # Bot operational logs
    BOT_STATUS = "bot_status"  # Bot status updates
    BOT_COMMAND = "bot_command"  # Command responses

    # Fallback
    UNKNOWN = "unknown"


# ══════════════════════════════════════════════════════════════════════════════
# CHANNEL ROUTING
# ══════════════════════════════════════════════════════════════════════════════

# Default channel routing map
# Format: ContentType -> channel name (must match self_guide.py channel names)
DEFAULT_ROUTING: Dict[ContentType, str] = {
    # Market Intelligence → Public channels
    ContentType.DIGEST: "📊-daily-digests",
    ContentType.PREMARKET: "📈-premarket-plans",
    ContentType.JOURNAL: "📔-trading-journal",
    ContentType.RESEARCH: "📚-research-journal",
    ContentType.CHART: "📈-day-charts",
    ContentType.ALERT: "🚨-alerts",
    # System Notifications → Admin channels
    ContentType.SYSTEM_ERROR: "🤖-bot-logs",
    ContentType.SYSTEM_HEALTH: "📋-admin-commands",
    ContentType.SYSTEM_REPORT: "📥-reports",
    ContentType.AUDIT: "📋-admin-commands",
    # Bot Operations → Bot logs
    ContentType.BOT_LOG: "🤖-bot-logs",
    ContentType.BOT_STATUS: "🤖-bot-logs",
    ContentType.BOT_COMMAND: "📋-bot-commands",
    # Fallback
    ContentType.UNKNOWN: "🤖-bot-logs",
}

# Content type groupings for bulk operations
MARKET_INTEL_TYPES = {
    ContentType.DIGEST,
    ContentType.PREMARKET,
    ContentType.JOURNAL,
    ContentType.RESEARCH,
    ContentType.CHART,
    ContentType.ALERT,
}

SYSTEM_TYPES = {
    ContentType.SYSTEM_ERROR,
    ContentType.SYSTEM_HEALTH,
    ContentType.SYSTEM_REPORT,
    ContentType.AUDIT,
}

BOT_TYPES = {
    ContentType.BOT_LOG,
    ContentType.BOT_STATUS,
    ContentType.BOT_COMMAND,
}


@dataclass
class RoutingResult:
    """Result of a content routing decision."""

    content_type: ContentType
    channel_name: str
    is_market_intel: bool
    is_system: bool
    is_bot: bool
    fallback_used: bool = False


class ContentRouter:
    """
    Routes content to appropriate Discord channels.

    Features:
    - Explicit routing rules prevent misrouting
    - Environment variable overrides for flexibility
    - Fallback handling with logging
    - Channel health awareness
    """

    def __init__(
        self,
        routing_overrides: Optional[Dict[ContentType, str]] = None,
        fallback_channel: str = "🤖-bot-logs",
    ):
        """
        Initialize the content router.

        Args:
            routing_overrides: Custom routing rules to override defaults
            fallback_channel: Channel to use when routing fails
        """
        self.routing = DEFAULT_ROUTING.copy()
        self.fallback_channel = fallback_channel

        # Apply overrides
        if routing_overrides:
            self.routing.update(routing_overrides)

        # Load environment overrides
        self._load_env_overrides()

        # Track channel health
        self._channel_health: Dict[str, bool] = {}

    def _load_env_overrides(self) -> None:
        """Load routing overrides from environment variables."""
        # Format: DISCORD_ROUTE_<CONTENT_TYPE>=channel_name
        # Example: DISCORD_ROUTE_DIGEST=my-custom-digest-channel
        for ct in ContentType:
            env_key = f"DISCORD_ROUTE_{ct.name}"
            channel = os.getenv(env_key)
            if channel:
                self.routing[ct] = channel
                logger.info(f"Routing override from env: {ct.name} -> {channel}")

    def route(self, content_type: ContentType) -> RoutingResult:
        """
        Determine the appropriate channel for content.

        Args:
            content_type: Type of content to route

        Returns:
            RoutingResult with channel and metadata
        """
        channel_name = self.routing.get(content_type)
        fallback_used = False

        if not channel_name:
            logger.warning(f"No routing for {content_type}, using fallback")
            channel_name = self.fallback_channel
            fallback_used = True

        return RoutingResult(
            content_type=content_type,
            channel_name=channel_name,
            is_market_intel=content_type in MARKET_INTEL_TYPES,
            is_system=content_type in SYSTEM_TYPES,
            is_bot=content_type in BOT_TYPES,
            fallback_used=fallback_used,
        )

    def get_channel_name(self, content_type: ContentType) -> str:
        """
        Get the channel name for a content type.

        Args:
            content_type: Type of content

        Returns:
            Channel name string
        """
        return self.route(content_type).channel_name

    async def get_channel(
        self,
        guild: "discord.Guild",
        content_type: ContentType,
    ) -> Optional["discord.TextChannel"]:
        """
        Get the Discord channel object for a content type.

        Args:
            guild: Discord guild
            content_type: Type of content

        Returns:
            Discord TextChannel or None if not found
        """
        import discord

        routing = self.route(content_type)
        channel_name = routing.channel_name

        # Try exact match first
        channel = discord.utils.get(guild.text_channels, name=channel_name)

        if channel:
            self._channel_health[channel_name] = True
            return channel

        # Log missing channel
        logger.warning(f"Channel not found: {channel_name} for {content_type.name}")
        self._channel_health[channel_name] = False

        # Try fallback if not already using it
        if not routing.fallback_used:
            fallback = discord.utils.get(guild.text_channels, name=self.fallback_channel)
            if fallback:
                logger.info(f"Using fallback channel: {self.fallback_channel}")
                return fallback

        return None

    def mark_channel_unhealthy(self, channel_name: str) -> None:
        """Mark a channel as unhealthy (send failed)."""
        self._channel_health[channel_name] = False
        logger.warning(f"Channel marked unhealthy: {channel_name}")

    def mark_channel_healthy(self, channel_name: str) -> None:
        """Mark a channel as healthy (send succeeded)."""
        self._channel_health[channel_name] = True

    def is_channel_healthy(self, channel_name: str) -> bool:
        """Check if a channel is healthy."""
        return self._channel_health.get(channel_name, True)

    def get_all_market_intel_channels(self) -> List[str]:
        """Get all channel names used for market intelligence."""
        return list({self.routing[ct] for ct in MARKET_INTEL_TYPES if ct in self.routing})

    def get_all_system_channels(self) -> List[str]:
        """Get all channel names used for system notifications."""
        return list({self.routing[ct] for ct in SYSTEM_TYPES if ct in self.routing})

    def get_routing_table(self) -> Dict[str, str]:
        """Get the complete routing table as strings."""
        return {ct.name: ch for ct, ch in self.routing.items()}


# ══════════════════════════════════════════════════════════════════════════════
# CONTENT TYPE DETECTION
# ══════════════════════════════════════════════════════════════════════════════


def detect_content_type(
    filename: Optional[str] = None,
    doc_type: Optional[str] = None,
    content: Optional[str] = None,
) -> ContentType:
    """
    Detect the content type from various inputs.

    Args:
        filename: Filename of the document
        doc_type: Document type (from frontmatter)
        content: Content to analyze

    Returns:
        Detected ContentType
    """
    import re

    # Priority 1: doc_type from frontmatter
    if doc_type:
        type_map = {
            "journal": ContentType.JOURNAL,
            "Pre-Market": ContentType.PREMARKET,
            "premarket": ContentType.PREMARKET,
            "research": ContentType.RESEARCH,
            "reports": ContentType.DIGEST,  # General reports go to digest
            "analysis": ContentType.RESEARCH,
            "insights": ContentType.RESEARCH,
            "charts": ContentType.CHART,
            "economic": ContentType.RESEARCH,
            "institutional": ContentType.RESEARCH,
            "alerts": ContentType.ALERT,
            "announcements": ContentType.ALERT,
        }
        if doc_type.lower() in type_map or doc_type in type_map:
            return type_map.get(doc_type.lower(), type_map.get(doc_type, ContentType.UNKNOWN))

    # Priority 2: Filename patterns
    if filename:
        patterns = [
            (r"^Journal_", ContentType.JOURNAL),
            (r"^journal_", ContentType.JOURNAL),
            (r"^premarket_", ContentType.PREMARKET),
            (r"^pre_market_", ContentType.PREMARKET),
            (r"^digest_", ContentType.DIGEST),
            (r"^daily_", ContentType.DIGEST),
            (r"^research_", ContentType.RESEARCH),
            (r"^catalyst", ContentType.RESEARCH),
            (r"^chart_", ContentType.CHART),
            (r"_chart\.", ContentType.CHART),
            (r"^alert_", ContentType.ALERT),
            (r"^health_", ContentType.SYSTEM_HEALTH),
            (r"^error_", ContentType.SYSTEM_ERROR),
            (r"^audit_", ContentType.AUDIT),
        ]
        for pattern, ctype in patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return ctype

    # Priority 3: Content keywords (basic heuristics)
    if content:
        content_lower = content.lower()
        if "error" in content_lower and "traceback" in content_lower:
            return ContentType.SYSTEM_ERROR
        if "health check" in content_lower or "status:" in content_lower:
            return ContentType.SYSTEM_HEALTH
        if "pre-market" in content_lower or "premarket" in content_lower:
            return ContentType.PREMARKET
        if "trading journal" in content_lower:
            return ContentType.JOURNAL

    return ContentType.UNKNOWN


# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ══════════════════════════════════════════════════════════════════════════════

# Global router instance (can be replaced for testing)
_router: Optional[ContentRouter] = None


def get_router() -> ContentRouter:
    """Get the global content router instance."""
    global _router
    if _router is None:
        _router = ContentRouter()
    return _router


def set_router(router: ContentRouter) -> None:
    """Set the global content router instance."""
    global _router
    _router = router


# ══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════


def get_channel_for_content(content_type: ContentType) -> str:
    """Get the channel name for a content type."""
    return get_router().get_channel_name(content_type)


def is_market_intel(content_type: ContentType) -> bool:
    """Check if content type is market intelligence."""
    return content_type in MARKET_INTEL_TYPES


def is_system_notification(content_type: ContentType) -> bool:
    """Check if content type is a system notification."""
    return content_type in SYSTEM_TYPES


if __name__ == "__main__":
    # Test the routing
    router = ContentRouter()
    print("Content Routing Table:")
    print("-" * 50)
    for ct in ContentType:
        result = router.route(ct)
        marker = "📊" if result.is_market_intel else ("⚙️" if result.is_system else "🤖")
        print(f"  {marker} {ct.name:20} -> {result.channel_name}")
