from fastapi import FastAPI

from .models import UserInput
from .utils import user_input_model_to_df
from ..src.process_scenario import post_process, run

app = FastAPI()

@app.post("/rpc/solve_plm/")
async def solve_plm(user_input: UserInput):
    df = user_input_model_to_df(user_input)
    output = post_process(ui_subbasins = user_input.subbasins, ui_bmps = df)
    return output.fillna(0).reset_index().to_dict(orient='records')