import unittest

import numpy as np

from rsi4tun.ring_theta_split import split_ring_source_by_theta


class RingThetaSplitTests(unittest.TestCase):
    def test_splits_original_b2_rows_after_the_cycle(self):
        source = np.array([6, 6, 6, 4, 6])
        shifted = np.array([1, 1, 1, 5, 1])
        rings = np.array([2, 2, 2, 2, 3])
        theta = np.array([10.0, 12.4, 13.0, 10.0, 10.0])
        out = split_ring_source_by_theta(
            shifted,
            source,
            rings,
            theta,
            ring=2,
            source_label=6,
            theta_cut=12.4,
            below_label=2,
            at_or_above_label=1,
        )
        np.testing.assert_array_equal(out, np.array([2, 1, 1, 5, 1]))
