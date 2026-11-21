# Sample tune measurements

Stage 6 wrote these scores. I copied each Mean IoU and each class IoU from that trial's `performance.md`. The printed values use three decimal places.

The scan is `data/scans/sample.txt`. The family is `sample`. The classes are background, K-block, B1-block, A1-block, A2-block, A3-block, and B2-block.

The pre-tune score is `data/development/sample/tune/baseline_before_tune_performance.md`.

The folder `data/development/sample/baseline` now matches `t22_denoise_mid`. I do not use that folder as the pre-tune control.

## Scores that moved

Before the tune, mean IoU was 0.880. K-block IoU was 0.784. Background IoU was 0.854.

I turned the K mirror on and left the other SAM settings unchanged (`t03_mirror_k`). Mean IoU was 0.894. K-block IoU was 0.876.

I set the template angle to −7.52 (`t02_angle_neg`). Mean IoU was 0.267. B1-block IoU was 0. A1-block IoU was 0. I set the same angle with the mirror on (`t04_angle_neg_mirror`). Mean IoU was 0.286. K-block IoU was 0.907.

I swapped the detecting oblique angle signs, with the mirror on (`t08_mirror_detect_swap`). Mean IoU was 0.859. K-block IoU was 0.811.

I set AB height to 3300, with the mirror on and K height 1100 (`t12_kh1100_ab3300`). Mean IoU was 0.839. A2-block IoU was 0.638. K-block IoU was 0.896.

I set AB height to 3200, with the mirror on and K height 1120 (`t20_ab3200`). Mean IoU was 0.881. A2-block IoU was 0.830.

I replaced detected prompts with ground-truth K medians and left the mirror off (`t01_oracle_gt`). Mean IoU was 0.876. K-block IoU was 0.781.

I used those ground-truth prompts with the mirror on and K height 1120 (`t15_oracle_mirror_kh1120`). Mean IoU was 0.890. The detector at that same geometry (`t09_kh_1120`) scored mean IoU 0.895.

The tight radial mask (`t21_denoise_tight`) scored mean IoU 0.845 and background IoU 0.859. A2-block IoU was 0.730.

The mid radial mask (`t22_denoise_mid`) scored mean IoU 0.896 and background IoU 0.849. K-block IoU was 0.890.

I turned off outlier interpolation in enhancing (`t23_enhance_no_outlier`). Mean IoU was 0.897. Background spill was 35,874 points against 35,856 on t22.

I set the depth-image window size to 3 (`t24_enhance_window3`). Mean IoU was 0.892. Background spill was 35,087.

I raised the denoise smoothing offset to +0.005 (`t25_denoise_offset_p005`). Mean IoU was 0.731. Background spill was 29,751. Every lining class fell by more than 0.02.

I scaled the SAM template to 0.97 on the t22 stages 1–4 (`t26_template_scale_097`). Mean IoU was 0.878. Background spill was 31,534. B1 spill was 7,752. B2 spill was 9,473. A2-block IoU was 0.837.

I replayed the t22 SAM masks with overlap abstention (`t27_overlap_abstain`). Mean IoU was 0.887. Background spill was 35,155. K-block IoU was 0.860.

I replayed the same masks with a logit margin of 1.0 (`t28_margin_abstain`). Mean IoU was 0.896. Background spill was 35,851.

I relabelled t22 lining points to background when their radius differed from the local median by more than 5 mm in either direction. Mean IoU was 0.899. Background spill was 28,193. The lining guard held.

I relabelled t22 lining points to background only when the radius stood more than 5 mm above that median, inside a 10 cm neighbourhood in `(h, θ)`. Mean IoU was 0.902. Background spill was 28,702. The class scores are background 0.863, K-block 0.897, B1-block 0.919, A1-block 0.937, A2-block 0.887, A3-block 0.898, and B2-block 0.911. The function is `drop_proud_lining`. The replay is not a new stage-1 to stage-5 run.

The remaining detect and SAM trials kept the mirror on. Their mean IoU stayed between 0.892 and 0.895. The class scores are in the table.

## Full record

| Trial | Mean IoU | Background | K-block | B1-block | A1-block | A2-block | A3-block | B2-block |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| pre-tune baseline | 0.880 | 0.854 | 0.784 | 0.907 | 0.936 | 0.887 | 0.899 | 0.893 |
| t01_oracle_gt | 0.876 | 0.851 | 0.781 | 0.903 | 0.931 | 0.882 | 0.895 | 0.891 |
| t02_angle_neg | 0.267 | 0.361 | 0.775 | 0.000 | 0.000 | 0.000 | 0.404 | 0.328 |
| t03_mirror_k | 0.894 | 0.849 | 0.876 | 0.914 | 0.935 | 0.887 | 0.899 | 0.901 |
| t04_angle_neg_mirror | 0.286 | 0.364 | 0.907 | 0.000 | 0.000 | 0.000 | 0.404 | 0.328 |
| t05_mirror_angle_8 | 0.894 | 0.848 | 0.878 | 0.913 | 0.934 | 0.886 | 0.897 | 0.899 |
| t06_mirror_angle_7 | 0.892 | 0.848 | 0.876 | 0.910 | 0.933 | 0.884 | 0.894 | 0.898 |
| t07_mirror_kheight | 0.895 | 0.847 | 0.880 | 0.913 | 0.936 | 0.890 | 0.899 | 0.901 |
| t08_mirror_detect_swap | 0.859 | 0.849 | 0.811 | 0.888 | 0.901 | 0.811 | 0.876 | 0.879 |
| t09_kh_1120 | 0.895 | 0.845 | 0.885 | 0.911 | 0.935 | 0.891 | 0.899 | 0.901 |
| t10_kh_1150 | 0.893 | 0.841 | 0.893 | 0.907 | 0.928 | 0.883 | 0.898 | 0.899 |
| t11_kh_1080 | 0.894 | 0.849 | 0.876 | 0.914 | 0.935 | 0.887 | 0.899 | 0.901 |
| t12_kh1100_ab3300 | 0.839 | 0.811 | 0.896 | 0.906 | 0.874 | 0.638 | 0.850 | 0.898 |
| t13_kh1100_width1250 | 0.895 | 0.846 | 0.880 | 0.912 | 0.936 | 0.891 | 0.898 | 0.900 |
| t14_kh1100_angle7_8 | 0.894 | 0.845 | 0.881 | 0.911 | 0.934 | 0.890 | 0.898 | 0.898 |
| t15_oracle_mirror_kh1120 | 0.890 | 0.843 | 0.874 | 0.907 | 0.931 | 0.886 | 0.894 | 0.897 |
| t16_pad200 | 0.895 | 0.845 | 0.884 | 0.912 | 0.935 | 0.893 | 0.897 | 0.898 |
| t17_crop30 | 0.895 | 0.843 | 0.884 | 0.910 | 0.935 | 0.892 | 0.900 | 0.901 |
| t18_taper500 | 0.894 | 0.842 | 0.887 | 0.909 | 0.931 | 0.892 | 0.898 | 0.900 |
| t19_ybounds | 0.895 | 0.844 | 0.884 | 0.911 | 0.935 | 0.891 | 0.899 | 0.900 |
| t20_ab3200 | 0.881 | 0.847 | 0.878 | 0.910 | 0.920 | 0.830 | 0.885 | 0.896 |
| t21_denoise_tight | 0.845 | 0.859 | 0.848 | 0.866 | 0.859 | 0.730 | 0.873 | 0.883 |
| t22_denoise_mid | 0.896 | 0.849 | 0.890 | 0.914 | 0.934 | 0.889 | 0.896 | 0.901 |
| t23_enhance_no_outlier | 0.897 | 0.848 | 0.890 | 0.912 | 0.933 | 0.894 | 0.901 | 0.902 |
| t24_enhance_window3 | 0.892 | 0.842 | 0.877 | 0.907 | 0.927 | 0.890 | 0.902 | 0.899 |
| t25_denoise_offset_p005 | 0.731 | 0.622 | 0.739 | 0.767 | 0.758 | 0.781 | 0.762 | 0.686 |
| t26_template_scale_097 | 0.878 | 0.816 | 0.902 | 0.908 | 0.904 | 0.837 | 0.887 | 0.892 |
| t27_overlap_abstain | 0.887 | 0.823 | 0.860 | 0.918 | 0.924 | 0.888 | 0.893 | 0.905 |
| t28_margin_abstain | 0.896 | 0.849 | 0.890 | 0.914 | 0.933 | 0.889 | 0.896 | 0.901 |
| t29_radius_abs_5mm | 0.899 | 0.860 | 0.897 | 0.919 | 0.932 | 0.878 | 0.899 | 0.909 |
| t30_proud_5mm | 0.902 | 0.863 | 0.897 | 0.919 | 0.937 | 0.887 | 0.898 | 0.911 |

## Background spill counts on full-pipeline arms

| Trial | Background spill | Change vs t22 |
| --- | ---: | ---: |
| t22_denoise_mid | 35,856 | control |
| t23_enhance_no_outlier | 35,874 | −0.05% |
| t24_enhance_window3 | 35,087 | −2.1% |
| t25_denoise_offset_p005 | 29,751 | −17.0% |
| t26_template_scale_097 | 31,534 | −12.1% |
| t27_overlap_abstain | 35,155 | −2.0% |
| t28_margin_abstain | 35,851 | −0.0% |
| t29_radius_abs_5mm | 28,193 | −21.4% |
| t30_proud_5mm | 28,702 | −20.0% |

## Background points labelled as lining

I joined `t22_denoise_mid/baseline/final.csv` in row order to column 4 of `data/scans/sample.txt`.

35,856 points have ground-truth label 0 and a predicted lining class.

Every one of those points has radius between 2.72 and 2.78. The median radius is 2.751.

The predicted counts are K-block 4,514, B1-block 9,377, A1-block 4,192, A2-block 504, A3-block 5,957, and B2-block 11,312.

I measured distance in chainage `h` and circumferential coordinate `θ`. The span of `θ` matches `2πr`, about 17.26 m, so I treat `θ` as metres along the ring. The median distance from these points to a ground-truth lining point is 0.014 m. The share within 0.05 m is 0.912.

## Record gaps

`results.jsonl` lists t01 through t20, then the full-pipeline arms t23 through t25. It lists `t02_angle_neg` twice, once as `oracle_gt` and once as `detect`. Both lines say mean IoU 0.267. The trial folder keeps one `performance.md`.

t21 and t22 are absent from `results.jsonl`. t26 is a SAM and evaluation rerun on the t22 copies. t27 and t28 replay `t22` `results.pkl` and change only the assignment. t29 and t30 replay the t22 point labels. They do not rerun stages 1 to 5.
