"""
Data preparation utilities for training dataset
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter


class DataPreparator:
    """Prepare and clean text data for training"""
    
    def __init__(self, min_length: int = 3, max_length: int = 50):
        self.min_length = min_length
        self.max_length = max_length
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text while preserving emoji and Unicode.
        
        Args:
            text: Raw text string
        
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def is_valid_sequence(self, text: str) -> bool:
        """
        Check if text sequence is valid for training.
        
        Args:
            text: Text to validate
        
        Returns:
            True if valid, False otherwise
        """
        # Check length
        words = text.split()
        if len(words) < self.min_length or len(words) > self.max_length:
            return False
        
        # Check for spam patterns (all same character)
        if len(set(text.replace(' ', ''))) < 3:
            return False
        
        return True
    
    def prepare_dataset(
        self,
        input_files: List[str],
        output_file: str,
        language: str = "en"
    ) -> Dict[str, int]:
        """
        Prepare dataset from input files.
        
        Args:
            input_files: List of input file paths
            output_file: Output file path
            language: Language code
        
        Returns:
            Statistics dictionary
        """
        all_texts = []
        total_lines = 0
        valid_lines = 0
        
        # Read all input files
        for input_file in input_files:
            if not Path(input_file).exists():
                print(f"Warning: File not found: {input_file}")
                continue
            
            with open(input_file, 'r', encoding='utf-8') as f:
                for line in f:
                    total_lines += 1
                    cleaned = self.clean_text(line)
                    
                    if self.is_valid_sequence(cleaned):
                        all_texts.append(cleaned)
                        valid_lines += 1
        
        # Write to output file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for text in all_texts:
                f.write(text + '\n')
        
        stats = {
            'total_lines': total_lines,
            'valid_lines': valid_lines,
            'output_file': output_file,
            'language': language
        }
        
        return stats


def create_sample_training_data(output_dir: str = "data/raw"):
    """
    Create sample training data for testing.
    
    Args:
        output_dir: Directory to save sample data
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # English sample data (casual, with emoji)
    english_samples = [
        "I'm going to the store",
        "wanna go to the movies tonight",
        "gonna be late sorry",
        "I love you ❤️",
        "Check this out 👀",
        "That's so cool",
        "lol that's funny 😂",
        "See you later",
        "Thanks for your help",
        "I'm happy today 😊",
        "omg this is amazing",
        "btw I'll be there soon",
        "tbh I don't know",
        "ngl that's pretty good",
        "Good morning everyone",
        "Have a great day",
        "Talk to you later",
        "No problem at all",
        "You're welcome",
        "Let me know if you need anything",
        "I'm on my way",
        "Be right back",
        "I don't know what to say",
        "That sounds good to me",
        "Can't wait to see you",
        "Miss you so much",
        "Congratulations on your success 🎉",
        "Good night sleep well 😴",
        "I'm thinking about it 🤔",
        "This is so exciting 🥳",
    ]
    
    # Japanese sample data (polite)
    japanese_samples = [
        "今日はいい天気ですね",
        "ありがとうございます",
        "お疲れ様です",
        "よろしくお願いします",
        "すみませんが",
        "おはようございます",
        "いただきます",
        "失礼します",
        "お世話になっております",
        "ご確認ください",
        "承知いたしました",
        "恐れ入りますが",
        "お待たせいたしました",
        "どうぞよろしくお願いいたします",
        "ご連絡ありがとうございます",
        "お忙しいところ申し訳ございません",
        "お手数をおかけします",
        "ご理解いただけますと幸いです",
        "何卒よろしくお願い申し上げます",
        "お返事お待ちしております",
    ]
    
    # Write English data
    en_file = output_path / "english_sample.txt"
    with open(en_file, 'w', encoding='utf-8') as f:
        for text in english_samples:
            f.write(text + '\n')
    
    print(f"Created English sample data: {en_file}")
    print(f"  - {len(english_samples)} samples")
    
    # Write Japanese data
    ja_file = output_path / "japanese_sample.txt"
    with open(ja_file, 'w', encoding='utf-8') as f:
        for text in japanese_samples:
            f.write(text + '\n')
    
    print(f"Created Japanese sample data: {ja_file}")
    print(f"  - {len(japanese_samples)} samples")
    
    return en_file, ja_file


if __name__ == "__main__":
    # Create sample training data
    print("Creating sample training data...")
    en_file, ja_file = create_sample_training_data()
    
    # Prepare datasets
    print("\nPreparing datasets...")
    preparator = DataPreparator()
    
    # Prepare English dataset
    en_stats = preparator.prepare_dataset(
        input_files=[str(en_file)],
        output_file="data/processed/english_train.txt",
        language="en"
    )
    print(f"\nEnglish dataset stats:")
    print(f"  Total lines: {en_stats['total_lines']}")
    print(f"  Valid lines: {en_stats['valid_lines']}")
    
    # Prepare Japanese dataset
    ja_stats = preparator.prepare_dataset(
        input_files=[str(ja_file)],
        output_file="data/processed/japanese_train.txt",
        language="ja"
    )
    print(f"\nJapanese dataset stats:")
    print(f"  Total lines: {ja_stats['total_lines']}")
    print(f"  Valid lines: {ja_stats['valid_lines']}")
    
    # Combine for multilingual training
    combined_stats = preparator.prepare_dataset(
        input_files=[str(en_file), str(ja_file)],
        output_file="data/processed/combined_train.txt",
        language="multilingual"
    )
    print(f"\nCombined dataset stats:")
    print(f"  Total lines: {combined_stats['total_lines']}")
    print(f"  Valid lines: {combined_stats['valid_lines']}")
