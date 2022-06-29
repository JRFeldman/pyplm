from typing import List, Union

from pydantic import BaseModel, Field

class LandUse(BaseModel):
    name: str
    pct_implemented: float = Field(default = 0, gte = 0, lte = 100)

class BMP(BaseModel):
    name: str
    landuses: List[LandUse]

class UserInput(BaseModel):
    subbasins: List[int] 
    bmps: List[BMP]

    class Config:
        schema_extra = {
            "example":{
                "subbasins":["606","607"],
                "bmps":[{
                    "name":"Nutrient Management Plan - Agriculture",
                    "landuses":[{
                        "name":"AGR",
                        "pct_implemented": 0
                    }]
                }]
            }
        }
