"""
Export PyTorch model to Core ML format for iOS deployment
"""

import torch
import coremltools as ct
from pathlib import Path
import json

import sys
sys.path.append('src')

from model.tiny_lstm import TinyLSTM
from utils.config_loader import get_model_config


def export_to_coreml(
    pytorch_model_path: str,
    output_dir: str = "ios/KeyboardAI",
    model_name: str = "KeyboardAI"
):
    """
    Export PyTorch model to Core ML format.
    
    Args:
        pytorch_model_path: Path to trained PyTorch model (.pt)
        output_dir: Output directory for Core ML model
        model_name: Name for the Core ML model
    """
    print("="*70)
    print("Exporting to Core ML for iOS")
    print("="*70)
    
    # Load model config
    config = get_model_config()
    model_config = config['model']
    
    # Load PyTorch model
    print(f"\n1. Loading PyTorch model from: {pytorch_model_path}")
    checkpoint = torch.load(pytorch_model_path, map_location='cpu')
    
    model = TinyLSTM(**model_config)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    print(f"   ✓ Model loaded")
    print(f"   Parameters: {model.count_parameters():,}")
    print(f"   Size: {model.get_model_size():.2f} MB")
    
    # Create example input
    batch_size = 1
    seq_length = 50
    example_input = torch.randint(
        0, model_config['vocab_size'],
        (batch_size, seq_length),
        dtype=torch.long
    )
    
    print(f"\n2. Tracing model with example input")
    print(f"   Input shape: {example_input.shape}")
    
    # Trace the model
    traced_model = torch.jit.trace(model, example_input)
    
    print(f"   ✓ Model traced successfully")
    
    # Convert to Core ML
    print(f"\n3. Converting to Core ML format")
    
    # Define input
    input_shape = ct.Shape(shape=(1, ct.RangeDim(1, 512)))  # Variable sequence length
    
    mlmodel = ct.convert(
        traced_model,
        inputs=[ct.TensorType(name="input_ids", shape=input_shape, dtype=int)],
        outputs=[ct.TensorType(name="logits")],
        minimum_deployment_target=ct.target.iOS15,
        compute_precision=ct.precision.FLOAT16  # Use FP16 for smaller size
    )
    
    # Add metadata
    mlmodel.author = "Keyboard Suggestions AI"
    mlmodel.license = "MIT"
    mlmodel.short_description = "Multilingual next-word prediction model"
    mlmodel.version = "1.0.0"
    
    # Add input/output descriptions
    mlmodel.input_description["input_ids"] = "Token IDs from SentencePiece tokenizer"
    mlmodel.output_description["logits"] = "Prediction logits for next token"
    
    print(f"   ✓ Converted to Core ML")
    
    # Save model
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    model_path = output_path / f"{model_name}.mlpackage"
    mlmodel.save(str(model_path))
    
    print(f"\n4. Model saved to: {model_path}")
    
    # Get model size
    import os
    size_mb = sum(
        os.path.getsize(os.path.join(dirpath, filename))
        for dirpath, _, filenames in os.walk(model_path)
        for filename in filenames
    ) / (1024 ** 2)
    
    print(f"   Size: {size_mb:.2f} MB")
    
    # Save metadata
    metadata = {
        "model_name": model_name,
        "version": "1.0.0",
        "vocab_size": model_config['vocab_size'],
        "embedding_dim": model_config['embedding_dim'],
        "hidden_dim": model_config['hidden_dim'],
        "model_size_mb": round(size_mb, 2),
        "input_name": "input_ids",
        "output_name": "logits",
        "min_ios_version": "15.0",
        "compute_precision": "FLOAT16"
    }
    
    metadata_path = output_path / "model_info.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"   Metadata: {metadata_path}")
    
    print("\n" + "="*70)
    print("✓ Core ML export complete!")
    print("="*70)
    print(f"\nFiles created in {output_dir}/:")
    print(f"  - {model_name}.mlpackage (Core ML model)")
    print(f"  - model_info.json (Metadata)")
    
    return str(model_path)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Export model to Core ML")
    parser.add_argument(
        "--model",
        default="models/best_model.pt",
        help="Path to PyTorch model"
    )
    parser.add_argument(
        "--output",
        default="ios/KeyboardAI",
        help="Output directory"
    )
    parser.add_argument(
        "--name",
        default="KeyboardAI",
        help="Model name"
    )
    
    args = parser.parse_args()
    
    # Check if model exists
    if not Path(args.model).exists():
        print(f"Error: Model not found: {args.model}")
        print("\nPlease train the model first:")
        print("  python src/model/train.py")
        exit(1)
    
    # Check if coremltools is installed
    try:
        import coremltools
    except ImportError:
        print("Error: coremltools not installed")
        print("\nInstall with:")
        print("  pip install coremltools")
        exit(1)
    
    export_to_coreml(args.model, args.output, args.name)
