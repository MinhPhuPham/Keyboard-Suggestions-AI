"""
Inference engine for next-word prediction
Combines model, custom dictionary, and rule engine
"""

import torch
import numpy as np
from typing import List, Tuple, Optional, Dict
from pathlib import Path

import sys
sys.path.append('src')

from model.tiny_lstm import TinyLSTM
from tokenizer.train_tokenizer import Tokenizer
from dictionary.custom_dict import CustomDictionary
from rules.rule_engine import LanguageRuleEngine
from utils.config_loader import get_model_config, get_language_rules


class PredictionEngine:
    """
    Main prediction engine combining all components.
    
    Flow:
    1. Check custom dictionary for prefix matches
    2. Get model predictions
    3. Apply language rules
    4. Filter with no-mean filter
    5. Merge and rank results
    """
    
    def __init__(
        self,
        model_path: str,
        tokenizer_path: str,
        dictionary_path: Optional[str] = None,
        rules_config: Optional[Dict] = None,
        device: str = "cpu"
    ):
        self.device = device
        
        # Load tokenizer
        print("Loading tokenizer...")
        self.tokenizer = Tokenizer(tokenizer_path)
        
        # Load model
        print("Loading model...")
        self.model = self._load_model(model_path)
        self.model.eval()
        
        # Load custom dictionary
        print("Loading custom dictionary...")
        self.dictionary = CustomDictionary(dictionary_path) if dictionary_path else CustomDictionary()
        
        # Load rule engine
        print("Loading rule engine...")
        self.rule_engine = LanguageRuleEngine(rules_config or get_language_rules())
        
        print("✓ Prediction engine ready!")
    
    def _load_model(self, model_path: str) -> TinyLSTM:
        """Load trained model from checkpoint"""
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # Get model config
        config = get_model_config()
        model_config = config['model']
        model_config['vocab_size'] = self.tokenizer.get_vocab_size()
        
        # Create model
        model = TinyLSTM(**model_config)
        
        # Load weights
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(self.device)
        
        return model
    
    def predict(
        self,
        text: str,
        language: str = "en",
        top_k: int = 5,
        temperature: float = 1.0,
        include_custom: bool = True
    ) -> List[Tuple[str, float]]:
        """
        Predict next words for given text.
        
        Args:
            text: Input text
            language: Language code (en, ja)
            top_k: Number of predictions to return
            temperature: Sampling temperature
            include_custom: Whether to include custom dictionary matches
        
        Returns:
            List of (word, confidence) tuples
        """
        results = []
        
        # 1. Check custom dictionary
        custom_matches = []
        if include_custom:
            # Get last word as prefix
            words = text.strip().split()
            if words:
                prefix = words[-1].lower()
                custom_matches = self.dictionary.prefix_search(prefix, max_results=top_k)
        
        # 2. Get model predictions
        model_predictions = self._get_model_predictions(
            text, language, top_k * 2, temperature
        )
        
        # 3. Merge results (custom first, then model)
        seen = set()
        
        # Add custom matches with high confidence
        for match in custom_matches:
            if match not in seen:
                results.append((match, 1.0))  # Custom matches get max confidence
                seen.add(match)
        
        # Add model predictions
        for word, conf in model_predictions:
            if word not in seen and len(results) < top_k:
                results.append((word, conf))
                seen.add(word)
        
        return results[:top_k]
    
    def _get_model_predictions(
        self,
        text: str,
        language: str,
        top_k: int,
        temperature: float
    ) -> List[Tuple[str, float]]:
        """Get predictions from model"""
        # Tokenize input
        token_ids = self.tokenizer.encode(text)
        
        if not token_ids:
            return []
        
        # Convert to tensor
        x = torch.tensor([token_ids], dtype=torch.long).to(self.device)
        
        # Get model predictions
        with torch.no_grad():
            probs, _ = self.model.predict_next(x, temperature=temperature)
            probs = probs[0].cpu().numpy()  # (vocab_size,)
        
        # Apply language rules (logit biasing)
        logits = np.log(probs + 1e-10)  # Convert back to logits
        
        # Get token pieces for rule application
        token_pieces = [self.tokenizer.id_to_piece(i) for i in range(len(logits))]
        token_ids_list = list(range(len(logits)))
        
        # Apply rules
        logits = self.rule_engine.apply_rules(
            logits, token_ids_list, token_pieces, language
        )
        
        # Convert back to probabilities
        probs = np.exp(logits)
        probs = probs / probs.sum()  # Renormalize
        
        # Get top-k predictions
        top_indices = np.argsort(probs)[-top_k:][::-1]
        
        predictions = []
        for idx in top_indices:
            word = self.tokenizer.id_to_piece(int(idx))
            confidence = float(probs[idx])
            predictions.append((word, confidence))
        
        # Filter with no-mean filter
        predictions = self.rule_engine.filter_predictions(predictions, language)
        
        return predictions
    
    def get_suggestions(
        self,
        text: str,
        language: str = "en",
        top_k: int = 5
    ) -> List[str]:
        """
        Get suggestion strings (without confidence scores).
        
        Args:
            text: Input text
            language: Language code
            top_k: Number of suggestions
        
        Returns:
            List of suggestion strings
        """
        predictions = self.predict(text, language, top_k)
        return [word for word, _ in predictions]
    
    def reload_dictionary(self):
        """Hot-reload custom dictionary"""
        self.dictionary.reload()


def test_prediction_engine():
    """Test prediction engine with examples"""
    
    # Check if model exists
    model_path = Path("models/best_model.pt")
    tokenizer_path = Path("models/tokenizer.model")
    dict_path = Path("config/custom_dictionary.json")
    
    if not model_path.exists():
        print("Error: Model not found. Please train the model first.")
        print("Run: python src/model/train.py")
        return
    
    if not tokenizer_path.exists():
        print("Error: Tokenizer not found. Please train tokenizer first.")
        print("Run: python src/tokenizer/train_tokenizer.py")
        return
    
    # Create prediction engine
    engine = PredictionEngine(
        model_path=str(model_path),
        tokenizer_path=str(tokenizer_path),
        dictionary_path=str(dict_path) if dict_path.exists() else None
    )
    
    # Test cases from example data
    test_cases = [
        ("I'm going to", "en"),
        ("wanna", "en"),
        ("I love", "en"),
        ("Check this out", "en"),
        ("ty", "en"),  # Custom dictionary
        ("ac", "en"),  # Custom dictionary
        ("今日は", "ja"),
        ("ありがとう", "ja"),
    ]
    
    print("\n" + "=" * 80)
    print("Testing Prediction Engine")
    print("=" * 80)
    
    for text, language in test_cases:
        suggestions = engine.predict(text, language, top_k=5)
        
        print(f"\nInput: '{text}' (Language: {language})")
        print("Suggestions:")
        for i, (word, conf) in enumerate(suggestions, 1):
            print(f"  {i}. {word} (confidence: {conf:.3f})")


if __name__ == "__main__":
    test_prediction_engine()
