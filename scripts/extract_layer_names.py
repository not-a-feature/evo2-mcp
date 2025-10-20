#!/usr/bin/env python3
"""Extract layer names from all Evo2 checkpoints and save to file.

This script loads different Evo2 checkpoints directly using the Evo2 package
and extracts all layer names from the model architecture. The results are
saved to a JSON file for documentation purposes.

Usage:
    python extract_layer_names.py
"""

import json
from typing import Any, Dict, List

from evo2 import Evo2  # type: ignore[import]


def get_model_layers(model: Any) -> List[str]:
    """Extract all layer names from model by inspecting its state dict.

    Extracts layer names from the model's state dict keys, which represent
    the full parameter paths in the model architecture (e.g., 'blocks.2.mlp.l3').

    Parameters
    ----------
    model : Any
        The Evo2 model instance.

    Returns
    -------
    List[str]
        Sorted list of all layer names in the model.
    """
    layers = []

    inner_model = model.model
    print(f"  DEBUG: Found inner model: {type(inner_model)}")
    if hasattr(inner_model, "state_dict"):
        state_dict = inner_model.state_dict()
        print(f"  DEBUG: Total state_dict keys: {len(state_dict)}")
        print(f"  DEBUG: First 5 keys: {list(state_dict.keys())[:5]}")

        # Extract unique layer prefixes by removing parameter suffixes
        for key in state_dict.keys():
            # Remove common parameter suffixes
            layer = key
            for suffix in [".weight", ".bias", ".scale", ".scale_inv", ".t", "._extra_state"]:
                if layer.endswith(suffix):
                    layer = layer[: -len(suffix)]
                    break

            if layer:
                layers.append(layer)

        # Remove duplicates and sort
        layers = sorted(set(layers))

    return layers


def main() -> None:
    """Load all checkpoints and extract layer names."""
    # List of all available Evo2 checkpoints
    checkpoints = [
        "evo2_1b_base",
        "evo2_7b",
        "evo2_40b",
        "evo2_7b_base",
        "evo2_40b_base",
    ]

    output: Dict[str, Any] = {}

    print(f"Processing {len(checkpoints)} checkpoints...")

    for checkpoint_name in checkpoints:
        print(f"\nLoading checkpoint: {checkpoint_name}")

        try:
            # Load the model checkpoint directly from Evo2
            model = Evo2(checkpoint_name)

            # Extract layer names
            layers = get_model_layers(model)

            # Store results
            output[checkpoint_name] = {
                "layer_count": len(layers),
                "layers": layers,
            }

            print(f"  ✓ Found {len(layers)} layers")

            # Print first few and last few layer names for verification
            if layers:
                print(f"    First layers: {layers[:3]}")
                if len(layers) > 3:
                    print(f"    Last layers: {layers[-3:]}")

        except Exception as e:
            print(f"  X Error loading checkpoint {checkpoint_name}: {e}")
            output[checkpoint_name] = {
                "error": str(e),
                "layers": [],
            }
    output_file = "layers.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n. Results saved to {output_file}")

    # Print summary
    successful = sum(1 for cp in output.values() if "error" not in cp)
    print(f"\nSummary: {successful}/{len(checkpoints)} checkpoints processed successfully")


if __name__ == "__main__":
    main()
