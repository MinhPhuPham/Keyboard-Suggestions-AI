# Training Data Collection Guide

## Overview

This guide provides structured templates for collecting real training data for the Keyboard Suggestions AI. Follow these formats to ensure data quality and consistency.

**Important**: Before collecting large datasets, **test with minimal data first** to ensure the model learns correctly. See [`TEST_ROADMAP.md`](TEST_ROADMAP.md) for testing strategy.

---

## Quick Start: Test Data (Start Here!)

Before collecting thousands of sentences, **validate the model with minimal test data**.

### Minimal Test Dataset (15 sentences)

Create `data/test/minimal_train.txt`:

```
I am happy
I am sad
I am tired
I love you
I love pizza
I love coding
you are great
you are awesome
you are amazing
thank you very much
thank you so much
how are you
how are you doing
what are you doing
what do you think
```

**Purpose**: Verify model learns patterns:
- "I am" → should predict `["happy", "sad", "tired"]`
- "I love" → should predict `["you", "pizza", "coding"]`
- "you are" → should predict `["great", "awesome", "amazing"]`

**Expected Results**:
- ✅ Different inputs → Different predictions
- ✅ Predictions match training data
- ✅ No crashes on unknown input

**If this works**, scale to 100 → 1,000 → 10,000 sentences.

**If this fails**, model architecture needs fixing before collecting more data.

See [`TEST_ROADMAP.md`](TEST_ROADMAP.md) for complete testing guide.

---

## Data Requirements

### Minimum Dataset Size
- **English**: 10,000+ sentences (target: 50,000+)
- **Japanese**: 10,000+ sentences (target: 50,000+)
- **Total**: 20,000+ sentences minimum

### Quality Guidelines
- Natural, conversational text
- Include emoji and symbols
- Mix of short and long sentences
- Diverse vocabulary
- Real-world typing patterns

---

## 1. English Training Data (Casual/Social Media Style)

### Format
One sentence per line, UTF-8 encoding, with emoji preserved.

### Example File: `english_casual.txt`

```
I'm going to the store later
wanna grab some coffee?
that's so cool!
lol I can't believe it 😂
thanks for your help!
see you tomorrow 👋
I love this song ❤️
omg that's amazing
btw I'll be there at 5
gonna be a great day
check this out 👀
I'm so excited 🎉
can't wait to see you
that was hilarious
you're the best
let me know when you're free
I'm on my way
be right back
talk to you later
have a great weekend
good morning everyone ☀️
congrats on the new job 🎊
happy birthday! 🎂
thinking of you 💭
miss you tons
how's it going?
what's up?
nothing much, you?
sounds good to me
perfect, see you then
```

### Sources to Collect From
1. **Twitter/X**: Public tweets (casual conversation)
2. **Reddit**: Comments from casual subreddits
3. **SMS/iMessage**: Personal messages (anonymized)
4. **Chat apps**: Discord, Slack public channels
5. **Movie subtitles**: Conversational dialogue
6. **Blog comments**: Informal writing

### Collection Script Example

```python
# english_data_collector.py
import json

def collect_english_casual():
    """
    Template for collecting English casual text.
    Replace with your actual data source.
    """
    sentences = []
    
    # Example: Read from your data source
    # with open('your_source.txt', 'r', encoding='utf-8') as f:
    #     for line in f:
    #         sentence = clean_sentence(line)
    #         if is_valid_casual_english(sentence):
    #             sentences.append(sentence)
    
    # Save to training file
    with open('data/raw/english_casual.txt', 'w', encoding='utf-8') as f:
        for sentence in sentences:
            f.write(sentence + '\n')
    
    return len(sentences)

def is_valid_casual_english(text):
    """Validate casual English text"""
    # Must be 3-50 words
    words = text.split()
    if len(words) < 3 or len(words) > 50:
        return False
    
    # Should contain mostly English characters
    ascii_ratio = sum(ord(c) < 128 for c in text) / len(text)
    if ascii_ratio < 0.7:
        return False
    
    return True
```

---

## 2. Japanese Training Data (Polite/Formal Style)

### Format
One sentence per line, UTF-8 encoding, polite forms preferred.

### Example File: `japanese_polite.txt`

```
今日はいい天気ですね
ありがとうございます
お疲れ様です
よろしくお願いします
すみませんが、少々お待ちください
おはようございます
いただきます
失礼します
お世話になっております
ご確認ください
承知いたしました
恐れ入りますが
お待たせいたしました
どうぞよろしくお願いいたします
ご連絡ありがとうございます
お忙しいところ申し訳ございません
お手数をおかけします
ご理解いただけますと幸いです
何卒よろしくお願い申し上げます
お返事お待ちしております
本日はありがとうございました
また明日お会いしましょう
お気をつけてお帰りください
良い週末をお過ごしください
お大事になさってください
```

### Sources to Collect From
1. **Business emails**: Formal Japanese correspondence
2. **Customer service**: Polite responses
3. **News articles**: Formal writing
4. **Corporate websites**: About pages, announcements
5. **Japanese textbooks**: Polite conversation examples
6. **NHK transcripts**: Formal broadcast language

### Collection Script Example

```python
# japanese_data_collector.py

def collect_japanese_polite():
    """
    Template for collecting Japanese polite text.
    """
    sentences = []
    
    # Example: Read from your data source
    # with open('your_japanese_source.txt', 'r', encoding='utf-8') as f:
    #     for line in f:
    #         sentence = clean_sentence(line)
    #         if is_valid_polite_japanese(sentence):
    #             sentences.append(sentence)
    
    # Save to training file
    with open('data/raw/japanese_polite.txt', 'w', encoding='utf-8') as f:
        for sentence in sentences:
            f.write(sentence + '\n')
    
    return len(sentences)

def is_valid_polite_japanese(text):
    """Validate polite Japanese text"""
    # Must contain Japanese characters
    has_japanese = any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9faf' 
                       for c in text)
    if not has_japanese:
        return False
    
    # Prefer polite forms (です、ます endings)
    polite_endings = ['です', 'ます', 'ました', 'ません', 'ございます']
    has_polite = any(text.endswith(ending) for ending in polite_endings)
    
    # Length check
    if len(text) < 5 or len(text) > 200:
        return False
    
    return True
```

---

## 3. Emoji-Rich Training Data

### Format
Sentences with natural emoji usage.

### Example File: `emoji_rich.txt`

```
I love you ❤️
good morning ☀️
congratulations 🎉
good night 😴
that's so funny 😂
thinking of you 🤔
you're amazing ⭐
happy birthday 🎂
good luck 🍀
thank you so much 🙏
I'm so happy 😊
miss you 💕
you got this 💪
feeling great today 😎
let's celebrate 🥳
sending hugs 🤗
coffee time ☕
pizza night 🍕
beach day 🏖️
study time 📚
music lover 🎵
movie night 🎬
workout done 💪
travel time ✈️
foodie life 🍔
```

### Collection Tips
- Look for social media posts with emoji
- Analyze emoji frequency in your target audience
- Include common emoji combinations
- Preserve emoji positioning (beginning, middle, end)

---

## 4. Mixed Language Data (Code-Switching)

### Format
Sentences mixing English and Japanese naturally.

### Example File: `mixed_language.txt`

```
東京 is amazing
I love 寿司
let's go to 渋谷
this is so 美味しい
meeting at 3時
see you in 新宿
I'm learning 日本語
that's so 可愛い
working in Tokyo オフィス
my favorite 居酒屋
weekend in 京都
studying at 大学
shopping in 原宿
living in Japan is great
I love Japanese 文化
```

### Collection Sources
- Bilingual social media users
- Language learning forums
- Expat communities
- International business communications

---

## 5. Data Cleaning Pipeline

### Script: `clean_training_data.py`

```python
import re
from pathlib import Path

class DataCleaner:
    """Clean and validate training data"""
    
    def __init__(self):
        self.min_length = 3  # words
        self.max_length = 50  # words
    
    def clean_text(self, text):
        """Clean a single text line"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'([!?.]){3,}', r'\1\1', text)
        
        # Strip and normalize
        text = text.strip()
        
        return text
    
    def is_valid(self, text, language='en'):
        """Validate text quality"""
        if not text:
            return False
        
        # Length check
        words = text.split()
        if len(words) < self.min_length or len(words) > self.max_length:
            return False
        
        # Language-specific validation
        if language == 'en':
            return self._is_valid_english(text)
        elif language == 'ja':
            return self._is_valid_japanese(text)
        
        return True
    
    def _is_valid_english(self, text):
        """Validate English text"""
        # Should be mostly ASCII
        ascii_ratio = sum(ord(c) < 128 for c in text) / len(text)
        return ascii_ratio > 0.6
    
    def _is_valid_japanese(self, text):
        """Validate Japanese text"""
        # Must contain Japanese characters
        return any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9faf' 
                   for c in text)
    
    def process_file(self, input_file, output_file, language='en'):
        """Process entire file"""
        valid_lines = []
        total_lines = 0
        
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                total_lines += 1
                cleaned = self.clean_text(line)
                
                if self.is_valid(cleaned, language):
                    valid_lines.append(cleaned)
        
        # Write cleaned data
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in valid_lines:
                f.write(line + '\n')
        
        print(f"Processed {input_file}:")
        print(f"  Total lines: {total_lines}")
        print(f"  Valid lines: {len(valid_lines)}")
        print(f"  Kept: {len(valid_lines)/total_lines*100:.1f}%")
        
        return len(valid_lines)

# Usage
if __name__ == "__main__":
    cleaner = DataCleaner()
    
    # Clean English data
    cleaner.process_file(
        'data/raw/english_casual.txt',
        'data/processed/english_clean.txt',
        language='en'
    )
    
    # Clean Japanese data
    cleaner.process_file(
        'data/raw/japanese_polite.txt',
        'data/processed/japanese_clean.txt',
        language='ja'
    )
```

---

## 6. Data Statistics & Validation

### Script: `validate_dataset.py`

```python
import json
from collections import Counter
from pathlib import Path

def analyze_dataset(file_path, language='en'):
    """Analyze training dataset statistics"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    # Basic stats
    total_sentences = len(lines)
    total_words = sum(len(line.split()) for line in lines)
    total_chars = sum(len(line) for line in lines)
    
    # Word length distribution
    word_lengths = [len(line.split()) for line in lines]
    
    # Character frequency
    all_text = ''.join(lines)
    char_freq = Counter(all_text)
    
    # Emoji count
    emoji_count = sum(1 for c in all_text 
                     if ord(c) > 0x1F300)
    
    stats = {
        'file': str(file_path),
        'language': language,
        'total_sentences': total_sentences,
        'total_words': total_words,
        'total_characters': total_chars,
        'avg_words_per_sentence': total_words / total_sentences,
        'avg_chars_per_sentence': total_chars / total_sentences,
        'min_words': min(word_lengths),
        'max_words': max(word_lengths),
        'emoji_count': emoji_count,
        'unique_characters': len(char_freq),
        'most_common_chars': char_freq.most_common(20)
    }
    
    # Print report
    print(f"\n{'='*60}")
    print(f"Dataset Analysis: {file_path.name}")
    print(f"{'='*60}")
    print(f"Language: {language}")
    print(f"Total sentences: {stats['total_sentences']:,}")
    print(f"Total words: {stats['total_words']:,}")
    print(f"Avg words/sentence: {stats['avg_words_per_sentence']:.1f}")
    print(f"Avg chars/sentence: {stats['avg_chars_per_sentence']:.1f}")
    print(f"Word range: {stats['min_words']}-{stats['max_words']}")
    print(f"Emoji count: {stats['emoji_count']}")
    print(f"Unique characters: {stats['unique_characters']}")
    
    return stats

# Usage
if __name__ == "__main__":
    # Analyze all datasets
    datasets = [
        ('data/processed/english_clean.txt', 'en'),
        ('data/processed/japanese_clean.txt', 'ja'),
    ]
    
    all_stats = []
    for file_path, lang in datasets:
        if Path(file_path).exists():
            stats = analyze_dataset(Path(file_path), lang)
            all_stats.append(stats)
    
    # Save stats
    with open('data/dataset_stats.json', 'w') as f:
        json.dump(all_stats, f, indent=2, ensure_ascii=False)
```

---

## 7. Recommended Data Sources

### Free Public Datasets

1. **English Casual**:
   - Twitter API (with proper authentication)
   - Reddit API (r/CasualConversation, r/AskReddit)
   - OpenSubtitles (movie dialogue)
   - Common Crawl (filtered for conversational text)

2. **Japanese Polite**:
   - JESC (Japanese-English Subtitle Corpus)
   - Tatoeba Project (sentence pairs)
   - JParaCrawl (web-crawled Japanese text)
   - Wikipedia Japanese (formal writing)

3. **Multilingual**:
   - OPUS (parallel corpora)
   - Tatoeba (multilingual sentences)
   - CC-100 (Common Crawl monolingual)

### Data Collection Checklist

- [ ] Collect 10,000+ English sentences
- [ ] Collect 10,000+ Japanese sentences
- [ ] Include 500+ emoji examples
- [ ] Add 200+ mixed language examples
- [ ] Clean and validate all data
- [ ] Remove duplicates
- [ ] Check for offensive content
- [ ] Verify emoji preservation
- [ ] Split train/val/test (80/10/10)
- [ ] Generate statistics report

---

## 8. Final Dataset Structure

```
data/
├── raw/
│   ├── english_casual.txt          # Raw English data
│   ├── japanese_polite.txt         # Raw Japanese data
│   ├── emoji_rich.txt              # Emoji examples
│   └── mixed_language.txt          # Code-switching
├── processed/
│   ├── english_clean.txt           # Cleaned English
│   ├── japanese_clean.txt          # Cleaned Japanese
│   ├── combined_train.txt          # Combined training set
│   ├── validation.txt              # Validation set (10%)
│   └── test.txt                    # Test set (10%)
└── dataset_stats.json              # Statistics report
```

---

## Next Steps

1. **Collect data** using the templates above
2. **Clean data** with the provided scripts
3. **Validate** using the analysis tools
4. **Train tokenizer** on combined dataset
5. **Train model** with the full dataset
6. **Evaluate** on test set

**Target**: 20,000+ sentences minimum for production-quality model!
