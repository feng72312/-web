from dataclasses import dataclass
from typing import Dict, Union


@dataclass(frozen=True)
class PaipanRules:
    """Configurable paipan rules. Extend fields as new features are added."""

    sect: int = 2
    early_zishi_mode: str = "midnight"

    def as_meta(self) -> Dict[str, Union[str, int]]:
        return {
            "sect": self.sect,
            "earlyZishiMode": self.early_zishi_mode,
            "monthRule": "solar_term",
            "note": "Sect 2: split day at midnight for early zi hour.",
        }
