"""
Model export utilities for mobile deployment
Supports ONNX export and quantization
"""

import torch
import torch.onnx
from pathlib import Path
import onnx
import onnxruntime as ort
import numpy as np

import sys
sys.path.append('src')

from model.tiny_lstm import TinyLSTM
from utils.config_loader import get_model_config


class ModelExporter:
    """Export PyTorch model to ONNX format for mobile deployment"""
    
    def __init__(self, model: TinyLSTM, tokenizer_vocab_size: int):
        self.model = model
        self.vocab_size = tokenizer_vocab_size
    
    def export_to_onnx(
        self,
        output_path: str,
        batch_size: int = 1,
        seq_length: int = 50,
        opset_version: int = 14
    ):
        """
        Export model to ONNX format.
        
        Args:
            output_path: Path to save ONNX model
            batch_size: Batch size for export
            seq_length: Sequence length
            opset_version: ONNX opset version
        """
        self.model.eval()
        
        # Create dummy input
        dummy_input = torch.randint(
            0, self.vocab_size,
            (batch_size, seq_length),
            dtype=torch.long
        )
        
        # Export to ONNX
        print(f"Exporting model to ONNX...")
        print(f"  Input shape: {dummy_input.shape}")
        print(f"  Opset version: {opset_version}")
        
        torch.onnx.export(
            self.model,
            dummy_input,
            output_path,
            export_params=True,
            opset_version=opset_version,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={
                'input': {0: 'batch_size', 1: 'seq_length'},
                'output': {0: 'batch_size', 1: 'seq_length'}
            }
        )
        
        print(f"✓ Model exported to: {output_path}")
        
        # Verify ONNX model
        self._verify_onnx_model(output_path)
    
    def _verify_onnx_model(self, onnx_path: str):
        """Verify exported ONNX model"""
        print("\nVerifying ONNX model...")
        
        # Load and check model
        onnx_model = onnx.load(onnx_path)
        onnx.checker.check_model(onnx_model)
        
        print("✓ ONNX model is valid")
        
        # Get model size
        size_mb = Path(onnx_path).stat().st_size / (1024 ** 2)
        print(f"  Model size: {size_mb:.2f} MB")
    
    def quantize_onnx(
        self,
        input_path: str,
        output_path: str,
        quantization_mode: str = "int8"
    ):
        """
        Quantize ONNX model to reduce size.
        
        Args:
            input_path: Input ONNX model path
            output_path: Output quantized model path
            quantization_mode: Quantization mode (int8, uint8)
        """
        try:
            from onnxruntime.quantization import quantize_dynamic, QuantType
            
            print(f"\nQuantizing model to {quantization_mode}...")
            
            # Determine quantization type
            quant_type = QuantType.QInt8 if quantization_mode == "int8" else QuantType.QUInt8
            
            # Quantize
            quantize_dynamic(
                input_path,
                output_path,
                weight_type=quant_type
            )
            
            # Compare sizes
            original_size = Path(input_path).stat().st_size / (1024 ** 2)
            quantized_size = Path(output_path).stat().st_size / (1024 ** 2)
            reduction = (1 - quantized_size / original_size) * 100
            
            print(f"✓ Model quantized successfully")
            print(f"  Original size: {original_size:.2f} MB")
            print(f"  Quantized size: {quantized_size:.2f} MB")
            print(f"  Size reduction: {reduction:.1f}%")
            
        except ImportError:
            print("Warning: onnxruntime quantization not available")
            print("Install with: pip install onnxruntime")
    
    def test_onnx_inference(self, onnx_path: str, test_input: np.ndarray):
        """
        Test ONNX model inference.
        
        Args:
            onnx_path: Path to ONNX model
            test_input: Test input array
        """
        print(f"\nTesting ONNX inference...")
        
        # Create inference session
        session = ort.InferenceSession(onnx_path)
        
        # Get input/output names
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        
        # Run inference
        result = session.run([output_name], {input_name: test_input})
        
        print(f"✓ Inference successful")
        print(f"  Input shape: {test_input.shape}")
        print(f"  Output shape: {result[0].shape}")
        
        return result[0]


def export_model_for_mobile(
    model_path: str = "models/best_model.pt",
    output_dir: str = "models/mobile"
):
    """
    Export trained model for mobile deployment.
    
    Args:
        model_path: Path to trained PyTorch model
        output_dir: Output directory for exported models
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load model config
    config = get_model_config()
    model_config = config['model']
    
    # Load checkpoint
    print(f"Loading model from: {model_path}")
    checkpoint = torch.load(model_path, map_location='cpu')
    
    # Create model
    model = TinyLSTM(**model_config)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    print(f"✓ Model loaded")
    print(f"  Parameters: {model.count_parameters():,}")
    print(f"  Size: {model.get_model_size():.2f} MB")
    
    # Create exporter
    exporter = ModelExporter(model, model_config['vocab_size'])
    
    # Export to ONNX
    onnx_path = output_path / "tiny_lstm.onnx"
    exporter.export_to_onnx(str(onnx_path))
    
    # Quantize model
    quantized_path = output_path / "tiny_lstm_int8.onnx"
    exporter.quantize_onnx(str(onnx_path), str(quantized_path), "int8")
    
    # Test inference
    test_input = np.random.randint(
        0, model_config['vocab_size'],
        (1, 10),
        dtype=np.int64
    )
    
    print("\nTesting original ONNX model:")
    exporter.test_onnx_inference(str(onnx_path), test_input)
    
    print("\nTesting quantized ONNX model:")
    exporter.test_onnx_inference(str(quantized_path), test_input)
    
    print("\n" + "=" * 80)
    print("Export Summary:")
    print("=" * 80)
    print(f"Original ONNX: {onnx_path}")
    print(f"Quantized ONNX: {quantized_path}")
    print("\nThese models can be integrated into iOS/Android apps")


if __name__ == "__main__":
    export_model_for_mobile()
