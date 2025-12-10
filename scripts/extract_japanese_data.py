"""
Extract Japanese training data from Mozc dictionary files
Processes dictionary, kanji, emoji, and emoticon data to create training sentences
"""

import re
from pathlib import Path
from typing import List, Set, Dict
from collections import defaultdict
import random

class JapaneseDataExtractor:
    """Extract and process Japanese training data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.words = []  # List of (reading, word, frequency_score)
        self.kanji_map = {}  # kanji -> readings
        self.emoticons = []  # List of (keys, symbol)
        self.emojis = []  # List of (reading, emoji)
        
    def extract_dictionary_words(self) -> int:
        """
        Extract words from dictionary files.
        Format: reading  left_id  right_id  cost  word
        """
        print("Extracting dictionary words...")
        dict_dir = self.data_dir / "dictionary_oss"
        
        word_freq = defaultdict(int)
        
        for dict_file in dict_dir.glob("dictionary*.txt"):
            print(f"  Processing {dict_file.name}...")
            with open(dict_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 5:
                        reading = parts[0]
                        cost = int(parts[3])  # Lower cost = more frequent
                        word = parts[4]
                        
                        # Skip if word is just reading (no kanji)
                        if word == reading:
                            continue
                            
                        # Calculate frequency score (lower cost = higher frequency)
                        freq_score = 10000 - min(cost, 9999)
                        word_freq[(reading, word)] += freq_score
        
        # Convert to list
        self.words = [(r, w, f) for (r, w), f in word_freq.items()]
        self.words.sort(key=lambda x: x[2], reverse=True)  # Sort by frequency
        
        print(f"  Extracted {len(self.words)} unique words")
        return len(self.words)
    
    def extract_kanji_readings(self) -> int:
        """
        Extract kanji readings.
        Format: reading  kanji_variants
        """
        print("Extracting kanji readings...")
        kanji_file = self.data_dir / "single_kanji" / "single_kanji.tsv"
        
        if not kanji_file.exists():
            print("  Kanji file not found, skipping")
            return 0
        
        with open(kanji_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    reading = parts[0]
                    kanjis = parts[1]
                    for kanji in kanjis:
                        if kanji not in self.kanji_map:
                            self.kanji_map[kanji] = []
                        self.kanji_map[kanji].append(reading)
        
        print(f"  Extracted {len(self.kanji_map)} kanji mappings")
        return len(self.kanji_map)
    
    def extract_emoticons(self) -> int:
        """
        Extract emoticons.
        Format: symbol  keys  categories
        """
        print("Extracting emoticons...")
        emoticon_file = self.data_dir / "emoticon" / "emoticon.tsv"
        
        if not emoticon_file.exists():
            print("  Emoticon file not found, skipping")
            return 0
        
        with open(emoticon_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    symbol = parts[0]
                    keys = parts[1].split()
                    self.emoticons.append((keys, symbol))
        
        print(f"  Extracted {len(self.emoticons)} emoticons")
        return len(self.emoticons)
    
    def extract_emojis(self) -> int:
        """Extract emoji data"""
        print("Extracting emojis...")
        emoji_file = self.data_dir / "emoji" / "emoji_data.tsv"
        
        if not emoji_file.exists():
            print("  Emoji file not found, skipping")
            return 0
        
        with open(emoji_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    emoji = parts[0]
                    readings = parts[1].split()
                    for reading in readings:
                        self.emojis.append((reading, emoji))
        
        print(f"  Extracted {len(self.emojis)} emoji mappings")
        return len(self.emojis)
    
    def generate_training_sentences(self, num_sentences: int = 100000) -> List[str]:
        """
        Generate training sentences from extracted data.
        Creates natural Japanese text patterns for keyboard prediction.
        """
        print(f"\nGenerating {num_sentences} training sentences...")
        sentences = []
        
        # Take top frequent words
        top_words = self.words[:50000]  # Top 50K most frequent
        
        # Generate sentences of varying lengths
        for i in range(num_sentences):
            if i % 10000 == 0:
                print(f"  Generated {i} sentences...")
            
            # Vary sentence length (2-8 words)
            length = random.choices([2, 3, 4, 5, 6, 7, 8], 
                                   weights=[10, 20, 25, 20, 15, 7, 3])[0]
            
            # Select words (weighted by frequency)
            selected = random.choices(top_words, 
                                     weights=[w[2] for w in top_words],
                                     k=length)
            
            # Create sentence from words (not readings)
            sentence_words = [w[1] for w in selected]
            sentence = ''.join(sentence_words)
            
            # Add emoticon occasionally (5% chance)
            if random.random() < 0.05 and self.emoticons:
                emoticon = random.choice(self.emoticons)
                sentence += emoticon[1]
            
            # Add emoji occasionally (3% chance)
            if random.random() < 0.03 and self.emojis:
                emoji = random.choice(self.emojis)
                sentence += emoji[1]
            
            sentences.append(sentence)
        
        print(f"  Generated {len(sentences)} sentences")
        return sentences
    
    def save_training_data(self, sentences: List[str], output_file: str):
        """Save training sentences to file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for sentence in sentences:
                f.write(sentence + '\n')
        
        print(f"\nSaved {len(sentences)} sentences to {output_file}")
        
        # Print statistics
        total_chars = sum(len(s) for s in sentences)
        avg_length = total_chars / len(sentences) if sentences else 0
        print(f"  Total characters: {total_chars:,}")
        print(f"  Average sentence length: {avg_length:.1f} characters")
    
    def run(self, output_file: str = "data/processed/japanese_train_large.txt",
            num_sentences: int = 100000):
        """Run complete extraction pipeline"""
        print("="*70)
        print("Japanese Training Data Extraction")
        print("="*70)
        
        # Extract all data
        self.extract_dictionary_words()
        self.extract_kanji_readings()
        self.extract_emoticons()
        self.extract_emojis()
        
        # Generate training sentences
        sentences = self.generate_training_sentences(num_sentences)
        
        # Save to file
        self.save_training_data(sentences, output_file)
        
        print("\n" + "="*70)
        print("✓ Extraction complete!")
        print("="*70)
        
        return output_file


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract Japanese training data")
    parser.add_argument("--output", default="data/processed/japanese_train_large.txt",
                       help="Output file path")
    parser.add_argument("--num-sentences", type=int, default=100000,
                       help="Number of sentences to generate")
    parser.add_argument("--data-dir", default="data",
                       help="Data directory")
    
    args = parser.parse_args()
    
    extractor = JapaneseDataExtractor(data_dir=args.data_dir)
    extractor.run(output_file=args.output, num_sentences=args.num_sentences)
