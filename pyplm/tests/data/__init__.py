from pathlib import Path

import pandas

datapath = Path(__file__).resolve()
datapath_dir = datapath.parent


def USER_INPUT_EXAMPLE():
    df = pandas.read_csv(datapath_dir / "S4_User_Input.csv").set_index(
        "Land Use"
    )
    return df


def KNOWN_RESULT():
    df = pandas.read_csv(datapath_dir / "S4_Load_Reduction.csv").set_index(
        ["HUC"]
    ).astype(float)
    return df

