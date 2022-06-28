import sys
import os
import pandas as pd
from typing import List
from statements.util import Data

sys.stdout = open(os.devnull, 'w')

from statements.Gilead_Sciences.script import gilead
from statements.Biogen.script import biogen

sys.stdout = sys.__stdout__


def compare_line(data: List[Data], df_name, line_name: str):
    results = []
    for d in data:
        df = d.__dict__[df_name]
        line = df.loc[line_name]
        line.name = d.name
        results.append(pd.DataFrame(line).transpose())
    final_df = pd.concat(results)
    final_df.index.name = line_name
    return final_df


results = compare_line([gilead, biogen], 'margins', 'R&D Margin')
