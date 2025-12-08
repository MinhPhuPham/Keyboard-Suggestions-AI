"""
Dataset class for PyTorch training
"""

import torch
from torch.utils.data import Dataset, DataLoader
from typing import List, Tuple
from pathlib import Path


class NextWordDataset(Dataset):
    """
    Dataset for next-word prediction training.
    
    Creates (context, target) pairs where:
    - context: sequence of tokens
    - target: next token to predict
    """
    
    def __init__(
        self,
        text_file: str,
        tokenizer,
        max_seq_length: int = 50,
        min_seq_length: int = 3
    ):
        """
        Initialize dataset.
        
        Args:
            text_file: Path to text file
            tokenizer: Tokenizer instance
            max_seq_length: Maximum sequence length
            min_seq_length: Minimum sequence length
        """
        self.tokenizer = tokenizer
        self.max_seq_length = max_seq_length
        self.min_seq_length = min_seq_length
        
        # Load and tokenize all texts
        self.sequences = []
        self._load_data(text_file)
    
    def _load_data(self, text_file: str):
        """Load and prepare training sequences"""
        with open(text_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Tokenize
                token_ids = self.tokenizer.encode(line)
                
                # Skip if too short
                if len(token_ids) < self.min_seq_length:
                    continue
                
                # Create sliding window sequences
                for i in range(1, len(token_ids)):
                    # Get context (all tokens up to i)
                    context = token_ids[max(0, i - self.max_seq_length):i]
                    target = token_ids[i]
                    
                    self.sequences.append((context, target))
    
    def __len__(self) -> int:
        return len(self.sequences)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        context, target = self.sequences[idx]
        
        # Convert to tensors
        context_tensor = torch.tensor(context, dtype=torch.long)
        target_tensor = torch.tensor(target, dtype=torch.long)
        
        return context_tensor, target_tensor


def collate_fn(batch: List[Tuple[torch.Tensor, torch.Tensor]]) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Collate function for DataLoader.
    Pads sequences to same length in batch.
    
    Args:
        batch: List of (context, target) tuples
    
    Returns:
        Padded contexts and targets
    """
    contexts, targets = zip(*batch)
    
    # Find max length in batch
    max_len = max(len(c) for c in contexts)
    
    # Pad contexts
    padded_contexts = []
    for context in contexts:
        # Pad with 0 (pad token)
        padding = torch.zeros(max_len - len(context), dtype=torch.long)
        padded = torch.cat([padding, context])
        padded_contexts.append(padded)
    
    # Stack into batch
    contexts_batch = torch.stack(padded_contexts)
    targets_batch = torch.stack(targets)
    
    return contexts_batch, targets_batch


def create_dataloaders(
    train_file: str,
    tokenizer,
    batch_size: int = 128,
    max_seq_length: int = 50,
    validation_split: float = 0.1,
    num_workers: int = 0
) -> Tuple[DataLoader, DataLoader]:
    """
    Create train and validation dataloaders.
    
    Args:
        train_file: Path to training data
        tokenizer: Tokenizer instance
        batch_size: Batch size
        max_seq_length: Maximum sequence length
        validation_split: Fraction of data for validation
        num_workers: Number of worker processes
    
    Returns:
        Train and validation dataloaders
    """
    # Create full dataset
    full_dataset = NextWordDataset(
        train_file,
        tokenizer,
        max_seq_length=max_seq_length
    )
    
    # Split into train and validation
    total_size = len(full_dataset)
    val_size = int(total_size * validation_split)
    train_size = total_size - val_size
    
    train_dataset, val_dataset = torch.utils.data.random_split(
        full_dataset,
        [train_size, val_size]
    )
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_fn,
        num_workers=num_workers
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collate_fn,
        num_workers=num_workers
    )
    
    print(f"Dataset created:")
    print(f"  Total sequences: {total_size:,}")
    print(f"  Train sequences: {train_size:,}")
    print(f"  Validation sequences: {val_size:,}")
    print(f"  Batch size: {batch_size}")
    
    return train_loader, val_loader


if __name__ == "__main__":
    from train_tokenizer import Tokenizer
    
    # Load tokenizer
    tokenizer = Tokenizer("models/tokenizer.model")
    
    # Create dataloaders
    train_loader, val_loader = create_dataloaders(
        train_file="data/processed/combined_train.txt",
        tokenizer=tokenizer,
        batch_size=4,  # Small batch for testing
        max_seq_length=20
    )
    
    # Test one batch
    print("\nTesting dataloader:")
    for contexts, targets in train_loader:
        print(f"Contexts shape: {contexts.shape}")
        print(f"Targets shape: {targets.shape}")
        print(f"\nSample context: {contexts[0]}")
        print(f"Sample target: {targets[0]}")
        break
