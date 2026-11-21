import sys
import tracemalloc
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sam4tun"))

from helpers.proud_lining import drop_proud_lining


class ProudLiningTests(unittest.TestCase):
    def test_drops_a_point_proud_of_its_neighbours(self):
        h = np.array([0.0, 0.02, 0.04, 0.06, 0.08])
        theta = np.zeros(5)
        radius = np.array([2.75, 2.75, 2.76, 2.75, 2.75])
        pred = np.array([1, 1, 1, 1, 1])
        out = drop_proud_lining(h, theta, radius, pred, 0.10, 0.005)
        self.assertEqual(out.tolist(), [1, 1, 0, 1, 1])

    def test_keeps_an_inset_point(self):
        h = np.array([0.0, 0.02, 0.04, 0.06, 0.08])
        theta = np.zeros(5)
        radius = np.array([2.75, 2.75, 2.74, 2.75, 2.75])
        pred = np.ones(5, dtype=int)
        out = drop_proud_lining(h, theta, radius, pred, 0.10, 0.005)
        self.assertEqual(out.tolist(), [1, 1, 1, 1, 1])

    def test_neighbourhood_wraps_theta(self):
        period = float(2 * np.pi * 2.75)
        h = np.zeros(3)
        theta = np.array([0.0, period - 0.03, 1.0])
        radius = np.array([2.76, 2.75, 2.75])
        pred = np.ones(3, dtype=int)
        out = drop_proud_lining(h, theta, radius, pred, 0.10, 0.005)
        self.assertEqual(int(out[0]), 0)
        self.assertEqual(int(out[1]), 1)
        self.assertEqual(int(out[2]), 1)

    def test_dense_neighbourhood_does_not_hold_every_pair(self):
        count = 2500
        h = np.linspace(0.0, 0.04, count)
        theta = np.zeros(count)
        radius = np.full(count, 2.75)
        radius[2000] = 2.80
        pred = np.ones(count, dtype=int)
        tracemalloc.start()
        out = drop_proud_lining(h, theta, radius, pred, 0.10, 0.005)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.assertLess(peak, 64 * 1024 * 1024)
        self.assertEqual(int(out[2000]), 0)
        self.assertEqual(int(out[0]), 1)
        self.assertEqual(int(out[-1]), 1)

    def test_ignores_background_neighbours(self):
        h = np.array([0.0, 0.02, 0.04])
        theta = np.zeros(3)
        radius = np.array([2.76, 2.75, 2.80])
        pred = np.array([1, 1, 0])
        out = drop_proud_lining(h, theta, radius, pred, 0.10, 0.005)
        self.assertEqual(int(out[0]), 0)
        self.assertEqual(int(out[2]), 0)
