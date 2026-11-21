# 1-1 tune measurements

Stage 6 wrote these scores, except for the two proud replays. Those two rescore an existing cloud. I copied each mean IoU and each class IoU from that arm's `performance.md`. The printed values use three decimal places.

The scan is `data/scans/1-1.txt`. The family is `staggered`. The classes are background, K-block, B1-block, A1-block, A2-block, A3-block, and B2-block.

The episode baseline is `data/development/1-1/baseline`.

## Scores that moved

Before the tune, mean IoU was 0.785. K-block IoU was 0.716. A2-block IoU was 0.624.

I turned the K mirror on and left the other family settings unchanged (`a01_mirror_k`). Mean IoU was 0.796. K-block IoU was 0.797. Spill was 89,898.

I replayed that cloud with the 5 mm proud cut at 10 cm (`a02_proud_on_a01`). Mean IoU was 0.810. Spill was 59,628. The same cloud with a 3 mm residual (`a05_proud3_on_a01`) scored 0.778. B1-block and A1-block fell more than 0.02 below the baseline.

Template scale 1.03 with the mirror on (`a03_template_scale_103`) scored 0.774. A1-block and A2-block failed the lining guard. Template scale 0.97 with the mirror and the 5 mm cut (`a04_scale097_mirror_proud`) scored 0.800. The guard held. Mean IoU stayed below the 5 mm replay.

The mid radial mask 2.72–2.78, with the mirror and the 5 mm cut (`a06_mid_mask_mirror_proud`), scored 0.846. Spill was 37,536. K height 1120 on that stack (`a07_mid_mask_proud5_kh1120`) scored 0.848.

The next arms stayed on that stack and moved one local knob. Window size 7 (`a08`), outlier interpolation (`a09`), the wider mask 2.70–2.80 (`a10`), smoothing offset −0.005 (`a12`), and a 7 cm proud neighbourhood (`a13_a08_proud_radius_007`) scored 0.848, 0.848, 0.848, 0.847, and 0.849. Spill stayed between 37,226 and 38,772.

`a11_a08_proud_radius_015` set the proud neighbourhood to 15 cm and left the family mask at 2.32–2.79. Mean IoU was 0.811. Spill was 58,184.

`a13_a08_proud_radius_007` is the highest mean IoU in this tune: 0.849. The target was 0.9. The episode stopped there.

## Full record

| Trial | Mean IoU | Background | K-block | B1-block | A1-block | A2-block | A3-block | B2-block |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| episode baseline | 0.785 | 0.813 | 0.716 | 0.859 | 0.799 | 0.624 | 0.815 | 0.872 |
| a01_mirror_k | 0.796 | 0.803 | 0.797 | 0.863 | 0.790 | 0.622 | 0.815 | 0.879 |
| a02_proud_on_a01 | 0.810 | 0.838 | 0.807 | 0.872 | 0.799 | 0.636 | 0.826 | 0.892 |
| a03_template_scale_103 | 0.774 | 0.813 | 0.757 | 0.844 | 0.759 | 0.588 | 0.796 | 0.859 |
| a04_scale097_mirror_proud | 0.800 | 0.792 | 0.821 | 0.871 | 0.783 | 0.635 | 0.824 | 0.875 |
| a05_proud3_on_a01 | 0.778 | 0.784 | 0.773 | 0.837 | 0.775 | 0.619 | 0.800 | 0.859 |
| a06_mid_mask_mirror_proud | 0.846 | 0.887 | 0.849 | 0.871 | 0.829 | 0.718 | 0.867 | 0.901 |
| a07_mid_mask_proud5_kh1120 | 0.848 | 0.883 | 0.853 | 0.867 | 0.832 | 0.724 | 0.873 | 0.902 |
| a08_mid_mask_proud5_kh1120_ab3239_scale100 | 0.848 | 0.883 | 0.863 | 0.867 | 0.832 | 0.719 | 0.874 | 0.902 |
| a09_a08_outlier_interp | 0.848 | 0.882 | 0.861 | 0.868 | 0.833 | 0.716 | 0.872 | 0.901 |
| a10_a08_mask_wide_270_280 | 0.848 | 0.884 | 0.861 | 0.867 | 0.830 | 0.721 | 0.874 | 0.901 |
| a11_a08_proud_radius_015 | 0.811 | 0.827 | 0.816 | 0.879 | 0.796 | 0.635 | 0.833 | 0.888 |
| a12_a08_smoothing_offset_m005 | 0.847 | 0.883 | 0.862 | 0.866 | 0.827 | 0.716 | 0.871 | 0.902 |
| a13_a08_proud_radius_007 | 0.849 | 0.884 | 0.858 | 0.868 | 0.830 | 0.725 | 0.874 | 0.902 |
