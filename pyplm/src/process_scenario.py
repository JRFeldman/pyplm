from typing import List

import pandas
# from pyplm.src.loading import calculate_pre_bmp_load
from pyplm.src.loading import calculate_post_bmp_load
from pyplm.src.loading import calculate_load_reduction
from pyplm.src.loading import calculate_percent_reduction

from pyplm.data import PRE_BMP_LOAD

def run(ui_subbasins: List[int], ui_bmps: pandas.DataFrame) -> pandas.DataFrame:

    pre_bmp_load = (PRE_BMP_LOAD() #calculate_pre_bmp_load()
    .reset_index().groupby(['HUC']).sum()
    )
    pre_bmp_load.round(3).to_csv('Pre-BMP_Load.csv')

    post_bmp_load = (calculate_post_bmp_load(ui_subbasins, ui_bmps)
    .reset_index().groupby(['HUC']).sum()
    )
    post_bmp_load.round(3).to_csv('Post-BMP_Load.csv')

    load_reduction = calculate_load_reduction(pre_bmp_load, post_bmp_load)
    load_reduction.round(3).to_csv('Load_Reduction.csv')

    return load_reduction 

def post_process(ui_subbasins: List[int], ui_bmps: pandas.DataFrame) -> pandas.DataFrame:

    load_reduction = run(ui_subbasins, ui_bmps)

    pre_bmp_load = (PRE_BMP_LOAD() #calculate_pre_bmp_load()
    .reset_index().groupby(['HUC']).sum()
    )
    
    percent_reduction = calculate_percent_reduction(pre_bmp_load, load_reduction).round(3)
    percent_reduction.to_csv('Load_Reduction_Percent.csv')

    return percent_reduction 

# if __name__ == "__main__":
    # run()

