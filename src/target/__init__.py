"""
Target LLM application module - the "victim" that RED attacks.
"""

from .chatbot import TargetChatbot
from .system_prompt import SYSTEM_PROMPT, FAKE_CUSTOMER_DATA

__all__ = ["TargetChatbot", "SYSTEM_PROMPT", "FAKE_CUSTOMER_DATA"]
