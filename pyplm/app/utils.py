import pandas

from .models import UserInput
from ..core.config import LAND_USES, BMPS

def user_input_model_to_df(model: UserInput):
    bmps = model.bmps
    df = pandas.DataFrame(index = LAND_USES, columns = BMPS)
    for bmp in bmps:
        bmp_name = bmp.name
        landuses = bmp.landuses
        for lu in landuses:
            lu_name = lu.name
            percent = lu.pct_implemented
            df.loc[lu_name, bmp_name] = percent
    df.index.name = 'LandUse'
    return df