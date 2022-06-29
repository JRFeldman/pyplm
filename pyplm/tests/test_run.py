from pandas.testing import assert_frame_equal

from pyplm.core.config import SUBBASINS
from pyplm.tests.data import USER_INPUT_EXAMPLE, KNOWN_RESULT
from pyplm.src.process_scenario import run


def test_run_end_to_end():

    ui_subbasins = SUBBASINS
    ui_bmps = USER_INPUT_EXAMPLE()
    
    output = run(ui_subbasins, ui_bmps).round(3)

    known_result =  KNOWN_RESULT().round(3)

    assert_frame_equal(output, known_result, rtol = 1e-3)




