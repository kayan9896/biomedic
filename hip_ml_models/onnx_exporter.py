"""
This script exports a PyTorch (.pth) model checkpoint to ONNX format while
preserving all non-weight checkpoint metadata inside the resulting ONNX file.

Code by Maad Ebrahim for Torus Biomedical Inc., 2025-2027.

Key features:
- Loads a PyTorch checkpoint directly from disk (supports legacy raw state_dicts)
- Instantiates the model via a user-provided wrapper that handles checkpoint logic
- Infers a safe dummy input shape from checkpoint metadata (with fallbacks)
- Exports the model to ONNX using a configurable opset version
- Embeds the full checkpoint metadata (excluding the state_dict) verbatim into
  the ONNX model's metadata_props as a JSON string

This allows downstream consumers of the ONNX model to recover training-time
configuration, preprocessing parameters, and other contextual information
without requiring access to the original .pth file.

Intended use cases:
- Model deployment pipelines
- Long-term model archival
- Interoperability across frameworks while retaining provenance
"""

import json
import torch
import onnx
from onnx import StringStringEntryProto


def export_pth_to_onnx(
    model_wrapper,
    pth_path: str,
    onnx_path: str,
    opset: int = 17,
):
    """
    Export a .pth checkpoint to ONNX, embedding all checkpoint metadata
    verbatim (everything except state_dict).
    """

    # ---- Load checkpoint directly ----
    ckpt = torch.load(pth_path, map_location="cpu")

    # Handle legacy raw state_dict
    if "state_dict" not in ckpt:
        ckpt = {"state_dict": ckpt}

    # ---- Instantiate model via wrapper (uses ckpt internally) ----
    wrapper = model_wrapper(model_path=pth_path)
    model = wrapper.model
    model.eval()

    device = wrapper.device

    # ---- Dummy input inferred from metadata (fallback-safe) ----
    image_size = tuple(ckpt.get("image_size", (256, 256)))
    dummy_input = torch.zeros(
        1, 1, image_size[0], image_size[1],
        dtype=torch.float32,
        device=device,
    )

    # ---- Export to ONNX ----
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        input_names=["input"],
        output_names=["output"],
        opset_version=opset,
    )

    # ---- Embed verbatim metadata into ONNX ----
    onnx_model = onnx.load(onnx_path)

    # Everything except weights
    metadata = {
        k: v for k, v in ckpt.items()
        if k != "state_dict"
    }

    # Ensure JSON-serializable (safety)
    metadata_json = json.dumps(metadata, default=str)

    onnx_model.metadata_props.append(
        StringStringEntryProto(
            key="checkpoint",
            value=metadata_json,
        )
    )

    onnx.save(onnx_model, onnx_path)

    print(f"ONNX exported (with checkpoint metadata if available) → {onnx_path}")
