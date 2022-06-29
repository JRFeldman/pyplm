from fastapi.testclient import TestClient

from ..app.app import app

client = TestClient(app)

def test_solve_plm():
    response = client.post(
        "/rpc/solve_plm/",
        json = {
            "subbasins":["606","607"],
            "bmps":[{
                "name":"Nutrient Management Plan - Agriculture",
                "landuses":[{
                    "name":"AGR",
                    "pct_implemented": 0
                }]
            }]
        }
    )
    assert response.status_code == 200