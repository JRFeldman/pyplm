import pandas

from pyplm.core import config
from pyplm.data import RUNOFF, RAINFALL, SUBBASIN_LANDUSE_AREAS, COEFFS


def calculate_runoff():
    '''Calculates runoff volume from each landuse in each subbasin
    ----------
    update: boolean indicates whether calculations should be updated, default is to not update (read from file)
    '''
    runoff = pandas.DataFrame()
    for lu in config.LAND_USES:
        land_use_areas = SUBBASIN_LANDUSE_AREAS()
        _runoff = (
            land_use_areas.assign(LU=lu)
            .rename(columns={"LU": "Land Use", lu: "Area (ac)"})
            .loc[lambda df: df["Area (ac)"] > 0][["HUC", "Area (ac)", "Land Use"]]
        )
        runoff = pandas.concat([runoff, _runoff], ignore_index=True)
    rainfall = RAINFALL()
    coeffs = COEFFS()
    runoff = (
        runoff.set_index(["HUC", "Land Use"])
        .join(rainfall.set_index("HUC"))
        .join(coeffs.set_index(["HUC", "Land Use"]))
        .sort_index()
        .assign(
            Runoff=lambda df: df["Area (ac)"]
            * df["Precip (in/yr)"]
            * df["RC"]
            / 12
            * 43560
        )
    )
    return runoff

