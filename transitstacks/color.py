from typing import Collection

import colorcet as cc

from colour import Color

BRIGHTNESS_ADJ = 0.5


def _adjust_hex(hexcolor: str, brightness_adj: float = BRIGHTNESS_ADJ) -> str:
    c = Color(hexcolor)
    c.luminance = c.luminance * brightness_adj
    return c.hex


def bg_colors(
    color_ramp: Collection = cc.glasbey_cool,
    brightness_adj: float = BRIGHTNESS_ADJ,
    quantity: int = None,
) -> Collection[str]:
    """[summary]

    Args:
        color_ramp (Collection, optional): [description]. Defaults to cc.glasbey_cool.
        brightness_adj (float, optional): [description]. Defaults to BRIGHTNESS_ADJ.
        quantity (int, optional): [description]. Defaults to None.

    Returns:
        Collection[str]: [description]
    """
    adj_color_ramp = [_adjust_hex(c, brightness_adj=brightness_adj) for c in color_ramp]
    if quantity:
        adj_color_ramp = adj_color_ramp[:quantity]
    return adj_color_ramp
