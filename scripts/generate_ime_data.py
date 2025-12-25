#!/usr/bin/env python3
"""
Japanese IME Training Data Generator
Creates training data specifically for Japanese keyboard IME behavior.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

class JapaneseIMEDataGenerator:
    """Generate IME-specific training data"""
    
    def __init__(self):
        self.data_dir = Path('data/japanese')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Romaji to Hiragana mapping
        self.romaji_map = self.create_romaji_map()
        
        # Training examples
        self.examples = []
        
    def create_romaji_map(self) -> Dict[str, str]:
        """Create comprehensive romaji to hiragana mapping"""
        return {
            # Vowels
            'a': 'あ', 'i': 'い', 'u': 'う', 'e': 'え', 'o': 'お',
            
            # K-row
            'ka': 'か', 'ki': 'き', 'ku': 'く', 'ke': 'け', 'ko': 'こ',
            'kya': 'きゃ', 'kyu': 'きゅ', 'kyo': 'きょ',
            
            # S-row
            'sa': 'さ', 'shi': 'し', 'su': 'す', 'se': 'せ', 'so': 'そ',
            'sha': 'しゃ', 'shu': 'しゅ', 'sho': 'しょ',
            
            # T-row
            'ta': 'た', 'chi': 'ち', 'tsu': 'つ', 'te': 'て', 'to': 'と',
            'cha': 'ちゃ', 'chu': 'ちゅ', 'cho': 'ちょ',
            
            # N-row
            'na': 'な', 'ni': 'に', 'nu': 'ぬ', 'ne': 'ね', 'no': 'の',
            'nya': 'にゃ', 'nyu': 'にゅ', 'nyo': 'にょ',
            
            # H-row
            'ha': 'は', 'hi': 'ひ', 'fu': 'ふ', 'he': 'へ', 'ho': 'ほ',
            'hya': 'ひゃ', 'hyu': 'ひゅ', 'hyo': 'ひょ',
            
            # M-row
            'ma': 'ま', 'mi': 'み', 'mu': 'む', 'me': 'め', 'mo': 'も',
            'mya': 'みゃ', 'myu': 'みゅ', 'myo': 'みょ',
            
            # Y-row
            'ya': 'や', 'yu': 'ゆ', 'yo': 'よ',
            
            # R-row
            'ra': 'ら', 'ri': 'り', 'ru': 'る', 're': 'れ', 'ro': 'ろ',
            'rya': 'りゃ', 'ryu': 'りゅ', 'ryo': 'りょ',
            
            # W-row
            'wa': 'わ', 'wo': 'を', 'n': 'ん',
            
            # G-row
            'ga': 'が', 'gi': 'ぎ', 'gu': 'ぐ', 'ge': 'げ', 'go': 'ご',
            'gya': 'ぎゃ', 'gyu': 'ぎゅ', 'gyo': 'ぎょ',
            
            # Z-row
            'za': 'ざ', 'ji': 'じ', 'zu': 'ず', 'ze': 'ぜ', 'zo': 'ぞ',
            'ja': 'じゃ', 'ju': 'じゅ', 'jo': 'じょ',
            
            # D-row
            'da': 'だ', 'di': 'ぢ', 'du': 'づ', 'de': 'で', 'do': 'ど',
            
            # B-row
            'ba': 'ば', 'bi': 'び', 'bu': 'ぶ', 'be': 'べ', 'bo': 'ぼ',
            'bya': 'びゃ', 'byu': 'びゅ', 'byo': 'びょ',
            
            # P-row
            'pa': 'ぱ', 'pi': 'ぴ', 'pu': 'ぷ', 'pe': 'ぺ', 'po': 'ぽ',
            'pya': 'ぴゃ', 'pyu': 'ぴゅ', 'pyo': 'ぴょ',
        }
    
    def romaji_to_hiragana(self, romaji: str) -> str:
        """Convert romaji to hiragana"""
        result = []
        i = 0
        romaji = romaji.lower()
        
        while i < len(romaji):
            # Try 3-char match first
            if i + 3 <= len(romaji):
                three = romaji[i:i+3]
                if three in self.romaji_map:
                    result.append(self.romaji_map[three])
                    i += 3
                    continue
            
            # Try 2-char match
            if i + 2 <= len(romaji):
                two = romaji[i:i+2]
                if two in self.romaji_map:
                    result.append(self.romaji_map[two])
                    i += 2
                    continue
            
            # Try 1-char match
            one = romaji[i]
            if one in self.romaji_map:
                result.append(self.romaji_map[one])
            else:
                result.append(one)  # Keep as-is if not found
            i += 1
        
        return ''.join(result)
    
    def generate_common_words(self):
        """Generate common Japanese word examples"""
        print("📝 Generating common word examples...")
        
        # Common words with romaji, hiragana, and kanji
        common_words = [
            # Greetings
            ('konnichiwa', 'こんにちは', ['こんにちは', '今日は']),
            ('arigatou', 'ありがとう', ['ありがとう', '有難う', '有り難う']),
            ('ohayou', 'おはよう', ['おはよう', 'お早う']),
            ('konbanwa', 'こんばんは', ['こんばんは', '今晩は']),
            ('sayonara', 'さよなら', ['さよなら', '左様なら']),
            ('sumimasen', 'すみません', ['すみません', '済みません']),
            
            # Common nouns
            ('nihongo', 'にほんご', ['日本語', 'にほんご']),
            ('nihon', 'にほん', ['日本', 'にほん']),
            ('tokyo', 'とうきょう', ['東京', 'とうきょう']),
            ('sensei', 'せんせい', ['先生', 'せんせい']),
            ('gakkou', 'がっこう', ['学校', 'がっこう']),
            ('tomodachi', 'ともだち', ['友達', 'ともだち']),
            
            # Pronouns
            ('watashi', 'わたし', ['私', 'わたし']),
            ('anata', 'あなた', ['あなた', '貴方']),
            ('kare', 'かれ', ['彼', 'かれ']),
            ('kanojo', 'かのじょ', ['彼女', 'かのじょ']),
            
            # Verbs
            ('taberu', 'たべる', ['食べる', 'たべる']),
            ('nomu', 'のむ', ['飲む', 'のむ']),
            ('iku', 'いく', ['行く', 'いく']),
            ('kuru', 'くる', ['来る', 'くる']),
            ('miru', 'みる', ['見る', 'みる']),
            ('kiku', 'きく', ['聞く', '聴く', 'きく']),
            ('hanasu', 'はなす', ['話す', 'はなす']),
            ('yomu', 'よむ', ['読む', 'よむ']),
            ('kaku', 'かく', ['書く', 'かく']),
            ('benkyou', 'べんきょう', ['勉強', 'べんきょう']),
            
            # Adjectives
            ('oishii', 'おいしい', ['美味しい', 'おいしい']),
            ('takai', 'たかい', ['高い', '高い']),
            ('yasui', 'やすい', ['安い', 'やすい']),
            ('ookii', 'おおきい', ['大きい', 'おおきい']),
            ('chiisai', 'ちいさい', ['小さい', 'ちいさい']),
            
            # Time
            ('kyou', 'きょう', ['今日', 'きょう']),
            ('ashita', 'あした', ['明日', 'あした']),
            ('kinou', 'きのう', ['昨日', 'きのう']),
            ('ima', 'いま', ['今', 'いま']),
            
            # Numbers
            ('ichi', 'いち', ['一', '1', 'いち']),
            ('ni', 'に', ['二', '2', 'に']),
            ('san', 'さん', ['三', '3', 'さん']),
            ('yon', 'よん', ['四', '4', 'よん']),
            ('go', 'ご', ['五', '5', 'ご']),
        ]
        
        for romaji, hiragana, kanji_list in common_words:
            # Add training examples
            # 1. Romaji input → hiragana suggestion
            self.examples.append(f"{romaji} {hiragana}")
            
            # 2. Hiragana → kanji suggestions
            for kanji in kanji_list:
                self.examples.append(f"{hiragana} {kanji}")
            
            # 3. Partial romaji → completion
            for i in range(2, len(romaji)):
                partial = romaji[:i]
                partial_hiragana = self.romaji_to_hiragana(partial)
                self.examples.append(f"{partial} {partial_hiragana}")
        
        print(f"✅ Generated {len(self.examples)} common word examples")
    
    def generate_katakana_words(self):
        """Generate katakana loanword examples"""
        print("📝 Generating katakana examples...")
        
        start_count = len(self.examples)
        
        katakana_words = [
            ('amerika', 'あめりか', 'アメリカ'),
            ('koohii', 'こーひー', 'コーヒー'),
            ('terebi', 'てれび', 'テレビ'),
            ('konpyuutaa', 'こんぴゅーたー', 'コンピューター'),
            ('intaanetto', 'いんたーねっと', 'インターネット'),
            ('anime', 'あにめ', 'アニメ'),
            ('geemu', 'げーむ', 'ゲーム'),
            ('resutoran', 'れすとらん', 'レストラン'),
            ('hoteru', 'ほてる', 'ホテル'),
            ('takushii', 'たくしー', 'タクシー'),
            ('basu', 'ばす', 'バス'),
            ('densha', 'でんしゃ', 'デンシャ'),
            ('kamera', 'かめら', 'カメラ'),
            ('pasokon', 'ぱそこん', 'パソコン'),
            ('sumaho', 'すまほ', 'スマホ'),
        ]
        
        for romaji, hiragana, katakana in katakana_words:
            self.examples.append(f"{romaji} {katakana}")
            self.examples.append(f"{hiragana} {katakana}")
        
        print(f"✅ Generated {len(self.examples) - start_count} katakana examples")
    
    def generate_from_dictionary(self):
        """Generate examples from existing dictionary data"""
        print("📝 Processing existing dictionary data...")
        
        dict_file = Path('data/processed/comprehensive_train.txt')
        if not dict_file.exists():
            print("⚠️  Dictionary file not found, skipping")
            return
        
        start_count = len(self.examples)
        processed = 0
        
        with open(dict_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or len(line) < 2:
                    continue
                
                # Use dictionary entries as-is for context learning
                self.examples.append(line)
                processed += 1
                
                if processed >= 100000:  # Limit to 100K from dictionary
                    break
        
        print(f"✅ Added {len(self.examples) - start_count} dictionary examples")
    
    def save_training_data(self):
        """Save generated training data"""
        output_file = self.data_dir / 'ime_training.txt'
        
        print(f"\n💾 Saving training data...")
        print(f"   Total examples: {len(self.examples):,}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for example in self.examples:
                f.write(example + '\n')
        
        file_size = output_file.stat().st_size / (1024 * 1024)
        print(f"✅ Saved to: {output_file}")
        print(f"   Size: {file_size:.1f} MB")
        
        # Save statistics
        stats = {
            'total_examples': len(self.examples),
            'file_size_mb': file_size,
            'output_file': str(output_file)
        }
        
        stats_file = self.data_dir / 'ime_stats.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        print(f"📊 Stats saved to: {stats_file}")
    
    def generate_all(self):
        """Generate all training data"""
        print("="*70)
        print("JAPANESE IME TRAINING DATA GENERATION")
        print("="*70)
        print()
        
        # Generate different types of examples
        self.generate_common_words()
        self.generate_katakana_words()
        self.generate_from_dictionary()
        
        # Save
        self.save_training_data()
        
        print()
        print("="*70)
        print("✅ IME TRAINING DATA READY!")
        print("="*70)
        print()
        print("Next steps:")
        print("1. Train Japanese model:")
        print("   python scripts/train_multilang.py --language japanese")
        print()
        print("2. Test against IME cases:")
        print("   python scripts/test_japanese_ime.py")
        print()


def main():
    """Main entry point"""
    generator = JapaneseIMEDataGenerator()
    generator.generate_all()


if __name__ == '__main__':
    main()
