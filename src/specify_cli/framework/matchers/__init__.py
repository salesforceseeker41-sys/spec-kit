"""Rule matcher abstractions."""

from .base import MatchResult, RuleMatcher
from .keyword_matcher import KeywordMatcher

__all__ = ["KeywordMatcher", "MatchResult", "RuleMatcher"]

