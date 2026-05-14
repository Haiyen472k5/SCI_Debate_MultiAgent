"""Debate agents."""

from .base import BaseAgent
from .pro import ProAgent
from .con import ConAgent
from .judge import JudgeAgent, Verdict

__all__ = ["BaseAgent", "ProAgent", "ConAgent", "JudgeAgent", "Verdict"]