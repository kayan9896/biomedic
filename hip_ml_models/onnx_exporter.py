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
