import unittest

import numpy as np

from rsi4tun.dark_lining import drop_dark_lining


class DarkLiningTests(unittest.TestCase):
    def test_drops_lining_darker_than_the_cut_and_keeps_the_boundary(self):
        labels = np.array([0, 4, 1, 6, 2])
        intensity = np.array([-1500.0, -1500.0, -1400.0, -1399.0, -1600.0])
        out = drop_dark_lining(labels, intensity, below=-1400)
        np.testing.assert_array_equal(out, np.array([0, 0, 1, 6, 0]))
