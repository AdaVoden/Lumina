"""Analytics and reporting for follower data."""
import logging
from pydantic import BaseModel, Field
from typing import Optional

from bluesky_service import FollowerData, is_active_in_window
from config import config

logger = logging.getLogger(__name__)

class FollowerStats(BaseModel):
    """Statistics about followers"""
    total_followers: int = Field(..., ge=0, description="Total followers account has")
    enabled_count: int = Field(..., ge=0, description="Accounts still enabled")
    disabled_count: int = Field(..., ge=0, description="Accounts disabled or deleted")
    active_count: int = Field(..., ge=0, description="Number of accounts which posted recently")
    ghost_count: int = Field(..., ge=0, description="Number of accounts that have never posted")
    active_percentage: float = Field(..., ge=0, description="Percentage of active followers")

class SnapshotReport(BaseModel):
    """Complete report for a snapshot"""
    stats: FollowerStats = Field(..., description="Stats for followers")
    new_followers: dict[str, str] = Field(..., description="List of new followers by did:handle")
    unfollowers: dict[str, str] = Field(..., description="List of users who unfollowed by did:handle")
    follows_count: int = Field(..., ge=0, description="Number of follows account has")

class AnalyticsService:
    """Service for analyzing follower data"""

    @staticmethod
    def calculate_stats(total_followers: int, followers: list[FollowerData]) -> FollowerStats:
        """Calculate statistics from follower data"""
        enabled_count = len(followers)
        disabled_count = total_followers - enabled_count
        active_count = 0
        ghost_count = 0

        for follower in followers:
            if follower.last_posted_at:
                if is_active_in_window(follower.last_posted_at, config.ACTIVITY_WINDOW_DAYS):
                    active_count += 1
                else:
                    ghost_count += 1
        
        active_percentage = (active_count / total_followers) * 100 if total_followers > 0 else 0

        return FollowerStats(
            total_followers=total_followers,
            enabled_count=enabled_count,
            disabled_count=disabled_count,
            active_count=active_count,
            ghost_count=ghost_count,
            active_percentage=active_percentage
        )

    @staticmethod
    def format_report(report: SnapshotReport) -> str:
        """Format a report as a string"""
        lines = [
            "=" * 50,
            "FOLLOWER REPORT",
            "=" * 50,
            "",
            f"Total Followers: {report.stats.total_followers}",
            f"Follows: {report.follows_count}",
            "",
            "=" * 50,
            "FOLLOWER BREAKDOWN",
            "=" * 50,
            f"Enabled Accounts: {report.stats.enabled_count}",
            f"Disabled Accounts: {report.stats.disabled_count}",
            f"Active (posted in last {config.ACTIVITY_WINDOW_DAYS} days): {report.stats.active_count}",
            f"Active Percentage: {report.stats.active_percentage:.2f}%",
            f"Never Posted: {report.stats.ghost_count}",
            "",
        ]

        if report.new_followers:
            lines.extend([
                "=" * 50,
                f"NEW FOLLOWERS ({len(report.new_followers)})",
                "=" * 50,
            ])
            for did, handle in report.new_followers.items():
                lines.append(f"  + {handle}")
            lines.append("")

        if report.new_followers:
            lines.extend([
                "=" * 50,
                f"UNFOLLOWS ({len(report.unfollowers)})",
                "=" * 50,
            ])
            for did, handle in report.unfollowers.items():
                lines.append(f"  - {handle}")
            lines.append("")

        if not report.new_followers and not report.unfollowers:
            lines.extend([
                "=" * 50,
                "CHANGES",
                "=" * 50,
                "No new followers or unfollows since last snapshot.",
                ""
            ])
        
        return "\n".join(lines)

    @staticmethod
    def print_report(report: SnapshotReport):
        """Print a formatted report"""
        print(AnalyticsService.format_report(report))