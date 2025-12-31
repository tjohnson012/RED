"""
Attack library aggregator.
"""

from .jailbreaks import JAILBREAK_ATTACKS
from .injections import INJECTION_ATTACKS
from .extractions import EXTRACTION_ATTACKS
from .encoding import ENCODING_ATTACKS
from .chains import CHAIN_ATTACKS

# Combine all attacks
ALL_ATTACKS = (
    JAILBREAK_ATTACKS +
    INJECTION_ATTACKS +
    EXTRACTION_ATTACKS +
    ENCODING_ATTACKS
)

# Chain attacks are handled separately due to multi-step nature
ALL_CHAIN_ATTACKS = CHAIN_ATTACKS


def get_attacks_by_category(category: str) -> list:
    """Get all attacks of a specific category."""
    return [a for a in ALL_ATTACKS if a["category"] == category]


def get_attacks_by_severity(severity: str) -> list:
    """Get all attacks of a specific severity."""
    return [a for a in ALL_ATTACKS if a["severity"] == severity]


def get_attack_by_id(attack_id: str) -> dict:
    """Get a specific attack by ID."""
    for attack in ALL_ATTACKS:
        if attack["id"] == attack_id:
            return attack
    return None
