"""Cross-discipline consensus engine."""

from app.core.consensus.engine import ConsensusEngine, build_consensus_from_channels
from app.core.consensus.schema import ConfidenceBand, ConsensusResult, UnifiedInterpretExtras

__all__ = [
    "ConsensusEngine",
    "ConfidenceBand",
    "ConsensusResult",
    "UnifiedInterpretExtras",
    "build_consensus_from_channels",
]
