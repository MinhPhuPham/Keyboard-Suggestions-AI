"""
Data cleaning and validation utilities
"""

import re
from pathlib import Path
from typing import List, Tuple


class DataCleaner:
    """Clean and validate training data"""
    
    def __init__(self, min_length: int = 3, max_length: int = 50):
        self.min_length = min_length
        self.max_length = max_length
    
    def clean_text(self, text: str) -> str:
        """Clean a single text line"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove excessive punctuation (but keep emoji)
        text = re.sub(r'([!?.]){3,}', r'\1\1', text)
        
        # Strip and normalize
        text = text.strip()
        
        return text
    
    def is_valid(self, text: str, language: str = 'en') -> bool:
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
    
    def _is_valid_english(self, text: str) -> bool:
        """Validate English text"""
        # Should be mostly ASCII (allowing emoji)
        ascii_ratio = sum(ord(c) < 128 for c in text if ord(c) < 0x1F300) / max(len(text), 1)
        return ascii_ratio > 0.5
    
    def _is_valid_japanese(self, text: str) -> bool:
        """Validate Japanese text"""
        # Must contain Japanese characters
        has_hiragana = any('\u3040' <= c <= '\u309f' for c in text)
        has_katakana = any('\u30a0' <= c <= '\u30ff' for c in text)
        has_kanji = any('\u4e00' <= c <= '\u9faf' for c in text)
        
        return has_hiragana or has_katakana or has_kanji
    
    def process_file(
        self,
        input_file: str,
        output_file: str,
        language: str = 'en'
    ) -> Tuple[int, int]:
        """
        Process entire file.
        
        Returns:
            (total_lines, valid_lines)
        """
        valid_lines = []
        total_lines = 0
        
        input_path = Path(input_file)
        if not input_path.exists():
            print(f"Error: File not found: {input_file}")
            return 0, 0
        
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                total_lines += 1
                cleaned = self.clean_text(line)
                
                if self.is_valid(cleaned, language):
                    valid_lines.append(cleaned)
        
        # Write cleaned data
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in valid_lines:
                f.write(line + '\n')
        
        print(f"\nProcessed: {input_file}")
        print(f"  Total lines: {total_lines:,}")
        print(f"  Valid lines: {len(valid_lines):,}")
        print(f"  Kept: {len(valid_lines)/max(total_lines, 1)*100:.1f}%")
        print(f"  Output: {output_file}")
        
        return total_lines, len(valid_lines)


def combine_datasets(
    input_files: List[str],
    output_file: str,
    shuffle: bool = True
):
    """
    Combine multiple cleaned datasets into one.
    
    Args:
        input_files: List of input file paths
        output_file: Output file path
        shuffle: Whether to shuffle the combined data
    """
    all_lines = []
    
    for input_file in input_files:
        if not Path(input_file).exists():
            print(f"Warning: File not found: {input_file}")
            continue
        
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            all_lines.extend(lines)
            print(f"Loaded {len(lines):,} lines from {input_file}")
    
    # Shuffle if requested
    if shuffle:
        import random
        random.shuffle(all_lines)
        print(f"\nShuffled {len(all_lines):,} total lines")
    
    # Write combined file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in all_lines:
            f.write(line + '\n')
    
    print(f"Combined dataset saved to: {output_file}")
    print(f"Total lines: {len(all_lines):,}")
    
    return len(all_lines)


if __name__ == "__main__":
    print("="*60)
    print("Data Cleaning Pipeline")
    print("="*60)
    
    cleaner = DataCleaner()
    
    # Process English data
    print("\n1. Processing English data...")
    if Path("data/raw/english_casual.txt").exists():
        cleaner.process_file(
            'data/raw/english_casual.txt',
            'data/processed/english_clean.txt',
            language='en'
        )
    else:
        print("  Skipped: data/raw/english_casual.txt not found")
    
    # Process Japanese data
    print("\n2. Processing Japanese data...")
    if Path("data/raw/japanese_polite.txt").exists():
        cleaner.process_file(
            'data/raw/japanese_polite.txt',
            'data/processed/japanese_clean.txt',
            language='ja'
        )
    else:
        print("  Skipped: data/raw/japanese_polite.txt not found")
    
    # Combine datasets
    print("\n3. Combining datasets...")
    input_files = [
        'data/processed/english_clean.txt',
        'data/processed/japanese_clean.txt'
    ]
    
    existing_files = [f for f in input_files if Path(f).exists()]
    
    if existing_files:
        combine_datasets(
            existing_files,
            'data/processed/combined_train.txt',
            shuffle=True
        )
    else:
        print("  No processed files found to combine")
    
    print("\n" + "="*60)
    print("Cleaning complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review cleaned files in data/processed/")
    print("2. Add more training data to data/raw/")
    print("3. Run this script again to process new data")
    print("4. Train tokenizer: python src/tokenizer/train_tokenizer.py")
