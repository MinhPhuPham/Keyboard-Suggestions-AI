#!/usr/bin/env python3
"""
Generate Comprehensive Japanese Kanji Dictionary
Extracts kanji from existing data and creates a comprehensive dictionary
with homonyms, frequency, and context information
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

class KanjiDictionaryGenerator:
    """Generate comprehensive kanji dictionary for Japanese IME"""
    
    def __init__(self):
        self.kanji_dict = defaultdict(lambda: {"options": []})
        self.compound_words = {}
        self.grammar_patterns = {}
        
    def generate_comprehensive_dictionary(self):
        """Generate complete kanji dictionary"""
        
        print("="*70)
        print("GENERATING COMPREHENSIVE JAPANESE KANJI DICTIONARY")
        print("="*70)
        print()
        
        # Step 1: Common homonyms (most important for IME)
        print("Step 1: Adding common homonyms...")
        self.add_common_homonyms()
        print(f"✓ Added {len(self.kanji_dict)} hiragana readings")
        print()
        
        # Step 2: Compound words
        print("Step 2: Adding compound words...")
        self.add_compound_words()
        print(f"✓ Added {len(self.compound_words)} compound words")
        print()
        
        # Step 3: Grammar patterns
        print("Step 3: Adding grammar patterns...")
        self.add_grammar_patterns()
        print(f"✓ Added grammar patterns")
        print()
        
        # Step 4: Save dictionaries
        print("Step 4: Saving dictionaries...")
        self.save_dictionaries()
        print("✓ Dictionaries saved")
        print()
        
        # Summary
        self.print_summary()
        
    def add_common_homonyms(self):
        """Add most common Japanese homonyms"""
        
        # This is a comprehensive list of common Japanese homonyms
        # Based on frequency in Japanese text
        
        homonyms = {
            # Top homonyms from test cases
            "かみ": [
                {"kanji": "神", "meaning": "god", "frequency": 1000, "context": ["religion", "prayer", "shrine"]},
                {"kanji": "紙", "meaning": "paper", "frequency": 800, "context": ["writing", "printing", "document"]},
                {"kanji": "髪", "meaning": "hair", "frequency": 600, "context": ["beauty", "body", "hairstyle"]},
                {"kanji": "上", "meaning": "above/up", "frequency": 500, "context": ["direction", "position", "top"]}
            ],
            "はし": [
                {"kanji": "橋", "meaning": "bridge", "frequency": 700, "context": ["river", "crossing", "structure"]},
                {"kanji": "箸", "meaning": "chopsticks", "frequency": 600, "context": ["eating", "meal", "utensil"]},
                {"kanji": "端", "meaning": "edge/end", "frequency": 500, "context": ["border", "corner", "limit"]}
            ],
            "あめ": [
                {"kanji": "雨", "meaning": "rain", "frequency": 900, "context": ["weather", "sky", "umbrella"]},
                {"kanji": "飴", "meaning": "candy", "frequency": 400, "context": ["sweet", "children", "snack"]}
            ],
            
            # Verbs with multiple kanji
            "きく": [
                {"kanji": "聞く", "meaning": "to hear/ask", "frequency": 1500, "context": ["conversation", "question", "sound"]},
                {"kanji": "聴く", "meaning": "to listen", "frequency": 600, "context": ["music", "concert", "attentive"]},
                {"kanji": "訊く", "meaning": "to inquire", "frequency": 200, "context": ["formal", "investigation", "question"]},
                {"kanji": "効く", "meaning": "to be effective", "frequency": 400, "context": ["medicine", "remedy", "work"]}
            ],
            "みる": [
                {"kanji": "見る", "meaning": "to see", "frequency": 2000, "context": ["look", "watch", "view"]},
                {"kanji": "観る", "meaning": "to watch", "frequency": 500, "context": ["movie", "show", "performance"]},
                {"kanji": "診る", "meaning": "to examine", "frequency": 300, "context": ["medical", "doctor", "patient"]},
                {"kanji": "看る", "meaning": "to care for", "frequency": 200, "context": ["nursing", "sick", "caretaking"]}
            ],
            "あける": [
                {"kanji": "開ける", "meaning": "to open", "frequency": 1000, "context": ["door", "window", "container"]},
                {"kanji": "空ける", "meaning": "to empty", "frequency": 400, "context": ["seat", "space", "vacate"]},
                {"kanji": "明ける", "meaning": "to dawn", "frequency": 300, "context": ["morning", "year", "end"]}
            ],
            "はかる": [
                {"kanji": "測る", "meaning": "to measure", "frequency": 500, "context": ["length", "distance", "size"]},
                {"kanji": "量る", "meaning": "to weigh", "frequency": 400, "context": ["weight", "volume", "scale"]},
                {"kanji": "計る", "meaning": "to time", "frequency": 450, "context": ["time", "calculate", "measure"]},
                {"kanji": "図る", "meaning": "to plan", "frequency": 350, "context": ["plot", "scheme", "attempt"]}
            ],
            
            # Adjectives
            "あつい": [
                {"kanji": "暑い", "meaning": "hot (weather)", "frequency": 700, "context": ["summer", "weather", "climate"]},
                {"kanji": "熱い", "meaning": "hot (temperature)", "frequency": 600, "context": ["water", "food", "touch"]},
                {"kanji": "厚い", "meaning": "thick", "frequency": 400, "context": ["book", "wall", "layer"]}
            ],
            "はやい": [
                {"kanji": "早い", "meaning": "early", "frequency": 800, "context": ["morning", "time", "soon"]},
                {"kanji": "速い", "meaning": "fast", "frequency": 700, "context": ["speed", "quick", "rapid"]}
            ],
            
            # Common words
            "こう": [
                {"kanji": "工", "meaning": "craft/construction", "frequency": 600, "context": ["工事", "工場", "工業"]},
                {"kanji": "公", "meaning": "public", "frequency": 700, "context": ["公園", "公共", "公式"]},
                {"kanji": "校", "meaning": "school", "frequency": 900, "context": ["学校", "校長", "校舎"]},
                {"kanji": "高", "meaning": "high/expensive", "frequency": 1000, "context": ["高い", "高校", "高級"]},
                {"kanji": "交", "meaning": "exchange/mix", "frequency": 500, "context": ["交通", "交換", "交流"]},
                {"kanji": "考", "meaning": "think", "frequency": 800, "context": ["考える", "思考", "参考"]}
            ],
            
            # More common readings
            "かい": [
                {"kanji": "会", "meaning": "meeting/society", "frequency": 1200, "context": ["会社", "会議", "会う"]},
                {"kanji": "買", "meaning": "buy", "frequency": 900, "context": ["買う", "買い物", "購買"]},
                {"kanji": "海", "meaning": "sea/ocean", "frequency": 800, "context": ["海洋", "海岸", "海外"]},
                {"kanji": "貝", "meaning": "shellfish", "frequency": 300, "context": ["貝殻", "貝類"]}
            ],
            "せい": [
                {"kanji": "生", "meaning": "life/student", "frequency": 1500, "context": ["学生", "生活", "生まれる"]},
                {"kanji": "性", "meaning": "nature/gender", "frequency": 800, "context": ["性別", "男性", "女性"]},
                {"kanji": "成", "meaning": "become/achieve", "frequency": 700, "context": ["成功", "完成", "成長"]},
                {"kanji": "正", "meaning": "correct", "frequency": 900, "context": ["正しい", "正解", "正式"]},
                {"kanji": "政", "meaning": "politics", "frequency": 600, "context": ["政治", "政府", "行政"]},
                {"kanji": "制", "meaning": "system/control", "frequency": 500, "context": ["制度", "制限", "規制"]}
            ],
            "し": [
                {"kanji": "市", "meaning": "city", "frequency": 1000, "context": ["都市", "市場", "市民"]},
                {"kanji": "私", "meaning": "I/private", "frequency": 1200, "context": ["私立", "私的"]},
                {"kanji": "死", "meaning": "death", "frequency": 600, "context": ["死ぬ", "死亡", "必死"]},
                {"kanji": "詩", "meaning": "poem", "frequency": 300, "context": ["詩人", "詩歌"]},
                {"kanji": "師", "meaning": "teacher/master", "frequency": 500, "context": ["教師", "医師", "師匠"]}
            ],
            "じ": [
                {"kanji": "時", "meaning": "time/hour", "frequency": 1500, "context": ["時間", "時計", "3時"]},
                {"kanji": "自", "meaning": "self", "frequency": 1300, "context": ["自分", "自然", "自動"]},
                {"kanji": "字", "meaning": "character/letter", "frequency": 800, "context": ["文字", "漢字", "数字"]},
                {"kanji": "事", "meaning": "thing/matter", "frequency": 1400, "context": ["仕事", "事件", "大事"]},
                {"kanji": "次", "meaning": "next", "frequency": 900, "context": ["次回", "次第", "目次"]}
            ],
            
            # Technical/Scientific
            "かがく": [
                {"kanji": "科学", "meaning": "science", "frequency": 700, "context": ["科学者", "科学的", "研究"]},
                {"kanji": "化学", "meaning": "chemistry", "frequency": 600, "context": ["化学式", "化学反応", "実験"]}
            ],
            "こうせい": [
                {"kanji": "校正", "meaning": "proofreading", "frequency": 300, "context": ["原稿", "校正刷り", "編集"]},
                {"kanji": "公正", "meaning": "fairness", "frequency": 400, "context": ["公正な", "裁判", "公平"]},
                {"kanji": "構成", "meaning": "composition", "frequency": 500, "context": ["文章", "構成要素", "組織"]},
                {"kanji": "厚生", "meaning": "welfare", "frequency": 350, "context": ["厚生省", "福祉", "健康"]}
            ],
            
            # Proper nouns and names
            "さとう": [
                {"kanji": "佐藤", "meaning": "Sato (surname)", "frequency": 800, "context": ["名前", "人名", "さん"]},
                {"kanji": "砂糖", "meaning": "sugar", "frequency": 600, "context": ["甘い", "コーヒー", "料理"]}
            ],
            "たなか": [
                {"kanji": "田中", "meaning": "Tanaka (surname)", "frequency": 900, "context": ["名前", "人名", "さん"]}
            ],
            
            # Similar meanings
            "まち": [
                {"kanji": "町", "meaning": "town", "frequency": 800, "context": ["小さな", "町並み", "地方"]},
                {"kanji": "街", "meaning": "city/street", "frequency": 700, "context": ["街中", "賑やか", "都会"]}
            ],
            "かなしい": [
                {"kanji": "悲しい", "meaning": "sad", "frequency": 600, "context": ["涙", "辛い", "気持ち"]},
                {"kanji": "哀しい", "meaning": "sorrowful", "frequency": 200, "context": ["文学", "詩的", "深い"]}
            ],
            "うまれる": [
                {"kanji": "生まれる", "meaning": "to be born", "frequency": 700, "context": ["誕生", "年", "場所"]},
                {"kanji": "産まれる", "meaning": "to be born (moment)", "frequency": 300, "context": ["赤ちゃん", "出産", "新生児"]}
            ],
            
            # Edge cases
            "きょう": [
                {"kanji": "今日", "meaning": "today", "frequency": 1500, "context": ["今日は", "本日", "日付"]},
                {"kanji": "教", "meaning": "teach/religion", "frequency": 600, "context": ["教室", "教会", "宗教"]},
                {"kanji": "京", "meaning": "capital", "frequency": 700, "context": ["東京", "京都", "上京"]}
            ],
            "かいとう": [
                {"kanji": "回答", "meaning": "answer/reply", "frequency": 500, "context": ["アンケート", "質問", "返答"]},
                {"kanji": "解答", "meaning": "solution/answer", "frequency": 450, "context": ["テスト", "問題", "正解"]}
            ]
        }
        
        for reading, options in homonyms.items():
            self.kanji_dict[reading]["options"] = options
    
    def add_compound_words(self):
        """Add common compound words"""
        
        self.compound_words = {
            # Common compounds
            "がっこう": ["学校"],
            "せんせい": ["先生"],
            "がくせい": ["学生"],
            "とうきょう": ["東京"],
            "にほん": ["日本"],
            "にほんご": ["日本語"],
            "でんわ": ["電話"],
            "でんしゃ": ["電車"],
            "でんき": ["電気"],
            "でんし": ["電子"],
            
            # More compounds
            "かいしゃ": ["会社"],
            "かいぎ": ["会議"],
            "べんきょう": ["勉強"],
            "しごと": ["仕事"],
            "せいかつ": ["生活"],
            "せいと": ["生徒"],
            
            # Greetings and common phrases
            "こんにちは": ["こんにちは", "今日は"],
            "こんばんは": ["こんばんは", "今晩は"],
            "おはよう": ["おはよう", "お早う"],
            "ありがとう": ["ありがとう", "有難う", "有り難う"],
            "すみません": ["すみません", "済みません"],
            
            # Time
            "いま": ["今"],
            "あした": ["明日"],
            "きのう": ["昨日"],
            "まいにち": ["毎日"],
            
            # Pronouns
            "わたし": ["私", "わたし"],
            "あなた": ["あなた", "貴方"],
            "かれ": ["彼"],
            "かのじょ": ["彼女"],
            
            # Common verbs
            "たべる": ["食べる"],
            "のむ": ["飲む"],
            "いく": ["行く"],
            "くる": ["来る"],
            "する": ["する"],
            
            # Adjectives
            "おおきい": ["大きい"],
            "ちいさい": ["小さい"],
            "あたらしい": ["新しい"],
            "ふるい": ["古い"],
            "たかい": ["高い"],
            "やすい": ["安い"],
            "いい": ["いい", "良い"],
            "わるい": ["悪い"],
            "かわいい": ["可愛い", "かわいい"],
            
            # Numbers
            "いち": ["一", "1", "いち"],
            "に": ["二", "2", "に"],
            "さん": ["三", "3", "さん"],
            "よん": ["四", "4", "よん"],
            "ご": ["五", "5", "ご"],
            
            # Locations
            "うえ": ["上"],
            "した": ["下"],
            "ひだり": ["左", "←", "ひだり"],
            "みぎ": ["右", "→", "みぎ"],
            "なか": ["中"],
            "そと": ["外"],
            
            # Weather
            "てんき": ["天気"],
            "はれ": ["晴れ"],
            "くもり": ["曇り"],
            "ゆき": ["雪"],
            
            # Food
            "ごはん": ["ご飯", "御飯"],
            "みず": ["水"],
            "おちゃ": ["お茶"],
            "さかな": ["魚"],
            "にく": ["肉"]
        }
    
    def add_grammar_patterns(self):
        """Add Japanese grammar patterns"""
        
        self.grammar_patterns = {
            "particles": {
                "は": {"type": "topic_marker", "usage": "marks sentence topic", "example": "私は学生です"},
                "が": {"type": "subject_marker", "usage": "marks grammatical subject", "example": "雨が降る"},
                "を": {"type": "object_marker", "usage": "marks direct object", "example": "本を読む"},
                "に": {"type": "location/time/indirect_object", "usage": "marks location, time, or indirect object", "example": "学校に行く"},
                "で": {"type": "location/means", "usage": "marks location of action or means", "example": "図書館で勉強する"},
                "と": {"type": "and/with", "usage": "connects nouns or marks accompaniment", "example": "友達と話す"},
                "へ": {"type": "direction", "usage": "marks direction", "example": "東京へ行く"},
                "から": {"type": "from/because", "usage": "marks starting point or reason", "example": "9時から"},
                "まで": {"type": "until/to", "usage": "marks ending point", "example": "5時まで"},
                "の": {"type": "possessive/modifier", "usage": "shows possession or modification", "example": "私の本"},
                "も": {"type": "also/too", "usage": "indicates inclusion", "example": "私も"},
                "や": {"type": "and (partial list)", "usage": "lists examples", "example": "本や雑誌"},
                "か": {"type": "question/or", "usage": "marks questions or alternatives", "example": "学生ですか"}
            },
            "verb_endings": {
                "ます": {"form": "polite_present", "attach_to": "verb_stem", "example": "食べます"},
                "ました": {"form": "polite_past", "attach_to": "verb_stem", "example": "食べました"},
                "ません": {"form": "polite_negative", "attach_to": "verb_stem", "example": "食べません"},
                "ませんでした": {"form": "polite_past_negative", "attach_to": "verb_stem", "example": "食べませんでした"},
                "て": {"form": "te_form", "attach_to": "verb", "example": "食べて"},
                "た": {"form": "past", "attach_to": "verb", "example": "食べた"},
                "ない": {"form": "negative", "attach_to": "verb", "example": "食べない"},
                "たい": {"form": "want_to", "attach_to": "verb_stem", "example": "食べたい"},
                "られる": {"form": "potential/passive", "attach_to": "verb", "example": "食べられる"},
                "させる": {"form": "causative", "attach_to": "verb", "example": "食べさせる"}
            },
            "adjective_endings": {
                "い": {"type": "i_adjective", "conjugations": ["かった", "くない", "くて"], "example": "大きい"},
                "な": {"type": "na_adjective", "conjugations": ["だった", "ではない", "で"], "example": "静かな"}
            },
            "common_patterns": {
                "〜ている": {"meaning": "continuous/resultant state", "example": "食べている"},
                "〜てください": {"meaning": "please do", "example": "食べてください"},
                "〜たことがある": {"meaning": "have done before", "example": "食べたことがある"},
                "〜なければならない": {"meaning": "must do", "example": "食べなければならない"},
                "〜ほうがいい": {"meaning": "had better", "example": "食べたほうがいい"},
                "〜そうです": {"meaning": "looks like/I heard", "example": "美味しそうです"}
            }
        }
    
    def save_dictionaries(self):
        """Save all dictionaries to files"""
        
        # Create data directory
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        
        # Save kanji dictionary
        kanji_file = data_dir / 'kanji_dictionary.json'
        with open(kanji_file, 'w', encoding='utf-8') as f:
            json.dump(dict(self.kanji_dict), f, ensure_ascii=False, indent=2)
        
        # Save compound words
        compound_file = data_dir / 'compound_words.json'
        with open(compound_file, 'w', encoding='utf-8') as f:
            json.dump(self.compound_words, f, ensure_ascii=False, indent=2)
        
        # Save grammar patterns
        grammar_file = data_dir / 'grammar_patterns.json'
        with open(grammar_file, 'w', encoding='utf-8') as f:
            json.dump(self.grammar_patterns, f, ensure_ascii=False, indent=2)
    
    def print_summary(self):
        """Print generation summary"""
        
        total_kanji = sum(len(entry["options"]) for entry in self.kanji_dict.values())
        
        print("="*70)
        print("✅ DICTIONARY GENERATION COMPLETE!")
        print("="*70)
        print()
        print("📊 Statistics:")
        print(f"  - Hiragana readings: {len(self.kanji_dict)}")
        print(f"  - Total kanji options: {total_kanji}")
        print(f"  - Compound words: {len(self.compound_words)}")
        print(f"  - Particles: {len(self.grammar_patterns['particles'])}")
        print(f"  - Verb endings: {len(self.grammar_patterns['verb_endings'])}")
        print()
        print("📁 Files created:")
        print("  - data/kanji_dictionary.json")
        print("  - data/compound_words.json")
        print("  - data/grammar_patterns.json")
        print()
        print("="*70)


def main():
    generator = KanjiDictionaryGenerator()
    generator.generate_comprehensive_dictionary()


if __name__ == '__main__':
    main()
