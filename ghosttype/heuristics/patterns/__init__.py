"""Pattern definitions for heuristic detection."""

from ghosttype.heuristics.patterns.academic import PATTERNS as ACADEMIC
from ghosttype.heuristics.patterns.balance import PATTERNS as BALANCE
from ghosttype.heuristics.patterns.buzzwords import PATTERNS as BUZZWORDS
from ghosttype.heuristics.patterns.conversational import PATTERNS as CONVERSATIONAL
from ghosttype.heuristics.patterns.hedges import PATTERNS as HEDGES
from ghosttype.heuristics.patterns.journalist import PATTERNS as JOURNALIST
from ghosttype.heuristics.patterns.openers import PATTERNS as OPENERS
from ghosttype.heuristics.patterns.structure import PATTERNS as STRUCTURE
from ghosttype.heuristics.patterns.technical import PATTERNS as TECHNICAL
from ghosttype.heuristics.patterns.transitions import PATTERNS as TRANSITIONS

ALL_PATTERNS = (
    OPENERS + HEDGES + BUZZWORDS + STRUCTURE + BALANCE + TRANSITIONS +
    JOURNALIST + CONVERSATIONAL + ACADEMIC + TECHNICAL
)
