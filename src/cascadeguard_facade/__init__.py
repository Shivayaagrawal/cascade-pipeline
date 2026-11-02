"""Synthetic facade. Text-only. It does not decode audio."""

from cascadeguard_facade.contracts import STRATEGIES
from cascadeguard_facade.router import route

__all__ = ["STRATEGIES", "route"]
