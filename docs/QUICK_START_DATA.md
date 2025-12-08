# Quick Start: Data Collection

This guide helps you quickly collect and prepare training data for the Keyboard Suggestions AI.

## Step 1: Prepare Your Data Files

Create these files in `data/raw/`:

### `english_casual.txt`
One sentence per line, casual conversational English:
```
I'm going to the store
wanna grab coffee?
that's so cool!
thanks for your help
see you later 👋
```

### `japanese_polite.txt`
One sentence per line, polite Japanese:
```
ありがとうございます
お疲れ様です
よろしくお願いします
今日はいい天気ですね
```

## Step 2: Clean Your Data

Run the cleaning script:

```bash
python scripts/clean_data.py
```

This will:
- Remove URLs and emails
- Normalize whitespace
- Validate sentence length
- Filter out invalid text
- Save cleaned data to `data/processed/`

## Step 3: Validate Dataset Quality

Check your dataset statistics:

```bash
python scripts/validate_dataset.py
```

This shows:
- Total sentences and words
- Vocabulary richness
- Quality assessment
- Recommendations

## Step 4: Train Tokenizer

Once you have enough data (1,000+ sentences minimum):

```bash
python src/tokenizer/train_tokenizer.py
```

## Step 5: Train Model

With tokenizer ready:

```bash
python src/model/train.py
```

---

## Data Collection Tips

### For English Casual Data:

**Good sources:**
- Twitter/X public tweets
- Reddit comments (r/CasualConversation)
- SMS/chat messages (anonymized)
- Movie subtitles
- Blog comments

**What to include:**
- Contractions (I'm, wanna, gonna)
- Slang (lol, omg, btw)
- Emoji (😂, ❤️, 👍)
- Short phrases (3-20 words)

**What to avoid:**
- Formal writing
- Technical jargon
- Very long sentences (>50 words)
- Spam or gibberish

### For Japanese Polite Data:

**Good sources:**
- Business emails
- Customer service responses
- News articles
- Corporate websites
- Formal textbooks

**What to include:**
- Polite forms (です、ます)
- Honorifics (お、ご)
- Formal expressions
- Complete sentences

**What to avoid:**
- Casual speech (だ、じゃん)
- Slang
- Incomplete sentences

---

## Minimum Requirements

| Language | Minimum | Recommended | Production |
|----------|---------|-------------|------------|
| English  | 1,000   | 10,000      | 50,000+    |
| Japanese | 1,000   | 10,000      | 50,000+    |
| **Total** | **2,000** | **20,000** | **100,000+** |

---

## Quick Collection Script

Here's a simple script to get started:

```python
# collect_data.py
import requests

def collect_from_file(input_file, output_file):
    """Simple file-based collection"""
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Basic filtering
    valid_lines = []
    for line in lines:
        line = line.strip()
        words = line.split()
        
        # Keep sentences with 3-50 words
        if 3 <= len(words) <= 50:
            valid_lines.append(line)
    
    # Save
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in valid_lines:
            f.write(line + '\n')
    
    print(f"Collected {len(valid_lines)} sentences")

# Usage
collect_from_file('my_data.txt', 'data/raw/english_casual.txt')
```

---

## Troubleshooting

### "Dataset too small" error

**Solution:** Collect more data. Minimum 1,000 sentences per language.

### "Low vocabulary diversity" warning

**Solution:** Add text from different sources (social media, blogs, chats, etc.)

### Tokenizer training fails

**Solution:** 
1. Check if `data/processed/combined_train.txt` exists
2. Ensure file has at least 100 lines
3. Verify UTF-8 encoding

### Model training is slow

**Solution:**
1. Reduce batch size in `config/model_config.yaml`
2. Use smaller dataset for testing
3. Enable GPU if available

---

## Next Steps

After collecting data:

1. ✅ Clean data: `python scripts/clean_data.py`
2. ✅ Validate: `python scripts/validate_dataset.py`
3. ✅ Train tokenizer: `python src/tokenizer/train_tokenizer.py`
4. ✅ Train model: `python src/model/train.py`
5. ✅ Export: `python src/utils/export_model.py`
6. ✅ Test: `python src/inference/prediction_engine.py`

For detailed information, see [DATA_COLLECTION_GUIDE.md](DATA_COLLECTION_GUIDE.md)
