"""
SentencePiece tokenizer training and utilities
"""

import sentencepiece as spm
from pathlib import Path
from typing import List, Optional


class TokenizerTrainer:
    """Train and manage SentencePiece tokenizer"""
    
    def __init__(self, model_prefix: str = "tokenizer"):
        self.model_prefix = model_prefix
        self.model_file = f"{model_prefix}.model"
        self.vocab_file = f"{model_prefix}.vocab"
    
    def train(
        self,
        input_files: List[str],
        vocab_size: int = 25000,
        character_coverage: float = 1.0,
        model_type: str = "unigram",
        output_dir: str = "models"
    ) -> str:
        """
        Train SentencePiece tokenizer.
        
        Args:
            input_files: List of training text files
            vocab_size: Vocabulary size
            character_coverage: Character coverage (1.0 for full Unicode)
            model_type: Model type (unigram, bpe, char, word)
            output_dir: Output directory for model files
        
        Returns:
            Path to trained model file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        model_prefix = str(output_path / self.model_prefix)
        
        # Combine input files
        input_str = ','.join(input_files)
        
        # Training parameters
        train_params = [
            f'--input={input_str}',
            f'--model_prefix={model_prefix}',
            f'--vocab_size={vocab_size}',
            f'--character_coverage={character_coverage}',
            f'--model_type={model_type}',
            '--normalization_rule_name=nmt_nfkc',
            '--pad_id=0',
            '--unk_id=1',
            '--bos_id=2',
            '--eos_id=3',
            '--user_defined_symbols=😊,😂,❤️,🎉,👀,😴,🌙,💤,🤔,🥳,🎊,👏,😋,🍣,🔥,🥰',  # Common emoji
        ]
        
        # Train tokenizer
        print(f"Training SentencePiece tokenizer...")
        print(f"  Input files: {input_files}")
        print(f"  Vocab size: {vocab_size}")
        print(f"  Character coverage: {character_coverage}")
        print(f"  Model type: {model_type}")
        
        spm.SentencePieceTrainer.train(' '.join(train_params))
        
        model_file = f"{model_prefix}.model"
        print(f"\nTokenizer trained successfully!")
        print(f"  Model file: {model_file}")
        print(f"  Vocab file: {model_prefix}.vocab")
        
        return model_file
    
    def load(self, model_file: str) -> spm.SentencePieceProcessor:
        """
        Load trained tokenizer.
        
        Args:
            model_file: Path to model file
        
        Returns:
            SentencePieceProcessor instance
        """
        sp = spm.SentencePieceProcessor()
        sp.load(model_file)
        return sp
    
    def test_tokenizer(self, model_file: str, test_texts: List[str]):
        """
        Test tokenizer on sample texts.
        
        Args:
            model_file: Path to model file
            test_texts: List of test texts
        """
        sp = self.load(model_file)
        
        print(f"\nTesting tokenizer on {len(test_texts)} samples:")
        print("=" * 80)
        
        for text in test_texts:
            tokens = sp.encode_as_pieces(text)
            ids = sp.encode_as_ids(text)
            
            print(f"\nText: {text}")
            print(f"Tokens: {tokens}")
            print(f"IDs: {ids}")
            print(f"Token count: {len(tokens)}")
        
        print("\n" + "=" * 80)
        print(f"Tokenizer vocab size: {sp.vocab_size()}")


class Tokenizer:
    """Wrapper for SentencePiece tokenizer"""
    
    def __init__(self, model_file: str):
        self.sp = spm.SentencePieceProcessor()
        self.sp.load(model_file)
        self.vocab_size = self.sp.vocab_size()
        
        # Special token IDs
        self.pad_id = self.sp.pad_id()
        self.unk_id = self.sp.unk_id()
        self.bos_id = self.sp.bos_id()
        self.eos_id = self.sp.eos_id()
    
    def encode(self, text: str) -> List[int]:
        """Encode text to token IDs"""
        return self.sp.encode_as_ids(text)
    
    def decode(self, ids: List[int]) -> str:
        """Decode token IDs to text"""
        return self.sp.decode_ids(ids)
    
    def encode_pieces(self, text: str) -> List[str]:
        """Encode text to token pieces"""
        return self.sp.encode_as_pieces(text)
    
    def get_vocab_size(self) -> int:
        """Get vocabulary size"""
        return self.vocab_size
    
    def id_to_piece(self, token_id: int) -> str:
        """Convert token ID to piece"""
        return self.sp.id_to_piece(token_id)
    
    def piece_to_id(self, piece: str) -> int:
        """Convert piece to token ID"""
        return self.sp.piece_to_id(piece)


if __name__ == "__main__":
    # Train tokenizer on sample data
    trainer = TokenizerTrainer()
    
    # Check if training data exists
    train_file = Path("data/processed/combined_train.txt")
    
    if not train_file.exists():
        print("Training data not found. Creating sample data first...")
        from data_prep import create_sample_training_data, DataPreparator
        
        # Create sample data
        en_file, ja_file = create_sample_training_data()
        
        # Prepare combined dataset
        preparator = DataPreparator()
        preparator.prepare_dataset(
            input_files=[str(en_file), str(ja_file)],
            output_file=str(train_file),
            language="multilingual"
        )
    
    # Train tokenizer
    model_file = trainer.train(
        input_files=[str(train_file)],
        vocab_size=100,  # Small vocab for demo dataset
        character_coverage=1.0,
        model_type="unigram"
    )
    
    # Test tokenizer
    test_texts = [
        "I'm going to the store",
        "wanna go tonight",
        "I love you ❤️",
        "lol that's funny 😂",
        "今日はいい天気ですね",
        "ありがとうございます",
        "東京 is great",  # Code-switching
    ]
    
    trainer.test_tokenizer(model_file, test_texts)
