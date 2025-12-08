"""
Training script for TinyLSTM model
"""

import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path
from tqdm import tqdm
import json
from typing import Dict, Tuple

import sys
sys.path.append('src')

from model.tiny_lstm import TinyLSTM
from tokenizer.train_tokenizer import Tokenizer
from utils.dataset import create_dataloaders
from utils.config_loader import get_model_config


class Trainer:
    """Trainer for TinyLSTM model"""
    
    def __init__(
        self,
        model: TinyLSTM,
        train_loader,
        val_loader,
        device: str = "cpu",
        learning_rate: float = 0.001,
        gradient_clip: float = 1.0
    ):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.gradient_clip = gradient_clip
        
        # Loss and optimizer
        self.criterion = nn.CrossEntropyLoss(ignore_index=0)  # Ignore padding
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        
        # Training history
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'train_perplexity': [],
            'val_perplexity': []
        }
        
        self.best_val_loss = float('inf')
    
    def train_epoch(self) -> Tuple[float, float]:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        num_batches = 0
        
        pbar = tqdm(self.train_loader, desc="Training")
        for contexts, targets in pbar:
            contexts = contexts.to(self.device)
            targets = targets.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs, _ = self.model(contexts)
            
            # Get predictions for last token
            predictions = outputs[:, -1, :]
            
            # Calculate loss
            loss = self.criterion(predictions, targets)
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                self.gradient_clip
            )
            
            self.optimizer.step()
            
            # Update metrics
            total_loss += loss.item()
            num_batches += 1
            
            # Update progress bar
            pbar.set_postfix({'loss': f'{loss.item():.4f}'})
        
        avg_loss = total_loss / num_batches
        perplexity = torch.exp(torch.tensor(avg_loss)).item()
        
        return avg_loss, perplexity
    
    def validate(self) -> Tuple[float, float]:
        """Validate model"""
        self.model.eval()
        total_loss = 0
        num_batches = 0
        
        with torch.no_grad():
            for contexts, targets in tqdm(self.val_loader, desc="Validating"):
                contexts = contexts.to(self.device)
                targets = targets.to(self.device)
                
                # Forward pass
                outputs, _ = self.model(contexts)
                predictions = outputs[:, -1, :]
                
                # Calculate loss
                loss = self.criterion(predictions, targets)
                
                total_loss += loss.item()
                num_batches += 1
        
        avg_loss = total_loss / num_batches
        perplexity = torch.exp(torch.tensor(avg_loss)).item()
        
        return avg_loss, perplexity
    
    def train(
        self,
        num_epochs: int,
        save_dir: str = "models",
        early_stopping_patience: int = 5
    ):
        """
        Train model for multiple epochs.
        
        Args:
            num_epochs: Number of epochs
            save_dir: Directory to save checkpoints
            early_stopping_patience: Patience for early stopping
        """
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        patience_counter = 0
        
        print(f"\nStarting training for {num_epochs} epochs...")
        print(f"Device: {self.device}")
        print(f"Model parameters: {self.model.count_parameters():,}")
        print(f"Model size: {self.model.get_model_size():.2f} MB\n")
        
        for epoch in range(num_epochs):
            print(f"\nEpoch {epoch + 1}/{num_epochs}")
            print("-" * 50)
            
            # Train
            train_loss, train_ppl = self.train_epoch()
            
            # Validate
            val_loss, val_ppl = self.validate()
            
            # Save history
            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['train_perplexity'].append(train_ppl)
            self.history['val_perplexity'].append(val_ppl)
            
            # Print metrics
            print(f"\nTrain Loss: {train_loss:.4f} | Train PPL: {train_ppl:.2f}")
            print(f"Val Loss: {val_loss:.4f} | Val PPL: {val_ppl:.2f}")
            
            # Save best model
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                patience_counter = 0
                
                checkpoint_path = save_path / "best_model.pt"
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'val_loss': val_loss,
                    'val_perplexity': val_ppl,
                }, checkpoint_path)
                
                print(f"✓ Saved best model (val_loss: {val_loss:.4f})")
            else:
                patience_counter += 1
                print(f"No improvement ({patience_counter}/{early_stopping_patience})")
            
            # Early stopping
            if patience_counter >= early_stopping_patience:
                print(f"\nEarly stopping triggered after {epoch + 1} epochs")
                break
        
        # Save training history
        history_path = save_path / "training_history.json"
        with open(history_path, 'w') as f:
            json.dump(self.history, f, indent=2)
        
        print(f"\n✓ Training completed!")
        print(f"Best validation loss: {self.best_val_loss:.4f}")
        print(f"Training history saved to: {history_path}")


def main():
    """Main training function"""
    
    # Load configuration
    config = get_model_config()
    model_config = config['model']
    training_config = config['training']
    
    # Set device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Load tokenizer
    print("\nLoading tokenizer...")
    tokenizer = Tokenizer("models/tokenizer.model")
    print(f"Tokenizer vocab size: {tokenizer.get_vocab_size()}")
    
    # Update vocab size in config
    model_config['vocab_size'] = tokenizer.get_vocab_size()
    
    # Create dataloaders
    print("\nCreating dataloaders...")
    train_loader, val_loader = create_dataloaders(
        train_file="data/processed/combined_train.txt",
        tokenizer=tokenizer,
        batch_size=training_config['batch_size'],
        max_seq_length=config['data']['max_sequence_length'],
        validation_split=training_config['validation_split']
    )
    
    # Create model
    print("\nCreating model...")
    model = TinyLSTM(**model_config)
    print(f"Model parameters: {model.count_parameters():,}")
    print(f"Model size: {model.get_model_size():.2f} MB")
    
    # Create trainer
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        learning_rate=training_config['learning_rate'],
        gradient_clip=training_config['gradient_clip']
    )
    
    # Train
    trainer.train(
        num_epochs=training_config['num_epochs'],
        early_stopping_patience=training_config['early_stopping_patience']
    )


if __name__ == "__main__":
    main()
