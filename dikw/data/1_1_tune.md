# 1-1 tune measurements

Best mean IoU so far: **0.891** on `a43_ring2_shift_proud_r10_6mm`. The 0.9 target was not reached. Config chase stopped.

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

`a13_a08_proud_radius_007` is still the highest mean IoU: 0.849.

On the a13 stack, AB height 3100 (`a14_ab3100`) scored 0.804 and A2-block IoU 0.598. AB height 3400 (`a15_ab3400`) scored 0.748 and A2-block IoU 0.371. Both sealed calls failed. Both lining guards versus a13 failed.

Angle 8.5 (`a16_angle_850`) scored 0.848. Angle 6.5 (`a17_angle_650`) scored 0.850 and is the new best. Both sealed calls for mean IoU ≥ 0.860 failed. Both lining guards held.

On the a17 stack, segment width 1100 (`a18_width_1100`) scored 0.848. Width 1300 (`a19_width_1300`) scored 0.847. Both sealed calls failed. Both lining guards held.

B1 template height 1519.89 (`a20_b1_height_1519`) scored 0.849. The sealed call failed. The lining guard held. Best arm remains `a17_angle_650` at 0.850.

Exploratory A2 push after a20: assignment A2-over-A1 (`a23`) stayed at 0.850 with A2 0.726. `reverse_circumferential` (`a24`) and multimask (`a28`) stayed at 0.850. A1 template 0.90 (`a25`) scored 0.832 and broke A1. A2 template 1.10 (`a26`) scored 0.841 and dropped A2 to 0.674. Swapping the A1/A2 walk (`a27`) scored 0.632. Padding 250 (`a30`) scored 0.848. No template mask (`a31`) scored 0.782. Extra ring segment (`a32`) scored 0.849. A1 wrap negatives (`a33`) scored 0.786 with A2 0.348.

Ring-2 cyclic label shift +1 (`a34_ring2_label_shift` replay) scored 0.890 with A2 0.805. Full runs with `ring_label_shifts={"2":1}` scored 0.888 (`a36`, `a37`). `min_forward_blocks` 4 (`a35`) scored 0.805 with A2 0.448. Five proud replays on a34 (`a38`–`a42`) stayed at 0.882–0.890; none reached 0.9. Best proud tie was 0.10 m / 6 mm (`a41`). Full lock of ring-2 shift plus that proud (`a43`) scored 0.891 with A2 0.802. Sealed call for 0.9 failed. Config chase stopped.

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
| a14_ab3100 | 0.804 | 0.895 | 0.821 | 0.859 | 0.778 | 0.598 | 0.784 | 0.891 |
| a15_ab3400 | 0.748 | 0.817 | 0.878 | 0.833 | 0.691 | 0.371 | 0.765 | 0.883 |
| a16_angle_850 | 0.848 | 0.883 | 0.856 | 0.867 | 0.832 | 0.720 | 0.872 | 0.902 |
| a17_angle_650 | 0.850 | 0.884 | 0.862 | 0.868 | 0.831 | 0.727 | 0.874 | 0.902 |
| a18_width_1100 | 0.848 | 0.887 | 0.854 | 0.868 | 0.828 | 0.724 | 0.874 | 0.903 |
| a19_width_1300 | 0.847 | 0.884 | 0.860 | 0.866 | 0.830 | 0.718 | 0.872 | 0.902 |
| a20_b1_height_1519 | 0.849 | 0.884 | 0.856 | 0.867 | 0.830 | 0.727 | 0.876 | 0.902 |
| a23_a2_over_a1_on_a17 | 0.850 | 0.884 | 0.862 | 0.868 | 0.832 | 0.726 | 0.874 | 0.902 |
| a24_reverse_circ | 0.850 | 0.887 | 0.863 | 0.869 | 0.831 | 0.722 | 0.874 | 0.904 |
| a25_a1_scale_090 | 0.832 | 0.854 | 0.860 | 0.868 | 0.742 | 0.724 | 0.874 | 0.903 |
| a26_a2_scale_110 | 0.841 | 0.882 | 0.862 | 0.867 | 0.828 | 0.674 | 0.868 | 0.903 |
| a27_swap_a1_a2_walk | 0.632 | 0.885 | 0.862 | 0.868 | 0.002 | 0.028 | 0.874 | 0.902 |
| a28_multimask | 0.850 | 0.888 | 0.864 | 0.867 | 0.827 | 0.726 | 0.873 | 0.904 |
| a29_a1_over_b1_on_a17 | 0.849 | 0.884 | 0.862 | 0.868 | 0.830 | 0.727 | 0.874 | 0.902 |
| a30_padding_250 | 0.848 | 0.886 | 0.862 | 0.867 | 0.827 | 0.720 | 0.874 | 0.903 |
| a31_no_template_mask | 0.782 | 0.804 | 0.774 | 0.846 | 0.765 | 0.622 | 0.790 | 0.870 |
| a32_extra_ring_1 | 0.849 | 0.883 | 0.863 | 0.868 | 0.831 | 0.723 | 0.874 | 0.903 |
| a33_a1_wrap_negatives | 0.786 | 0.838 | 0.856 | 0.869 | 0.828 | 0.348 | 0.861 | 0.901 |
| a34_ring2_label_shift | 0.890 | 0.884 | 0.866 | 0.913 | 0.922 | 0.805 | 0.903 | 0.935 |
| a35_min_forward_4 | 0.805 | 0.854 | 0.860 | 0.868 | 0.830 | 0.448 | 0.872 | 0.902 |
| a36_ring2_shift | 0.888 | 0.883 | 0.865 | 0.912 | 0.920 | 0.797 | 0.902 | 0.935 |
| a37_ring2_shift_after_proud | 0.888 | 0.884 | 0.867 | 0.914 | 0.921 | 0.793 | 0.903 | 0.937 |
| a38_a34_proud_r10_5mm | 0.889 | 0.883 | 0.866 | 0.911 | 0.921 | 0.804 | 0.902 | 0.934 |
| a39_a34_proud_r15_5mm | 0.887 | 0.879 | 0.863 | 0.907 | 0.921 | 0.802 | 0.901 | 0.933 |
| a40_a34_proud_r20_5mm | 0.884 | 0.873 | 0.859 | 0.902 | 0.920 | 0.799 | 0.901 | 0.932 |
| a41_a34_proud_r10_6mm | 0.890 | 0.885 | 0.867 | 0.913 | 0.922 | 0.805 | 0.903 | 0.935 |
| a42_a34_proud_r07_4mm | 0.882 | 0.870 | 0.859 | 0.904 | 0.916 | 0.802 | 0.897 | 0.925 |
| a43_ring2_shift_proud_r10_6mm | 0.891 | 0.888 | 0.870 | 0.915 | 0.924 | 0.802 | 0.903 | 0.939 |
