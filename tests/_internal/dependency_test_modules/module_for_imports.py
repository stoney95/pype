import pandas as pd
import numpy as np

from numpy.testing import assert_array_equal


from .helper_module import try_request

def add(x: int, y: int) -> int:
    try_request()
    return x + y


def process(df: pd.DataFrame) -> np.ndarray:
    arr = df.to_numpy()
    ones = np.ones(arr.shape)

    assert_array_equal(ones, ones)

    return arr + ones