from pathlib import Path

import pandas


datapath = Path(__file__).resolve()
datapath_dir = datapath.parent


def ATTENUATION_REMOVAL():
    df = pandas.read_csv(datapath_dir / "Subbasin_Attenuation_Percent_Removal.csv").set_index(
        "Subbasin"
    )
    return df


def BMP_HYDR_PERF():
    df = pandas.read_csv(datapath_dir / "BMP_Hydraulic_Performance.csv").set_index(
        "BMP Name"
    )
    return df


def BMP_WQ_TYPE():
    df = pandas.read_csv(datapath_dir / "BMP_Performance_Type.csv").set_index(
        "BMP Name"
    )
    return df


def BMP_WQ_PERF():
    df = pandas.read_csv(datapath_dir / "BMP_WQ_Performance.csv").set_index(
        "BMP Name"
    )
    return df

def COEFFS():
    df = pandas.read_csv(datapath_dir / "Subcatchment_RCs.csv").rename(
        columns={"Average of Runoff Coefficient": "RC"}
    )
    return df


def EMCS():
    df = pandas.read_csv(datapath_dir / "Landuse_Pollutant_EMCs.csv").set_index(
        "Pollutant"
    )
    return df


def PRE_BMP_LOAD():
    df = pandas.read_csv(datapath_dir / "Pre-BMP_Load_Results.csv").set_index(
        ["HUC","Land Use"]
    )
    return df


def POL_MIN_CONC():
    df = pandas.read_csv(datapath_dir / "Pollutant_Minimum_Concentrations.csv").set_index(
        "Pollutant"
    )
    return df


def RAINFALL():
    df = pandas.read_csv(datapath_dir / "Subbasin_Rainfall.csv")
    return df


def RUNOFF():
    df = pandas.read_csv(datapath_dir / "Runoff_Results.csv").set_index(
        ["HUC", "Land Use"]
    )
    return df


def SUBBASIN_LANDUSE_AREAS():
    df = pandas.read_csv(datapath_dir / "Subbasin_Landuses.csv").rename(
        columns={"Subcatchment": "HUC"}
    )
    return df
