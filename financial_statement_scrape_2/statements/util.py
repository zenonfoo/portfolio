from dataclasses import dataclass
import pandas as pd


@dataclass
class Data:
    name: str
    earnings: pd.DataFrame
    ratios: pd.DataFrame
    margins: pd.DataFrame
    returns: pd.DataFrame
