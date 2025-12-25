#!/usr/bin/env python3
"""
Enhanced Japanese Predictive Text Engine
Uses comprehensive kanji dictionary, grammar patterns, and context analysis
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class EnhancedJapanesePredictiveEngine:
    """Advanced Japanese IME with context-aware kanji suggestions"""
    
    def __init__(self):
        self.kanji_dict = {}
        self.compound_words = {}
        self.grammar_patterns = {}
        self.load_dictionaries()
        
    def load_dictionaries(self):
        """Load all dictionaries"""
        data_dir = Path('data')
        
        # Load kanji dictionary
        kanji_file = data_dir / 'kanji_dictionary.json'
        if kanji_file.exists():
            with open(kanji_file, 'r', encoding='utf-8') as f:
                self.kanji_dict = json.load(f)
        
        # Load compound words
        compound_file = data_dir / 'compound_words.json'
        if compound_file.exists():
            with open(compound_file, 'r', encoding='utf-8') as f:
                self.compound_words = json.load(f)
        
        # Load grammar patterns
        grammar_file = data_dir / 'grammar_patterns.json'
        if grammar_file.exists():
            with open(grammar_file, 'r', encoding='utf-8') as f:
                self.grammar_patterns = json.load(f)
    
    def get_predictions(self, hiragana_input: str, context: Optional[Dict] = None) -> List[str]:
        """
        Get predictions for hiragana input with optional context
        
        Args:
            hiragana_input: Hiragana string to convert
            context: Optional context dict with 'preceding_text', 'following_text', etc.
        
        Returns:
            List of suggestions (kanji + hiragana options)
        """
        suggestions = []
        
        # Step 1: Check compound words first (highest priority)
        if hiragana_input in self.compound_words:
            suggestions.extend(self.compound_words[hiragana_input])
        
        # Step 2: Check kanji dictionary
        if hiragana_input in self.kanji_dict:
            kanji_options = self.kanji_dict[hiragana_input]["options"]
            
            # If context provided, reorder based on context
            if context:
                kanji_options = self.reorder_by_context(kanji_options, context)
            
            # Add kanji suggestions
            for option in kanji_options:
                if option["kanji"] not in suggestions:
                    suggestions.append(option["kanji"])
        
        # Step 3: Always include hiragana as fallback
        if hiragana_input not in suggestions:
            suggestions.append(hiragana_input)
        
        return suggestions[:10]  # Return top 10
    
    def reorder_by_context(self, kanji_options: List[Dict], context: Dict) -> List[Dict]:
        """
        Reorder kanji options based on context
        
        Args:
            kanji_options: List of kanji option dicts
            context: Context information
        
        Returns:
            Reordered list of kanji options
        """
        preceding_text = context.get('preceding_text', '').lower()
        following_text = context.get('following_text', '').lower()
        
        # Score each option based on context
        scored_options = []
        for option in kanji_options:
            score = option.get('frequency', 0)
            
            # Boost score if context matches
            context_tags = option.get('context', [])
            for tag in context_tags:
                tag_lower = tag.lower()
                if tag_lower in preceding_text or tag_lower in following_text:
                    score += 500  # Significant boost for context match
            
            # Check for specific context patterns
            if preceding_text:
                score += self.analyze_preceding_context(preceding_text, option)
            
            if following_text:
                score += self.analyze_following_context(following_text, option)
            
            scored_options.append((score, option))
        
        # Sort by score (descending)
        scored_options.sort(key=lambda x: x[0], reverse=True)
        
        return [opt for score, opt in scored_options]
    
    def analyze_preceding_context(self, preceding: str, option: Dict) -> int:
        """Analyze preceding text for context clues"""
        score = 0
        kanji = option.get('kanji', '')
        
        # Religious context
        if any(word in preceding for word in ['祈り', 'お祈り', '神社', '寺']) and kanji == '神':
            score += 1000
        
        # Paper/printing context
        if any(word in preceding for word in ['印刷', '紙', '書類', '文書']) and kanji == '紙':
            score += 1000
        
        # Beauty/hair context
        if any(word in preceding for word in ['美容', '髪', 'ヘア']) and kanji == '髪':
            score += 1000
        
        # River/bridge context
        if any(word in preceding for word in ['川', '河', '橋']) and kanji == '橋':
            score += 1000
        
        # Meal/eating context
        if any(word in preceding for word in ['食事', '食べ', 'ご飯', '料理']) and kanji == '箸':
            score += 1000
        
        # Weather context
        if any(word in preceding for word in ['天気', '今日', '明日', '雨']) and kanji == '雨':
            score += 1000
        
        # Children/candy context
        if any(word in preceding for word in ['子供', '子ども', '甘い']) and kanji == '飴':
            score += 1000
        
        # Music context
        if any(word in preceding for word in ['音楽', 'コンサート', '曲']) and kanji == '聴く':
            score += 1000
        
        # Medical context
        if any(word in preceding for word in ['患者', '病院', '医者', '診察']) and kanji == '診る':
            score += 1000
        
        # Door/opening context
        if any(word in preceding for word in ['ドア', '窓', '扉']) and kanji == '開ける':
            score += 1000
        
        # Summer/weather context
        if any(word in preceding for word in ['夏', '天気', '気温']) and kanji == '暑い':
            score += 1000
        
        # Hot water/temperature context
        if any(word in preceding for word in ['お湯', '水', '温度']) and kanji == '熱い':
            score += 1000
        
        # Morning/time context
        if any(word in preceding for word in ['朝', '時間', '早朝']) and kanji == '早い':
            score += 1000
        
        # Speed context
        if any(word in preceding for word in ['新幹線', 'スピード', '速度']) and kanji == '速い':
            score += 1000
        
        # Science context
        if any(word in preceding for word in ['研究', '科学者', '理論']) and kanji == '科学':
            score += 1000
        
        # Chemistry context
        if any(word in preceding for word in ['実験', '化学式', '反応']) and kanji == '化学':
            score += 1000
        
        # Name context
        if any(word in preceding for word in ['田中', 'さん', '先生']) and kanji == '佐藤':
            score += 1000
        
        # Coffee/sugar context
        if any(word in preceding for word in ['コーヒー', '紅茶', '甘い']) and kanji == '砂糖':
            score += 1000
        
        # Compound word context (学 + せい = 学生)
        if preceding.endswith('学') and kanji == '生':
            score += 2000
        if preceding.endswith('男') and kanji == '性':
            score += 2000
        if preceding.endswith('完') and kanji == '成':
            score += 2000
        if preceding.endswith('思') and kanji == '考':
            score += 2000
        if preceding.endswith('小中') and kanji == '高':
            score += 2000
        if preceding.endswith('都') and kanji == '市':
            score += 2000
        if preceding.endswith('教') and kanji == '師':
            score += 2000
        if preceding.endswith('東') and kanji == '京':
            score += 2000
        
        return score
    
    def analyze_following_context(self, following: str, option: Dict) -> int:
        """Analyze following text for context clues"""
        score = 0
        kanji = option.get('kanji', '')
        
        # Following context (政 + 府 = 政府)
        if following.startswith('府') and kanji == '政':
            score += 2000
        
        return score
    
    def get_context_from_text(self, full_text: str, cursor_position: int) -> Dict:
        """
        Extract context from full text and cursor position
        
        Args:
            full_text: Complete text
            cursor_position: Current cursor position
        
        Returns:
            Context dict with preceding and following text
        """
        preceding = full_text[:cursor_position]
        following = full_text[cursor_position:]
        
        # Get last few characters for context
        preceding_context = preceding[-20:] if len(preceding) > 20 else preceding
        following_context = following[:20] if len(following) > 20 else following
        
        return {
            'preceding_text': preceding_context,
            'following_text': following_context,
            'sentence_start': cursor_position == 0 or preceding.endswith('。')
        }


def main():
    """Test the enhanced prediction engine"""
    
    print("="*70)
    print("ENHANCED JAPANESE PREDICTIVE TEXT ENGINE - TEST")
    print("="*70)
    print()
    
    engine = EnhancedJapanesePredictiveEngine()
    
    # Test cases
    test_cases = [
        ("かみ", None, "No context"),
        ("かみ", {"preceding_text": "お祈りをして"}, "After 'praying'"),
        ("かみ", {"preceding_text": "印刷する"}, "After 'printing'"),
        ("かみ", {"preceding_text": "美容院で"}, "After 'beauty salon'"),
        ("はし", {"preceding_text": "川に"}, "After 'river'"),
        ("はし", {"preceding_text": "食事で"}, "After 'meal'"),
        ("きく", {"preceding_text": "音楽を"}, "After 'music'"),
        ("みる", {"preceding_text": "映画を"}, "After 'movie'"),
        ("あつい", {"preceding_text": "夏は"}, "After 'summer'"),
        ("あつい", {"preceding_text": "お湯が"}, "After 'hot water'"),
        ("せい", {"preceding_text": "学"}, "After '学' (compound)"),
        ("せい", {"preceding_text": "男"}, "After '男' (compound)"),
        ("がっこう", None, "Compound word"),
        ("こんにちは", None, "Greeting"),
    ]
    
    for hiragana, context, description in test_cases:
        predictions = engine.get_predictions(hiragana, context)
        print(f"Input: '{hiragana}' ({description})")
        print(f"  → {predictions[:5]}")
        print()
    
    print("="*70)
    print("✅ Test complete!")
    print("="*70)


if __name__ == '__main__':
    main()
