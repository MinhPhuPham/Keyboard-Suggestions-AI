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
    
    def __init__(self, model: TinyLSTM, vocab_size: int):
        self.model = model
        self.vocab_size = vocab_size
        self.model.eval()
        
        # Create dummy input for export
        self.dummy_input = torch.randint(
            0, vocab_size,
            (1, 50),  # batch_size=1, seq_length=50
            dtype=torch.long
        )
    
    def export_to_onnx(
        self,
        output_path: str,
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
        # Initialize a dummy input for ONNX export
    def export_to_torchscript(self, output_path: str):
        """Export model to TorchScript format (more stable than ONNX)"""
        self.model.eval()
        
        print(f"Exporting model to TorchScript...")
        print(f"  Input shape: {self.dummy_input.shape}")
        
        # Trace the model
        traced_model = torch.jit.trace(self.model, self.dummy_input)
        
        # Save traced model
        traced_model.save(output_path)
        
        print(f"✓ Model exported to: {output_path}")
        
        # Get file size
        size_mb = Path(output_path).stat().st_size / (1024 ** 2)
        print(f"  Size: {size_mb:.2f} MB")
        
        return output_path
    
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
    
    # Export to TorchScript (more stable than ONNX for LSTM)
    torchscript_path = output_path / "tiny_lstm.pt"
    exporter.export_to_torchscript(str(torchscript_path))
    
    # Test inference
    test_input = torch.randint(
        0, model_config['vocab_size'],
        (1, 10),
        dtype=torch.long
    )
    
    print(f"\nTesting TorchScript model:")
    traced_model = torch.jit.load(str(torchscript_path))
    traced_model.eval()
    
    with torch.no_grad():
        output = traced_model(test_input)
    
    print(f"✓ Inference successful")
    print(f"  Input shape: {test_input.shape}")
    print(f"  Output shape: {output[0].shape if isinstance(output, tuple) else output.shape}")
    
    print("\n" + "=" * 80)
    print("Export Summary:")
    print("=" * 80)
    print(f"TorchScript model: {torchscript_path}")
    print(f"\nThis model can be converted to:")
    print(f"  - iOS: Core ML (use coremltools)")
    print(f"  - Android: TFLite (use onnx-tf)")
    print(f"\nSee scripts/export_coreml.py and scripts/export_tflite.py")


if __name__ == "__main__":
    export_model_for_mobile()
