"""
Language-specific rule engine
Applies boost/suppress weights to model predictions
"""

import re
import math
from typing import List, Dict, Tuple, Optional
import numpy as np


class NoMeanFilter:
    """
    Filter for detecting and suppressing meaningless text.
    Detects spam, keyboard mashing, and low-entropy sequences.
    """
    
    def __init__(
        self,
        min_entropy: float = 2.0,
        max_repetition_ratio: float = 0.5,
        min_confidence: float = 0.1,
        blocked_patterns: Optional[List[str]] = None
    ):
        self.min_entropy = min_entropy
        self.max_repetition_ratio = max_repetition_ratio
        self.min_confidence = min_confidence
        self.blocked_patterns = blocked_patterns or []
        
        # Compile regex patterns
        self.compiled_patterns = [
            re.compile(pattern) for pattern in self.blocked_patterns
        ]
    
    def calculate_entropy(self, text: str) -> float:
        """
        Calculate Shannon entropy of text.
        
        Args:
            text: Input text
        
        Returns:
            Entropy value
        """
        if not text:
            return 0.0
        
        # Count character frequencies
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        # Calculate entropy
        length = len(text)
        entropy = 0.0
        
        for count in char_counts.values():
            prob = count / length
            entropy -= prob * math.log2(prob)
        
        return entropy
    
    def calculate_repetition_ratio(self, text: str) -> float:
        """
        Calculate ratio of most common character.
        
        Args:
            text: Input text
        
        Returns:
            Repetition ratio (0-1)
        """
        if not text:
            return 0.0
        
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        max_count = max(char_counts.values())
        return max_count / len(text)
    
    def matches_blocked_pattern(self, text: str) -> bool:
        """Check if text matches any blocked pattern"""
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True
        return False
    
    def is_meaningful(self, text: str, confidence: float = 1.0) -> bool:
        """
        Check if text is meaningful.
        
        Args:
            text: Input text
            confidence: Model confidence score
        
        Returns:
            True if meaningful, False otherwise
        """
        # Check confidence threshold
        if confidence < self.min_confidence:
            return False
        
        # Check blocked patterns
        if self.matches_blocked_pattern(text):
            return False
        
        # Check entropy
        entropy = self.calculate_entropy(text)
        if entropy < self.min_entropy:
            return False
        
        # Check repetition
        repetition = self.calculate_repetition_ratio(text)
        if repetition > self.max_repetition_ratio:
            return False
        
        return True


class LanguageRuleEngine:
    """
    Apply language-specific rules to model predictions.
    Boosts or suppresses tokens based on language configuration.
    """
    
    def __init__(self, rules_config: Dict):
        self.rules_config = rules_config
        self.no_mean_filter = self._create_no_mean_filter()
    
    def _create_no_mean_filter(self) -> NoMeanFilter:
        """Create no-mean filter from config"""
        filter_config = self.rules_config.get('no_mean_filter', {})
        
        return NoMeanFilter(
            min_entropy=filter_config.get('min_entropy', 2.0),
            max_repetition_ratio=filter_config.get('max_repetition_ratio', 0.5),
            min_confidence=filter_config.get('min_confidence', 0.1),
            blocked_patterns=filter_config.get('blocked_patterns', [])
        )
    
    def get_language_rules(self, language: str) -> Dict:
        """Get rules for specific language"""
        languages = self.rules_config.get('languages', {})
        return languages.get(language, {})
    
    def apply_rules(
        self,
        logits: np.ndarray,
        token_ids: List[int],
        token_pieces: List[str],
        language: str = "en"
    ) -> np.ndarray:
        """
        Apply language-specific rules to logits.
        
        Args:
            logits: Model output logits (vocab_size,)
            token_ids: Token IDs corresponding to logits
            token_pieces: Token pieces (strings)
            language: Language code
        
        Returns:
            Modified logits
        """
        rules = self.get_language_rules(language)
        if not rules:
            return logits
        
        # Get boost and suppress tokens
        boost_tokens = rules.get('boost_tokens', [])
        suppress_tokens = rules.get('suppress_tokens', [])
        boost_weight = rules.get('boost_weight', 0.5)
        suppress_weight = rules.get('suppress_weight', -1.0)
        
        # Apply boosts
        for i, piece in enumerate(token_pieces):
            if piece in boost_tokens:
                logits[i] += boost_weight
            elif piece in suppress_tokens:
                logits[i] += suppress_weight
        
        return logits
    
    def filter_predictions(
        self,
        predictions: List[Tuple[str, float]],
        language: str = "en"
    ) -> List[Tuple[str, float]]:
        """
        Filter predictions using no-mean filter.
        
        Args:
            predictions: List of (text, confidence) tuples
            language: Language code
        
        Returns:
            Filtered predictions
        """
        filtered = []
        
        for text, confidence in predictions:
            if self.no_mean_filter.is_meaningful(text, confidence):
                filtered.append((text, confidence))
        
        return filtered
    
    def get_emoji_frequency(self, language: str) -> str:
        """Get emoji frequency setting for language"""
        rules = self.get_language_rules(language)
        return rules.get('emoji_frequency', 'medium')
    
    def should_boost_emoji(self, language: str) -> bool:
        """Check if emoji should be boosted for language"""
        freq = self.get_emoji_frequency(language)
        return freq == 'high'
    
    def get_formality_level(self, language: str) -> str:
        """Get formality level for language"""
        rules = self.get_language_rules(language)
        return rules.get('formality', 'casual')


if __name__ == "__main__":
    import sys
    sys.path.append('src')
    from utils.config_loader import get_language_rules
    
    # Load rules
    rules_config = get_language_rules()
    
    # Create rule engine
    engine = LanguageRuleEngine(rules_config)
    
    # Test no-mean filter
    print("Testing No-Mean Filter:")
    print("-" * 50)
    
    test_cases = [
        ("hello world", 0.9, True),
        ("xdxd123", 0.8, False),
        ("asdfghjkl", 0.7, False),
        ("zzzzzzzzz", 0.6, False),
        ("I love you", 0.95, True),
        ("test", 0.05, False),  # Low confidence
    ]
    
    for text, confidence, expected in test_cases:
        is_meaningful = engine.no_mean_filter.is_meaningful(text, confidence)
        status = "✓" if is_meaningful == expected else "✗"
        print(f"{status} '{text}' (conf: {confidence:.2f}) -> {is_meaningful}")
    
    # Test rule application
    print("\n\nTesting Rule Application:")
    print("-" * 50)
    
    # Simulate logits
    vocab_size = 10
    logits = np.random.randn(vocab_size)
    token_pieces = ["gonna", "going", "to", "the", "whom", "wanna", "test", "です", "ます", "だ"]
    token_ids = list(range(vocab_size))
    
    print("\nEnglish rules (boost teen slang):")
    en_logits = engine.apply_rules(logits.copy(), token_ids, token_pieces, "en")
    for i, piece in enumerate(token_pieces):
        change = en_logits[i] - logits[i]
        if abs(change) > 0.01:
            print(f"  '{piece}': {logits[i]:.2f} -> {en_logits[i]:.2f} ({change:+.2f})")
    
    print("\nJapanese rules (boost polite forms):")
    ja_logits = engine.apply_rules(logits.copy(), token_ids, token_pieces, "ja")
    for i, piece in enumerate(token_pieces):
        change = ja_logits[i] - logits[i]
        if abs(change) > 0.01:
            print(f"  '{piece}': {logits[i]:.2f} -> {ja_logits[i]:.2f} ({change:+.2f})")
