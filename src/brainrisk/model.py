"""Baseline segmentation network and stochastic (MC dropout + flip) inference."""

import itertools

import numpy as np
import torch
from monai.inferers import sliding_window_inference
from monai.networks.nets import UNet


def build_unet(seg_cfg):
    # A standard residual 3D U-Net. Dropout in every unit makes MC dropout meaningful.
    return UNet(
        spatial_dims=3,
        in_channels=4,
        out_channels=3,
        channels=tuple(seg_cfg["channels"]),
        strides=tuple(seg_cfg["strides"]),
        num_res_units=seg_cfg["num_res_units"],
        dropout=seg_cfg["dropout"],
    )


def enable_mc_dropout(model):
    model.eval()
    n = 0
    for m in model.modules():
        if isinstance(m, torch.nn.modules.dropout._DropoutNd):
            m.train()
            n += 1
    if n == 0:
        raise RuntimeError("Model has no dropout layers; MC dropout would give identical samples.")
    return n


FLIPS = [axes for k in range(4) for axes in itertools.combinations((2, 3, 4), k)]  # 8 combinations


@torch.no_grad()
def stochastic_predict(model, image, n_samples, roi_size, sw_batch_size=2, overlap=0.5,
                       tta_flips=True, amp=True):
    """Return sigmoid probabilities, shape [S, 3, X, Y, Z], float16 on CPU.

    Each pass keeps dropout active; with tta_flips the passes also cycle through
    the 8 axis-flip combinations, so S passes cost the same either way.
    """
    enable_mc_dropout(model)
    samples = []
    for i in range(n_samples):
        axes = FLIPS[i % len(FLIPS)] if tta_flips else ()
        x = torch.flip(image, axes) if axes else image
        with torch.autocast(device_type=image.device.type, enabled=amp and image.device.type == "cuda"):
            logits = sliding_window_inference(x, roi_size, sw_batch_size, model, overlap=overlap)
        if axes:
            logits = torch.flip(logits, axes)
        samples.append(torch.sigmoid(logits.float())[0].cpu().numpy().astype(np.float16))
    return np.stack(samples)
