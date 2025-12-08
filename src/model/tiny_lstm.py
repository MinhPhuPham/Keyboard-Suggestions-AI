"""
TinyLSTM Model for Next-Word Prediction
Optimized for mobile deployment with minimal size
"""

import torch
import torch.nn as nn
from typing import Tuple, Optional


class TinyLSTM(nn.Module):
    """
    Tiny LSTM model for next-word prediction.
    
    Architecture:
    - Embedding layer (vocab_size -> embedding_dim)
    - LSTM layer (embedding_dim -> hidden_dim)
    - Output layer (hidden_dim -> vocab_size)
    
    Args:
        vocab_size: Size of vocabulary
        embedding_dim: Dimension of word embeddings
        hidden_dim: Dimension of LSTM hidden state
        num_layers: Number of LSTM layers
        dropout: Dropout probability
    """
    
    def __init__(
        self,
        vocab_size: int = 25000,
        embedding_dim: int = 64,
        hidden_dim: int = 128,
        num_layers: int = 1,
        dropout: float = 0.2
    ):
        super(TinyLSTM, self).__init__()
        
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        
        # LSTM layer
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Dropout for regularization
        self.dropout = nn.Dropout(dropout)
        
        # Output layer
        self.fc = nn.Linear(hidden_dim, vocab_size)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights with Xavier uniform initialization"""
        nn.init.xavier_uniform_(self.embedding.weight)
        nn.init.xavier_uniform_(self.fc.weight)
        nn.init.zeros_(self.fc.bias)
        
        # Initialize LSTM weights
        for name, param in self.lstm.named_parameters():
            if 'weight' in name:
                nn.init.xavier_uniform_(param)
            elif 'bias' in name:
                nn.init.zeros_(param)
    
    def forward(
        self,
        x: torch.Tensor,
        hidden: Optional[Tuple[torch.Tensor, torch.Tensor]] = None
    ) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        Forward pass through the model.
        
        Args:
            x: Input tensor of shape (batch_size, seq_len)
            hidden: Optional hidden state tuple (h_0, c_0)
        
        Returns:
            output: Logits of shape (batch_size, seq_len, vocab_size)
            hidden: Hidden state tuple (h_n, c_n)
        """
        # Embedding: (batch_size, seq_len) -> (batch_size, seq_len, embedding_dim)
        embedded = self.embedding(x)
        embedded = self.dropout(embedded)
        
        # LSTM: (batch_size, seq_len, embedding_dim) -> (batch_size, seq_len, hidden_dim)
        if hidden is None:
            lstm_out, hidden = self.lstm(embedded)
        else:
            lstm_out, hidden = self.lstm(embedded, hidden)
        
        # Dropout
        lstm_out = self.dropout(lstm_out)
        
        # Output: (batch_size, seq_len, hidden_dim) -> (batch_size, seq_len, vocab_size)
        output = self.fc(lstm_out)
        
        return output, hidden
    
    def predict_next(
        self,
        x: torch.Tensor,
        hidden: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        temperature: float = 1.0
    ) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        Predict next token probabilities.
        
        Args:
            x: Input tensor of shape (batch_size, seq_len)
            hidden: Optional hidden state
            temperature: Temperature for softmax (higher = more random)
        
        Returns:
            probs: Probabilities of shape (batch_size, vocab_size)
            hidden: Updated hidden state
        """
        with torch.no_grad():
            output, hidden = self.forward(x, hidden)
            
            # Get logits for last token
            logits = output[:, -1, :] / temperature
            
            # Apply softmax
            probs = torch.softmax(logits, dim=-1)
            
            return probs, hidden
    
    def get_model_size(self) -> float:
        """
        Calculate model size in MB.
        
        Returns:
            Model size in megabytes
        """
        param_size = sum(p.numel() * p.element_size() for p in self.parameters())
        buffer_size = sum(b.numel() * b.element_size() for b in self.buffers())
        size_mb = (param_size + buffer_size) / (1024 ** 2)
        return size_mb
    
    def count_parameters(self) -> int:
        """
        Count total number of trainable parameters.
        
        Returns:
            Number of parameters
        """
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


def create_model(config: dict) -> TinyLSTM:
    """
    Create TinyLSTM model from configuration.
    
    Args:
        config: Model configuration dictionary
    
    Returns:
        Initialized TinyLSTM model
    """
    model = TinyLSTM(
        vocab_size=config.get('vocab_size', 25000),
        embedding_dim=config.get('embedding_dim', 64),
        hidden_dim=config.get('hidden_dim', 128),
        num_layers=config.get('num_layers', 1),
        dropout=config.get('dropout', 0.2)
    )
    
    return model


if __name__ == "__main__":
    # Test model creation
    model = TinyLSTM()
    print(f"Model created successfully!")
    print(f"Total parameters: {model.count_parameters():,}")
    print(f"Model size: {model.get_model_size():.2f} MB")
    
    # Test forward pass
    batch_size = 4
    seq_len = 10
    x = torch.randint(0, 25000, (batch_size, seq_len))
    
    output, hidden = model(x)
    print(f"\nInput shape: {x.shape}")
    print(f"Output shape: {output.shape}")
    
    # Test prediction
    probs, _ = model.predict_next(x)
    print(f"Prediction probabilities shape: {probs.shape}")
