import unittest

import numpy as np

from rsi4tun.theta_wrap import crop_image_theta, paste_patch_theta, wrap_prompt_y


class ThetaWrapTests(unittest.TestCase):
    def test_default_clip_shortens_window_at_top(self):
        image = np.arange(60, dtype=np.uint8).reshape(20, 3)
        image = np.stack([image, image, image], axis=-1)
        cropped, centre, origin = crop_image_theta(image, cx=1, cy=2, crop_width=2, crop_height=10, wrap_theta=False)
        self.assertEqual(cropped.shape[0], 7)
        self.assertEqual(origin[1], 0)
        self.assertEqual(centre[1], 2)

    def test_wrap_keeps_full_height_and_matches_bottom_strip(self):
        image = np.arange(60, dtype=np.uint8).reshape(20, 3)
        image = np.stack([image, image, image], axis=-1)
        cropped, centre, origin = crop_image_theta(image, cx=1, cy=2, crop_width=2, crop_height=10, wrap_theta=True)
        self.assertEqual(cropped.shape, (10, 2, 3))
        self.assertEqual(origin[1], -3)
        top = cropped[:3, :, 0]
        bottom = image[-3:, 0:2, 0]
        np.testing.assert_array_equal(top, bottom)
        self.assertEqual(centre[1], 5)

    def test_wrap_prompt_y_keeps_points_inside_crop(self):
        points = np.array([[1.0, -2.0], [1.0, 12.0], [1.0, 3.0]])
        labels = np.array([1, 0, 1])
        wrapped, kept = wrap_prompt_y(points, labels, crop_height=10, wrap_theta=True)
        self.assertEqual(len(wrapped), 3)
        self.assertTrue(np.all(wrapped[:, 1] >= 0))
        self.assertTrue(np.all(wrapped[:, 1] < 10))
        clipped, kept_clip = wrap_prompt_y(points, labels, crop_height=10, wrap_theta=False)
        self.assertEqual(len(clipped), 1)
        self.assertEqual(int(kept_clip[0]), 1)

    def test_paste_wraps_onto_bottom_rows(self):
        logits_map = np.full((20, 5), -np.inf)
        label_map = np.zeros((20, 5), dtype=int)
        ring_map = np.zeros((20, 5), dtype=int)
        mask = np.ones((6, 3), dtype=bool)
        new_logits = np.full((6, 3), 1.0)
        paste_patch_theta(
            logits_map,
            label_map,
            ring_map,
            mask,
            new_logits,
            4,
            2,
            1,
            -3,
            wrap_theta=True,
        )
        self.assertTrue(np.all(label_map[17:20, 1:4] == 4))
        self.assertTrue(np.all(label_map[0:3, 1:4] == 4))
        self.assertTrue(np.all(ring_map[17:20, 1:4] == 2))


if __name__ == "__main__":
    unittest.main()
