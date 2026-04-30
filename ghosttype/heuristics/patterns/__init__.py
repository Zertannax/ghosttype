"""Pattern definitions for heuristic detection."""

from ghosttype.heuristics.patterns.buzzwords import PATTERNS as BUZZWORDS
from ghosttype.heuristics.patterns.hedges import PATTERNS as HEDGES
from ghosttype.heuristics.patterns.openers import PATTERNS as OPENERS

ALL_PATTERNS = OPENERS + HEDGES + BUZZWORDS
