"""Pattern definitions for heuristic detection."""

from ghosttype.heuristics.patterns.balance import PATTERNS as BALANCE
from ghosttype.heuristics.patterns.buzzwords import PATTERNS as BUZZWORDS
from ghosttype.heuristics.patterns.french_buzzwords import PATTERNS as FRENCH_BUZZWORDS
from ghosttype.heuristics.patterns.french_hedges import PATTERNS as FRENCH_HEDGES
from ghosttype.heuristics.patterns.french_openers import PATTERNS as FRENCH_OPENERS
from ghosttype.heuristics.patterns.hedges import PATTERNS as HEDGES
from ghosttype.heuristics.patterns.openers import PATTERNS as OPENERS
from ghosttype.heuristics.patterns.structure import PATTERNS as STRUCTURE
from ghosttype.heuristics.patterns.transitions import PATTERNS as TRANSITIONS

ALL_PATTERNS = (
    OPENERS + HEDGES + BUZZWORDS + STRUCTURE + BALANCE + TRANSITIONS +
    FRENCH_OPENERS + FRENCH_HEDGES + FRENCH_BUZZWORDS
)
