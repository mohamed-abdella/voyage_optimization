# ============================
# src/ea_corridors/io.py
# ============================

from __future__ import annotations

import os
from typing import Optional

import pandas as pd


def to_latex_table(
    df: pd.DataFrame,
    filepath: str,
    float_format: str = "{:.2f}",
    index: bool = False,
) -> None:
    """
    Save DataFrame as a LaTeX tabular (without table env).

    Note: use 'booktabs' option in your main tex preamble.
    """
    def ff(x):
        try:
            return float_format.format(x)
        except Exception:
            return x

    latex = df.to_latex(index=index)
    # If you prefer rounded numbers, you can pre-round df instead of ff.

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(latex)