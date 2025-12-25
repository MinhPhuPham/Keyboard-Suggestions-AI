#!/usr/bin/env python3
"""
Comprehensive data collection script for Keyboard Suggestions AI.
Processes ALL data from the data folder and creates a unified training dataset.
"""

import os
import re
from pathlib import Path
from collections import Counter
import json

class ComprehensiveDataCollector:
    """Collects and processes all available data sources"""
    
    def __init__(self, data_dir='data', output_dir='data/processed'):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            'sources': {},
            'total_sentences': 0,
            'total_words': 0,
            'total_chars': 0
        }
    
    def collect_all_data(self):
        """Main entry point - collect from all sources"""
        print("="*70)
        print("COMPREHENSIVE DATA COLLECTION")
        print("="*70)
        print()
        
        all_sentences = []
        
        # 1. Dictionary OSS (Mozc dictionaries)
        print("📚 Processing dictionary_oss...")
        dict_sentences = self.process_dictionary_oss()
        all_sentences.extend(dict_sentences)
        self.stats['sources']['dictionary_oss'] = len(dict_sentences)
        print(f"   ✓ Collected {len(dict_sentences):,} entries")
        print()
        
        # 2. Processed data (already extracted)
        print("📝 Processing processed data...")
        processed_sentences = self.process_processed_data()
        all_sentences.extend(processed_sentences)
        self.stats['sources']['processed'] = len(processed_sentences)
        print(f"   ✓ Collected {len(processed_sentences):,} sentences")
        print()
        
        # 3. Emoji data
        print("😊 Processing emoji data...")
        emoji_sentences = self.process_emoji_data()
        all_sentences.extend(emoji_sentences)
        self.stats['sources']['emoji'] = len(emoji_sentences)
        print(f"   ✓ Collected {len(emoji_sentences):,} emoji phrases")
        print()
        
        # 4. Symbol data
        print("🔣 Processing symbol data...")
        symbol_sentences = self.process_symbol_data()
        all_sentences.extend(symbol_sentences)
        self.stats['sources']['symbol'] = len(symbol_sentences)
        print(f"   ✓ Collected {len(symbol_sentences):,} symbol phrases")
        print()
        
        # Remove duplicates
        print("🔄 Removing duplicates...")
        unique_sentences = list(set(all_sentences))
        print(f"   Before: {len(all_sentences):,}")
        print(f"   After: {len(unique_sentences):,}")
        print(f"   Removed: {len(all_sentences) - len(unique_sentences):,} duplicates")
        print()
        
        # Filter and clean
        print("🧹 Cleaning and filtering...")
        clean_sentences = self.clean_sentences(unique_sentences)
        print(f"   Valid sentences: {len(clean_sentences):,}")
        print()
        
        # Save
        output_file = self.output_dir / 'comprehensive_train.txt'
        self.save_sentences(clean_sentences, output_file)
        
        # Statistics
        self.calculate_stats(clean_sentences)
        self.save_stats()
        
        return clean_sentences
    
    def process_dictionary_oss(self):
        """Process Mozc dictionary files"""
        sentences = []
        dict_dir = self.data_dir / 'dictionary_oss'
        
        if not dict_dir.exists():
            return sentences
        
        # Process dictionary files (dictionary00.txt - dictionary09.txt)
        for i in range(10):
            dict_file = dict_dir / f'dictionary{i:02d}.txt'
            if dict_file.exists():
                with open(dict_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        # Format: reading\tcost\tlid\trid\tword
                        parts = line.split('\t')
                        if len(parts) >= 5:
                            word = parts[4]  # The actual word
                            if self.is_valid_japanese(word):
                                sentences.append(word)
        
        return sentences
    
    def process_processed_data(self):
        """Process already processed data"""
        sentences = []
        processed_dir = self.data_dir / 'processed'
        
        if not processed_dir.exists():
            return sentences
        
        # Read all .txt files
        for txt_file in processed_dir.glob('*.txt'):
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            sentences.append(line)
            except Exception as e:
                print(f"   Warning: Could not read {txt_file.name}: {e}")
        
        return sentences
    
    def process_emoji_data(self):
        """Process emoji data"""
        sentences = []
        emoji_dir = self.data_dir / 'emoji'
        
        if not emoji_dir.exists():
            return sentences
        
        for tsv_file in emoji_dir.glob('*.tsv'):
            try:
                with open(tsv_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            # Emoji + description
                            emoji_phrase = parts[0] + ' ' + parts[1]
                            sentences.append(emoji_phrase)
            except Exception as e:
                print(f"   Warning: Could not read {tsv_file.name}: {e}")
        
        return sentences
    
    def process_symbol_data(self):
        """Process symbol data"""
        sentences = []
        symbol_dir = self.data_dir / 'symbol'
        
        if not symbol_dir.exists():
            return sentences
        
        for tsv_file in symbol_dir.glob('*.tsv'):
            try:
                with open(tsv_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            symbol_phrase = parts[0] + ' ' + parts[1]
                            sentences.append(symbol_phrase)
            except Exception as e:
                print(f"   Warning: Could not read {tsv_file.name}: {e}")
        
        return sentences
    
    def is_valid_japanese(self, text):
        """Check if text contains Japanese characters"""
        if not text or len(text) < 1:
            return False
        
        # Check for Japanese characters (Hiragana, Katakana, Kanji)
        has_japanese = any(
            '\u3040' <= c <= '\u30ff' or  # Hiragana + Katakana
            '\u4e00' <= c <= '\u9faf'      # Kanji
            for c in text
        )
        
        return has_japanese
    
    def clean_sentences(self, sentences):
        """Clean and filter sentences"""
        clean = []
        
        for sent in sentences:
            # Remove excessive whitespace
            sent = re.sub(r'\s+', ' ', sent).strip()
            
            # Skip if too short or too long
            if len(sent) < 2 or len(sent) > 200:
                continue
            
            # Skip if all numbers or symbols
            if re.match(r'^[\d\s\W]+$', sent):
                continue
            
            clean.append(sent)
        
        return clean
    
    def save_sentences(self, sentences, output_file):
        """Save sentences to file"""
        print(f"💾 Saving to {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for sent in sentences:
                f.write(sent + '\n')
        
        file_size = output_file.stat().st_size / (1024 * 1024)  # MB
        print(f"   ✓ Saved {len(sentences):,} sentences ({file_size:.1f} MB)")
    
    def calculate_stats(self, sentences):
        """Calculate dataset statistics"""
        self.stats['total_sentences'] = len(sentences)
        self.stats['total_words'] = sum(len(s.split()) for s in sentences)
        self.stats['total_chars'] = sum(len(s) for s in sentences)
        
        # Word length distribution
        word_lengths = [len(s.split()) for s in sentences]
        self.stats['avg_words_per_sentence'] = sum(word_lengths) / len(word_lengths)
        self.stats['min_words'] = min(word_lengths)
        self.stats['max_words'] = max(word_lengths)
        
        # Character distribution
        self.stats['avg_chars_per_sentence'] = self.stats['total_chars'] / len(sentences)
        
        # Character frequency
        all_text = ''.join(sentences)
        char_freq = Counter(all_text)
        self.stats['unique_characters'] = len(char_freq)
        self.stats['most_common_chars'] = char_freq.most_common(20)
    
    def save_stats(self):
        """Save statistics to JSON"""
        stats_file = self.output_dir / 'dataset_stats.json'
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        
        print("="*70)
        print("DATASET STATISTICS")
        print("="*70)
        print(f"Total sentences: {self.stats['total_sentences']:,}")
        print(f"Total words: {self.stats['total_words']:,}")
        print(f"Total characters: {self.stats['total_chars']:,}")
        print(f"Avg words/sentence: {self.stats['avg_words_per_sentence']:.1f}")
        print(f"Avg chars/sentence: {self.stats['avg_chars_per_sentence']:.1f}")
        print(f"Unique characters: {self.stats['unique_characters']:,}")
        print()
        print("Sources:")
        for source, count in self.stats['sources'].items():
            print(f"  {source}: {count:,}")
        print()
        print(f"✓ Statistics saved to {stats_file}")
        print("="*70)


def main():
    """Main entry point"""
    collector = ComprehensiveDataCollector()
    sentences = collector.collect_all_data()
    
    print()
    print("✅ Data collection complete!")
    print(f"📁 Output: data/processed/comprehensive_train.txt")
    print(f"📊 Stats: data/processed/dataset_stats.json")
    print()
    print("Next steps:")
    print("1. Train tokenizer: python -c \"from src.tokenizer.train_tokenizer import TokenizerTrainer; ...")
    print("2. Train model: python src/model/train.py --data-file data/processed/comprehensive_train.txt")
    print("3. Export to Core ML: python scripts/export_coreml.py")


if __name__ == '__main__':
    main()
