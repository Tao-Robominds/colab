# Tune artifact differences

Status: provisional. Prediction-artifact differences between each tune arm and its comparison arm.

Comparison arm is the named parent when the arm name, `source`, `source_arm`, `source_stack`, or a sealed Control line names one. Otherwise it is the previous number.

Aligned: same point rows. Counts of predicted-label changes, rings, intensity, radius, and theta on the changed points.
Unaligned: different clouds. Class counts and ring counts only.

`t29` and `t30` have no arm directory. Their proud facts stay in `sample_orientation_and_bg_ceiling.md`.

## Scan sample

### t01_oracle_gt

Comparison: `(none)`. Mean IoU 0.876.

First arm. Class counts: {'Bg': 325976, 'K': 82538, 'B1': 222544, 'A1': 137677, 'A2': 29696, 'A3': 103398, 'B2': 207939}. Rings: {0: 305135, 1: 23968, 2: 12876, 3: 17102, 4: 22610, 5: 31251, 6: 43307, 7: 65878, 8: 103588, 9: 173713}.

### t02_angle_neg

Comparison: `t01_oracle_gt`. Mean IoU 0.267.

Aligned cloud, 1109768 points. Predicted label changed on 588429 points.
Top transitions: B1->Bg 221215, A1->Bg 137637, B2->Bg 135419, A3->Bg 57357, A2->Bg 29437, Bg->K 2490, B1->K 1241, K->Bg 1082, B2->K 642, B2->A3 453, A3->B2 433, Bg->B2 351.
Changed points by pred_ring: 1:582976, 0:1942, 9:1362, 8:750, 7:407, 5:290, 6:240, 3:180.
Changed r min/p50/max 2.7267/2.7501/2.7936.
Changed theta min/p50/max 1.989/7.677/15.310.
Changed intensity min/p50/max -1726/-1224/1899.
To background: 582147 (r p50 2.7501, intensity p50 -1224).
On pred_ring 2: 120 changed; theta 9.170–15.219 (p50 10.139).
Ring-2 transitions: A3->B2 42, B1->K 26, Bg->K 24, A2->A3 15, B2->K 12, Bg->B2 1.

### t03_mirror_k

Comparison: `t02_angle_neg`. Mean IoU 0.894.

Aligned cloud, 1109768 points. Predicted label changed on 594871 points.
Top transitions: Bg->B1 221247, Bg->A1 137081, Bg->B2 135021, Bg->A3 57397, Bg->A2 29954, K->Bg 7378, Bg->K 3586, K->B1 701, K->B2 596, B2->A3 447, A3->B2 442, B2->Bg 373.
Changed points by pred_ring: 0:239260, 9:119053, 8:81146, 7:44637, 6:33732, 5:20932, 4:19997, 1:14636.
Changed r min/p50/max 2.7267/2.7501/2.7936.
Changed theta min/p50/max 1.988/7.707/15.310.
Changed intensity min/p50/max -1726/-1224/1899.
To background: 7912 (r p50 2.7576, intensity p50 -1169).
On pred_ring 2: 10094 changed; theta 2.063–15.160 (p50 7.673).
Ring-2 transitions: Bg->B1 4212, Bg->A1 2647, Bg->B2 2181, Bg->A3 544, Bg->A2 356, Bg->K 48, A3->B2 41, K->B1 37.

### t04_angle_neg_mirror

Comparison: `t03_mirror_k`. Mean IoU 0.286.

Aligned cloud, 1109768 points. Predicted label changed on 584891 points.
Top transitions: B1->Bg 220240, A1->Bg 137060, B2->Bg 133915, A3->Bg 57398, A2->Bg 29954, B1->K 1709, B2->K 1708, K->Bg 496, Bg->K 481, A3->B2 447, B2->A3 442, Bg->B2 376.
Changed points by pred_ring: 1:579141, 0:1720, 9:1299, 8:955, 7:564, 6:351, 5:319, 3:267.
Changed r min/p50/max 2.7267/2.7500/2.7933.
Changed theta min/p50/max 1.988/7.651/15.310.
Changed intensity min/p50/max -1726/-1224/1899.
To background: 579063 (r p50 2.7500, intensity p50 -1226).
On pred_ring 2: 151 changed; theta 9.176–15.219 (p50 10.312).
Ring-2 transitions: A3->B2 48, B2->K 46, B1->K 24, A2->A3 19, Bg->K 12, Bg->B2 2.

### t05_mirror_angle_8

Comparison: `t04_angle_neg_mirror`. Mean IoU 0.894.

Aligned cloud, 1109768 points. Predicted label changed on 585299 points.
Top transitions: Bg->B1 220800, Bg->A1 136970, Bg->B2 133937, Bg->A3 57491, Bg->A2 29897, K->B2 1722, K->B1 1682, B2->A3 493, Bg->K 487, A3->B2 401, K->Bg 389, B2->Bg 371.
Changed points by pred_ring: 0:238065, 9:118659, 8:80695, 7:44576, 6:33586, 5:20844, 4:19925, 3:11284.

### t06_mirror_angle_7

Comparison: `t05_mirror_angle_8`. Mean IoU 0.892.

Aligned cloud, 1109768 points. Predicted label changed on 10856 points.
Top transitions: K->B1 1033, K->B2 1032, B2->K 940, B1->K 861, Bg->B1 799, Bg->B2 677, B2->Bg 580, B1->Bg 533, A3->B2 531, B2->A3 526, A1->B1 460, B1->A1 455.
Changed points by pred_ring: 0:2562, 9:2198, 1:1735, 8:1358, 7:784, 5:570, 6:561, 4:469.

### t07_mirror_kheight

Comparison: `t06_mirror_angle_7`. Mean IoU 0.895.

Aligned cloud, 1109768 points. Predicted label changed on 12172 points.
Top transitions: B1->Bg 1312, B2->K 1080, B2->Bg 1030, B1->K 975, K->B1 779, K->B2 750, Bg->B2 683, A3->B2 664, A1->B1 569, B2->A3 518, B1->A1 475, Bg->B1 473.
Changed points by pred_ring: 1:3507, 0:2827, 9:1876, 8:1193, 7:756, 5:513, 6:479, 4:441.

### t08_mirror_detect_swap

Comparison: `t07_mirror_kheight`. Mean IoU 0.859.

Aligned cloud, 1109768 points. Predicted label changed on 25709 points.
Top transitions: K->B2 4562, A1->B1 3895, B1->K 3650, B2->A3 1916, A3->A2 1652, A2->A1 1448, Bg->B2 1083, Bg->B1 894, K->B1 894, B1->Bg 789, B2->K 731, B2->Bg 675.
Changed points by pred_ring: 4:8549, 3:7029, 0:2851, 1:2106, 9:1862, 8:1204, 7:735, 5:552.

### t09_kh_1120

Comparison: `t08_mirror_detect_swap`. Mean IoU 0.895.

Aligned cloud, 1109768 points. Predicted label changed on 28253 points.
Top transitions: B2->K 4688, B1->A1 3908, K->B1 3541, A3->B2 2083, B2->Bg 1689, A2->A3 1643, B1->Bg 1498, A1->A2 1436, B1->K 1012, Bg->B1 886, Bg->B2 817, A1->B1 707.
Changed points by pred_ring: 4:8256, 3:6844, 1:4868, 0:2894, 9:1938, 8:1373, 7:762, 5:536.

### t10_kh_1150

Comparison: `t09_kh_1120`. Mean IoU 0.893.

Aligned cloud, 1109768 points. Predicted label changed on 12618 points.
Top transitions: B1->Bg 1185, B2->Bg 1106, A1->B1 1000, Bg->B1 949, B1->K 879, Bg->A1 864, B2->K 833, Bg->B2 769, K->B2 577, K->B1 519, A3->B2 444, A3->Bg 409.
Changed points by pred_ring: 1:3593, 0:3419, 9:1846, 8:1192, 7:600, 6:493, 5:452, 4:441.

### t11_kh_1080

Comparison: `t10_kh_1150`. Mean IoU 0.894.

Aligned cloud, 1109768 points. Predicted label changed on 16761 points.
Top transitions: Bg->B1 2043, Bg->B2 1942, B1->A1 1614, K->B2 1301, K->B1 1202, B1->Bg 991, B2->Bg 937, A1->A2 752, B2->A3 723, Bg->A3 598, A1->Bg 565, B1->K 564.
Changed points by pred_ring: 0:4738, 1:3073, 9:3054, 8:1835, 7:1153, 6:774, 5:684, 4:625.

### t12_kh1100_ab3300

Comparison: `t11_kh_1080`. Mean IoU 0.839.

Aligned cloud, 1109768 points. Predicted label changed on 36782 points.
Top transitions: A1->Bg 5176, A3->Bg 4405, A2->Bg 4229, A2->A1 3720, B1->Bg 3069, B2->Bg 3032, A1->B1 1571, Bg->B1 1447, B2->K 1370, B1->K 1309, A2->A3 1194, A3->B2 893.
Changed points by pred_ring: 1:20418, 0:6877, 9:3084, 8:2086, 4:1070, 7:880, 6:829, 5:643.

### t13_kh1100_width1250

Comparison: `t12_kh1100_ab3300`. Mean IoU 0.895.

Aligned cloud, 1109768 points. Predicted label changed on 33544 points.
Top transitions: Bg->A1 5182, Bg->A3 4346, Bg->A2 4230, A1->A2 3403, Bg->B1 2495, Bg->B2 2301, B1->A1 1260, K->B2 1130, A3->A2 1124, K->B1 1091, A1->Bg 960, B2->A3 934.
Changed points by pred_ring: 0:10882, 9:6952, 8:4301, 1:3774, 7:2060, 6:1781, 4:1362, 5:1160.

### t14_kh1100_angle7_8

Comparison: `t13_kh1100_width1250`. Mean IoU 0.894.

Aligned cloud, 1109768 points. Predicted label changed on 11338 points.
Top transitions: Bg->B2 1241, Bg->B1 932, K->B1 899, K->B2 849, B2->K 812, B1->Bg 784, B1->K 783, A3->B2 485, B2->Bg 485, A1->B1 476, K->Bg 460, B2->A3 447.
Changed points by pred_ring: 0:2700, 1:2247, 9:2218, 8:1304, 7:767, 5:541, 6:518, 4:467.

### t15_oracle_mirror_kh1120

Comparison: `t14_kh1100_angle7_8`. Mean IoU 0.890.

Aligned cloud, 1109768 points. Predicted label changed on 16311 points.
Top transitions: B1->Bg 2537, B2->K 1472, B2->Bg 1206, K->B1 1029, B1->K 929, Bg->B1 809, A3->B2 795, B1->A1 790, Bg->K 765, A1->B1 699, K->B2 681, K->Bg 646.
Changed points by pred_ring: 1:6791, 0:3188, 9:2247, 8:1173, 4:606, 7:605, 5:595, 6:456.

### t16_pad200

Comparison: `t15_oracle_mirror_kh1120`. Mean IoU 0.895.

Aligned cloud, 1109768 points. Predicted label changed on 17863 points.
Top transitions: Bg->B1 2383, B1->Bg 1642, B2->Bg 1601, K->B2 1322, B1->K 1046, Bg->B2 1021, Bg->K 801, K->B1 801, B2->A3 791, A1->B1 748, K->Bg 709, B2->K 706.
Changed points by pred_ring: 1:7424, 0:3533, 9:2650, 8:1036, 7:721, 4:698, 5:634, 6:440.

### t17_crop30

Comparison: `t16_pad200`. Mean IoU 0.895.

Aligned cloud, 1109768 points. Predicted label changed on 13390 points.
Top transitions: Bg->B1 1652, Bg->B2 1523, Bg->A1 1031, B1->Bg 849, B2->K 782, B2->Bg 760, B1->K 737, K->B1 725, K->B2 682, A3->B2 587, B2->A3 439, K->Bg 429.
Changed points by pred_ring: 0:3673, 9:2594, 1:2564, 8:1436, 7:860, 5:573, 6:559, 4:522.

### t18_taper500

Comparison: `t17_crop30`. Mean IoU 0.894.

Aligned cloud, 1109768 points. Predicted label changed on 8286 points.
Top transitions: Bg->B1 798, B2->K 717, B1->K 690, K->B2 611, K->B1 595, B2->Bg 507, B2->A3 498, A1->B1 398, Bg->B2 397, A3->B2 359, B1->A1 335, B1->Bg 311.
Changed points by pred_ring: 0:2112, 9:1549, 1:1335, 8:1022, 7:601, 6:404, 5:396, 4:377.

### t19_ybounds

Comparison: `t18_taper500`. Mean IoU 0.895.

Aligned cloud, 1109768 points. Predicted label changed on 12269 points.
Top transitions: B1->Bg 1800, B2->Bg 1013, Bg->B2 862, A1->Bg 833, K->B2 798, K->B1 751, B1->K 683, Bg->B1 647, B2->K 620, B2->A3 497, A3->B2 462, A1->B1 443.
Changed points by pred_ring: 1:4278, 0:2385, 9:1734, 8:1208, 7:653, 5:532, 6:454, 4:444.

### t20_ab3200

Comparison: `t19_ybounds`. Mean IoU 0.881.

Aligned cloud, 1109768 points. Predicted label changed on 15452 points.
Top transitions: A1->A2 2138, Bg->B1 1561, B2->A3 1524, Bg->B2 1347, B1->A1 1223, Bg->A3 799, K->B2 778, K->B1 727, Bg->A1 703, A3->A2 568, B2->K 525, B2->Bg 468.
Changed points by pred_ring: 0:5423, 9:3125, 8:1887, 1:1211, 7:1038, 6:741, 4:683, 5:620.

### t21_denoise_tight

Comparison: `t20_ab3200`. Mean IoU 0.845.

Unaligned clouds (1109768 → 1109768 points).
Class counts prev: Bg 327015, K 80953, B1 221968, A1 136234, A2 32316, A3 104654, B2 206628.
Class counts curr: Bg 344430, K 80262, B1 218234, A1 133037, A2 25286, A3 102131, B2 206388.
Class delta: Bg +17415, K -691, B1 -3734, A1 -3197, A2 -7030, A3 -2523, B2 -240.
Ring counts prev: {0: 304770, 1: 26624, 2: 12674, 3: 16897, 4: 22588, 5: 30952, 6: 42957, 7: 65624, 8: 102746, 9: 173596}.
Ring counts curr: {0: 295904, 1: 23032, 2: 12517, 3: 16651, 4: 22200, 5: 30281, 6: 42127, 7: 64555, 8: 101147, 9: 170240}.

### t22_denoise_mid

Comparison: `t21_denoise_tight`. Mean IoU 0.896.

Unaligned clouds (1109768 → 1109768 points).
Class counts prev: Bg 344430, K 80262, B1 218234, A1 133037, A2 25286, A3 102131, B2 206388.
Class counts curr: Bg 331882, K 81401, B1 220918, A1 136809, A2 29851, A3 103267, B2 205640.
Class delta: Bg -12548, K +1139, B1 +2684, A1 +3772, A2 +4565, A3 +1136, B2 -748.
Ring counts prev: {0: 295904, 1: 23032, 2: 12517, 3: 16651, 4: 22200, 5: 30281, 6: 42127, 7: 64555, 8: 101147, 9: 170240}.
Ring counts curr: {0: 302126, 1: 28806, 2: 12646, 3: 16822, 4: 22404, 5: 30745, 6: 42860, 7: 65241, 8: 102485, 9: 172672}.

### t23_enhance_no_outlier

Comparison: `t22_denoise_mid`. Mean IoU 0.897.

Unaligned clouds (1109768 → 1109768 points).
Class counts prev: Bg 331882, K 81401, B1 220918, A1 136809, A2 29851, A3 103267, B2 205640.
Class counts curr: Bg 332286, K 81474, B1 221420, A1 136461, A2 29518, A3 102893, B2 205716.
Class delta: Bg +404, K +73, B1 +502, A1 -348, A2 -333, A3 -374, B2 +76.
Ring counts prev: {0: 302126, 1: 28806, 2: 12646, 3: 16822, 4: 22404, 5: 30745, 6: 42860, 7: 65241, 8: 102485, 9: 172672}.
Ring counts curr: {0: 302059, 1: 27781, 2: 12647, 3: 16807, 4: 22422, 5: 30702, 6: 42825, 7: 65216, 8: 102606, 9: 172629}.

### t24_enhance_window3

Comparison: `t23_enhance_no_outlier`. Mean IoU 0.892.

Unaligned clouds (1109768 → 1109768 points).
Class counts prev: Bg 332286, K 81474, B1 221420, A1 136461, A2 29518, A3 102893, B2 205716.
Class counts curr: Bg 336666, K 80920, B1 219501, A1 136002, A2 29546, A3 102496, B2 204637.
Class delta: Bg +4380, K -554, B1 -1919, A1 -459, A2 +28, A3 -397, B2 -1079.
Ring counts prev: {0: 302059, 1: 27781, 2: 12647, 3: 16807, 4: 22422, 5: 30702, 6: 42825, 7: 65216, 8: 102606, 9: 172629}.
Ring counts curr: {0: 303269, 1: 32585, 2: 11403, 3: 15705, 4: 21389, 5: 29411, 6: 42421, 7: 65336, 8: 102478, 9: 172489}.

### t25_denoise_offset_p005

Comparison: `t24_enhance_window3`. Mean IoU 0.731.

Unaligned clouds (1109768 → 1109768 points).
Class counts prev: Bg 336666, K 80920, B1 219501, A1 136002, A2 29546, A3 102496, B2 204637.
Class counts curr: Bg 481863, K 67350, B1 184530, A1 110090, A2 25356, A3 84321, B2 156258.
Class delta: Bg +145197, K -13570, B1 -34971, A1 -25912, A2 -4190, A3 -18175, B2 -48379.
Ring counts prev: {0: 303269, 1: 32585, 2: 11403, 3: 15705, 4: 21389, 5: 29411, 6: 42421, 7: 65336, 8: 102478, 9: 172489}.
Ring counts curr: {0: 276990, 1: 22665, 2: 4869, 3: 5661, 4: 10822, 5: 12659, 6: 23295, 7: 50668, 8: 82333, 9: 155749}.

### t26_template_scale_097

Comparison: `t22_denoise_mid`. Mean IoU 0.878.

Aligned cloud, 1109768 points. Predicted label changed on 28747 points.
Top transitions: B2->Bg 6999, B1->Bg 6439, A1->Bg 5432, A3->Bg 2312, A2->Bg 2066, K->Bg 992, B1->K 926, B2->K 921, A3->B2 453, K->B2 308, B2->A3 283, K->B1 273.
Changed points by pred_ring: 1:24307, 0:1489, 9:1047, 8:570, 4:315, 7:314, 3:191, 6:185.
Changed r min/p50/max 2.7260/2.7499/2.7765.
Changed theta min/p50/max 1.991/8.253/15.255.
Changed intensity min/p50/max -1722/-1214/-126.
To background: 24240 (r p50 2.7501, intensity p50 -1218).
On pred_ring 2: 153 changed; theta 2.508–15.187 (p50 10.045).
Ring-2 transitions: A3->B2 45, B1->A1 25, B2->K 22, K->B1 18, B1->K 14, A2->A3 8, A1->A2 6, B2->B1 6.

### t27_overlap_abstain

Comparison: `t22_denoise_mid`. Mean IoU 0.887.

Aligned cloud, 1109768 points. Predicted label changed on 13051 points.
Top transitions: K->Bg 2878, B2->Bg 2569, B1->Bg 2480, A1->Bg 2268, A3->Bg 2104, A2->Bg 752.
Changed points by pred_ring: 1:13051.
Changed r min/p50/max 2.7295/2.7489/2.7637.
Changed theta min/p50/max 2.006/9.204/15.280.
Changed intensity min/p50/max -1722/-1218/-671.
To background: 13051 (r p50 2.7489, intensity p50 -1218).

### t28_margin_abstain

Comparison: `t22_denoise_mid`. Mean IoU 0.896.

Aligned cloud, 1109768 points. Predicted label changed on 86 points.
Top transitions: K->Bg 41, A1->Bg 17, A3->Bg 11, B1->Bg 7, B2->Bg 7, A2->Bg 3.
Changed points by pred_ring: 1:86.
Changed r min/p50/max 2.7417/2.7494/2.7585.
Changed theta min/p50/max 2.146/9.188/15.213.
Changed intensity min/p50/max -1627/-1219/-1002.
To background: 86 (r p50 2.7494, intensity p50 -1219).

## Scan 1-1

### a01_mirror_k

Comparison: `(none)`. Mean IoU 0.796.

First arm. Class counts: {'Bg': 531229, 'K': 144945, 'B1': 352737, 'A1': 207376, 'A2': 96584, 'A3': 184426, 'B2': 410889}. Rings: {0: 22332, 1: 74451, 2: 39006, 3: 93161, 4: 200816, 5: 426953, 6: 319312, 7: 156319, 8: 76226, 9: 39512}.

### a02_proud_on_a01

Comparison: `a01_mirror_k`. Mean IoU 0.810.

Aligned cloud, 1928186 points. Predicted label changed on 40735 points.
Top transitions: B2->Bg 12642, B1->Bg 9387, A3->Bg 5355, A1->Bg 5121, K->Bg 4555, A2->Bg 3675.
Changed points by pred_ring: 5:14378, 6:7809, 4:6274, 3:3628, 7:3333, 2:1924, 8:1519, 1:897.
Changed r min/p50/max 2.4750/2.7631/2.7899.
Changed theta min/p50/max 1.584/8.610/15.756.
To background: 40735 (r p50 2.7631).
On pred_ring 2: 1924 changed; theta 1.682–15.457 (p50 8.999).
Ring-2 transitions: B2->Bg 551, B1->Bg 545, K->Bg 373, A1->Bg 248, A3->Bg 124, A2->Bg 83.

### a03_template_scale_103

Comparison: `a02_proud_on_a01`. Mean IoU 0.774.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 571964, K 140390, B1 343350, A1 202255, A2 92909, A3 179071, B2 398247.
Class counts curr: Bg 513407, K 141844, B1 362449, A1 208480, A2 97554, A3 184364, B2 420088.
Class delta: Bg -58557, K +1454, B1 +19099, A1 +6225, A2 +4645, A3 +5293, B2 +21841.
Ring counts prev: {0: 22332, 1: 74451, 2: 39006, 3: 93161, 4: 200816, 5: 426953, 6: 319312, 7: 156319, 8: 76226, 9: 39512}.
Ring counts curr: {0: 22319, 1: 57723, 2: 40565, 3: 94080, 4: 201880, 5: 430699, 6: 326474, 7: 157761, 8: 77095, 9: 39534}.

### a04_scale097_mirror_proud

Comparison: `a03_template_scale_103`. Mean IoU 0.800.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 513407, K 141844, B1 362449, A1 208480, A2 97554, A3 184364, B2 420088.
Class counts curr: Bg 620717, K 141383, B1 325275, A1 195700, A2 88393, A3 173879, B2 382839.
Class delta: Bg +107310, K -461, B1 -37174, A1 -12780, A2 -9161, A3 -10485, B2 -37249.
Ring counts prev: {0: 22319, 1: 57723, 2: 40565, 3: 94080, 4: 201880, 5: 430699, 6: 326474, 7: 157761, 8: 77095, 9: 39534}.
Ring counts curr: {0: 21573, 1: 127014, 2: 31578, 3: 88610, 4: 192605, 5: 414425, 6: 306827, 7: 151063, 8: 73571, 9: 38294}.

### a05_proud3_on_a01

Comparison: `a01_mirror_k`. Mean IoU 0.778.

Aligned cloud, 1928186 points. Predicted label changed on 100524 points.
Top transitions: B2->Bg 29582, B1->Bg 24739, A1->Bg 13120, A3->Bg 12894, K->Bg 11434, A2->Bg 8755.
Changed points by pred_ring: 5:36557, 6:24739, 4:14310, 7:9254, 3:6171, 8:3432, 2:2769, 9:1342.
Changed r min/p50/max 2.4729/2.7591/2.7899.
Changed theta min/p50/max 1.584/8.595/15.756.
To background: 100524 (r p50 2.7591).
On pred_ring 2: 2769 changed; theta 1.676–15.457 (p50 9.011).
Ring-2 transitions: B2->Bg 735, B1->Bg 723, K->Bg 486, A1->Bg 392, A3->Bg 273, A2->Bg 160.

### a06_mid_mask_mirror_proud

Comparison: `a05_proud3_on_a01`. Mean IoU 0.846.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 631753, K 133511, B1 327998, A1 194256, A2 87829, A3 171532, B2 381307.
Class counts curr: Bg 583821, K 142555, B1 349918, A1 196433, A2 81425, A3 174699, B2 399335.
Class delta: Bg -47932, K +9044, B1 +21920, A1 +2177, A2 -6404, A3 +3167, B2 +18028.
Ring counts prev: {0: 22332, 1: 74451, 2: 39006, 3: 93161, 4: 200816, 5: 426953, 6: 319312, 7: 156319, 8: 76226, 9: 39512}.
Ring counts curr: {0: 21921, 1: 59032, 2: 46619, 3: 92784, 4: 195235, 5: 422583, 6: 310709, 7: 152166, 8: 74280, 9: 39010}.

### a07_mid_mask_proud5_kh1120

Comparison: `a06_mid_mask_mirror_proud`. Mean IoU 0.848.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 583821, K 142555, B1 349918, A1 196433, A2 81425, A3 174699, B2 399335.
Class counts curr: Bg 588168, K 143224, B1 348927, A1 194744, A2 80390, A3 174294, B2 398439.
Class delta: Bg +4347, K +669, B1 -991, A1 -1689, A2 -1035, A3 -405, B2 -896.
Ring counts prev: {0: 21921, 1: 59032, 2: 46619, 3: 92784, 4: 195235, 5: 422583, 6: 310709, 7: 152166, 8: 74280, 9: 39010}.
Ring counts curr: {0: 21854, 1: 62432, 2: 46070, 3: 93088, 4: 195442, 5: 422261, 6: 309371, 7: 151842, 8: 74037, 9: 38895}.

### a08_mid_mask_proud5_kh1120_ab3239_scale100

Comparison: `a07_mid_mask_proud5_kh1120`. Mean IoU 0.848.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 588168, K 143224, B1 348927, A1 194744, A2 80390, A3 174294, B2 398439.
Class counts curr: Bg 586619, K 145196, B1 348607, A1 195286, A2 81106, A3 174013, B2 397359.
Class delta: Bg -1549, K +1972, B1 -320, A1 +542, A2 +716, A3 -281, B2 -1080.
Ring counts prev: {0: 21854, 1: 62432, 2: 46070, 3: 93088, 4: 195442, 5: 422261, 6: 309371, 7: 151842, 8: 74037, 9: 38895}.
Ring counts curr: {0: 21835, 1: 61818, 2: 46010, 3: 93053, 4: 194827, 5: 422563, 6: 310233, 7: 151345, 8: 74339, 9: 38929}.

### a09_a08_outlier_interp

Comparison: `a08_mid_mask_proud5_kh1120_ab3239_scale100`. Mean IoU 0.848.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 586619, K 145196, B1 348607, A1 195286, A2 81106, A3 174013, B2 397359.
Class counts curr: Bg 586717, K 144511, B1 348407, A1 194764, A2 81479, A3 174540, B2 397768.
Class delta: Bg +98, K -685, B1 -200, A1 -522, A2 +373, A3 +527, B2 +409.
Ring counts prev: {0: 21835, 1: 61818, 2: 46010, 3: 93053, 4: 194827, 5: 422563, 6: 310233, 7: 151345, 8: 74339, 9: 38929}.
Ring counts curr: {0: 21829, 1: 63374, 2: 45961, 3: 92734, 4: 195151, 5: 422378, 6: 310543, 7: 151491, 8: 74002, 9: 38923}.

### a10_a08_mask_wide_270_280

Comparison: `a08_mid_mask_proud5_kh1120_ab3239_scale100`. Mean IoU 0.848.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 586619, K 145196, B1 348607, A1 195286, A2 81106, A3 174013, B2 397359.
Class counts curr: Bg 586891, K 145015, B1 349254, A1 195495, A2 80709, A3 173767, B2 397055.
Class delta: Bg +272, K -181, B1 +647, A1 +209, A2 -397, A3 -246, B2 -304.
Ring counts prev: {0: 21835, 1: 61818, 2: 46010, 3: 93053, 4: 194827, 5: 422563, 6: 310233, 7: 151345, 8: 74339, 9: 38929}.
Ring counts curr: {0: 21813, 1: 71212, 2: 46509, 3: 93467, 4: 195170, 5: 425665, 6: 311560, 7: 151811, 8: 74382, 9: 39081}.

### a11_a08_proud_radius_015

Comparison: `a08_mid_mask_proud5_kh1120_ab3239_scale100`. Mean IoU 0.811.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 586619, K 145196, B1 348607, A1 195286, A2 81106, A3 174013, B2 397359.
Class counts curr: Bg 583529, K 141697, B1 334406, A1 201686, A2 92361, A3 176724, B2 397783.
Class delta: Bg -3090, K -3499, B1 -14201, A1 +6400, A2 +11255, A3 +2711, B2 +424.
Ring counts prev: {0: 21835, 1: 61818, 2: 46010, 3: 93053, 4: 194827, 5: 422563, 6: 310233, 7: 151345, 8: 74339, 9: 38929}.
Ring counts curr: {0: 22178, 1: 82597, 2: 34155, 3: 93608, 4: 198588, 5: 427011, 6: 317058, 7: 156138, 8: 75805, 9: 39287}.

### a12_a08_smoothing_offset_m005

Comparison: `a08_mid_mask_proud5_kh1120_ab3239_scale100`. Mean IoU 0.847.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 586619, K 145196, B1 348607, A1 195286, A2 81106, A3 174013, B2 397359.
Class counts curr: Bg 584283, K 144688, B1 349452, A1 196044, A2 80964, A3 174664, B2 398091.
Class delta: Bg -2336, K -508, B1 +845, A1 +758, A2 -142, A3 +651, B2 +732.
Ring counts prev: {0: 21835, 1: 61818, 2: 46010, 3: 93053, 4: 194827, 5: 422563, 6: 310233, 7: 151345, 8: 74339, 9: 38929}.
Ring counts curr: {0: 21777, 1: 62899, 2: 46808, 3: 93351, 4: 195380, 5: 422030, 6: 309958, 7: 151818, 8: 74164, 9: 38951}.

### a13_a08_proud_radius_007

Comparison: `a08_mid_mask_proud5_kh1120_ab3239_scale100`. Mean IoU 0.849.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 586619, K 145196, B1 348607, A1 195286, A2 81106, A3 174013, B2 397359.
Class counts curr: Bg 585978, K 144280, B1 349871, A1 195143, A2 80268, A3 174141, B2 398505.
Class delta: Bg -641, K -916, B1 +1264, A1 -143, A2 -838, A3 +128, B2 +1146.
Ring counts prev: {0: 21835, 1: 61818, 2: 46010, 3: 93053, 4: 194827, 5: 422563, 6: 310233, 7: 151345, 8: 74339, 9: 38929}.
Ring counts curr: {0: 21851, 1: 60577, 2: 46468, 3: 93086, 4: 195201, 5: 421485, 6: 308960, 7: 151723, 8: 74103, 9: 38876}.

### a14_ab3100

Comparison: `a13_a08_proud_radius_007`. Mean IoU 0.804.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585978, K 144280, B1 349871, A1 195143, A2 80268, A3 174141, B2 398505.
Class counts curr: Bg 572880, K 137435, B1 347828, A1 198422, A2 98382, A3 172793, B2 400446.
Class delta: Bg -13098, K -6845, B1 -2043, A1 +3279, A2 +18114, A3 -1348, B2 +1941.
Ring counts prev: {0: 21851, 1: 60577, 2: 46468, 3: 93086, 4: 195201, 5: 421485, 6: 308960, 7: 151723, 8: 74103, 9: 38876}.
Ring counts curr: {0: 22122, 1: 46695, 2: 47119, 3: 93454, 4: 196046, 5: 429371, 6: 313300, 7: 154069, 8: 75813, 9: 39273}.

### a15_ab3400

Comparison: `a13_a08_proud_radius_007`. Mean IoU 0.748.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585978, K 144280, B1 349871, A1 195143, A2 80268, A3 174141, B2 398505.
Class counts curr: Bg 632766, K 148557, B1 348128, A1 189120, A2 48282, A3 166317, B2 395016.
Class delta: Bg +46788, K +4277, B1 -1743, A1 -6023, A2 -31986, A3 -7824, B2 -3489.
Ring counts prev: {0: 21851, 1: 60577, 2: 46468, 3: 93086, 4: 195201, 5: 421485, 6: 308960, 7: 151723, 8: 74103, 9: 38876}.
Ring counts curr: {0: 20766, 1: 103759, 2: 45607, 3: 88268, 4: 189171, 5: 413405, 6: 298610, 7: 145461, 8: 72570, 9: 37507}.

### a16_angle_850

Comparison: `a13_a08_proud_radius_007`. Mean IoU 0.848.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585978, K 144280, B1 349871, A1 195143, A2 80268, A3 174141, B2 398505.
Class counts curr: Bg 584972, K 144443, B1 349526, A1 194912, A2 81014, A3 174752, B2 398567.
Class delta: Bg -1006, K +163, B1 -345, A1 -231, A2 +746, A3 +611, B2 +62.
Ring counts prev: {0: 21851, 1: 60577, 2: 46468, 3: 93086, 4: 195201, 5: 421485, 6: 308960, 7: 151723, 8: 74103, 9: 38876}.
Ring counts curr: {0: 21726, 1: 63111, 2: 46083, 3: 92912, 4: 195091, 5: 422564, 6: 309684, 7: 151312, 8: 73762, 9: 38855}.

### a17_angle_650

Comparison: `a13_a08_proud_radius_007`. Mean IoU 0.850.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585978, K 144280, B1 349871, A1 195143, A2 80268, A3 174141, B2 398505.
Class counts curr: Bg 585718, K 144984, B1 349478, A1 195379, A2 80637, A3 174036, B2 397954.
Class delta: Bg -260, K +704, B1 -393, A1 +236, A2 +369, A3 -105, B2 -551.
Ring counts prev: {0: 21851, 1: 60577, 2: 46468, 3: 93086, 4: 195201, 5: 421485, 6: 308960, 7: 151723, 8: 74103, 9: 38876}.
Ring counts curr: {0: 21781, 1: 63227, 2: 46116, 3: 92906, 4: 194225, 5: 422426, 6: 310400, 7: 151536, 8: 74231, 9: 38892}.

### a18_width_1100

Comparison: `a17_angle_650`. Mean IoU 0.848.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585718, K 144984, B1 349478, A1 195379, A2 80637, A3 174036, B2 397954.
Class counts curr: Bg 581420, K 143605, B1 351442, A1 196410, A2 80046, A3 174281, B2 400982.
Class delta: Bg -4298, K -1379, B1 +1964, A1 +1031, A2 -591, A3 +245, B2 +3028.
Ring counts prev: {0: 21781, 1: 63227, 2: 46116, 3: 92906, 4: 194225, 5: 422426, 6: 310400, 7: 151536, 8: 74231, 9: 38892}.
Ring counts curr: {0: 21768, 1: 52889, 2: 46892, 3: 93167, 4: 196404, 5: 425189, 6: 311553, 7: 152259, 8: 74930, 9: 39106}.

### a19_width_1300

Comparison: `a17_angle_650`. Mean IoU 0.847.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585718, K 144984, B1 349478, A1 195379, A2 80637, A3 174036, B2 397954.
Class counts curr: Bg 585998, K 144793, B1 349091, A1 195221, A2 81156, A3 173705, B2 398222.
Class delta: Bg +280, K -191, B1 -387, A1 -158, A2 +519, A3 -331, B2 +268.
Ring counts prev: {0: 21781, 1: 63227, 2: 46116, 3: 92906, 4: 194225, 5: 422426, 6: 310400, 7: 151536, 8: 74231, 9: 38892}.
Ring counts curr: {0: 21619, 1: 66853, 2: 45916, 3: 93333, 4: 194804, 5: 420252, 6: 308486, 7: 151151, 8: 74044, 9: 38791}.

### a20_b1_height_1519

Comparison: `a17_angle_650`. Mean IoU 0.849.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585718, K 144984, B1 349478, A1 195379, A2 80637, A3 174036, B2 397954.
Class counts curr: Bg 586069, K 144195, B1 349705, A1 195439, A2 80214, A3 173887, B2 398677.
Class delta: Bg +351, K -789, B1 +227, A1 +60, A2 -423, A3 -149, B2 +723.
Ring counts prev: {0: 21781, 1: 63227, 2: 46116, 3: 92906, 4: 194225, 5: 422426, 6: 310400, 7: 151536, 8: 74231, 9: 38892}.
Ring counts curr: {0: 21832, 1: 61969, 2: 45974, 3: 92829, 4: 194152, 5: 423477, 6: 309562, 7: 151936, 8: 74095, 9: 38927}.

### a21_a2_over_a1

Comparison: `a17_angle_650`. Mean IoU 0.838.

Aligned cloud, 1928186 points. Predicted label changed on 34741 points.
Top transitions: Bg->B2 13481, Bg->B1 8232, Bg->A3 3738, Bg->K 3464, Bg->A1 3370, Bg->A2 1722, A1->A2 734.
Changed points by pred_ring: 5:14803, 6:5730, 4:4927, 3:3216, 7:2183, 2:1610, 8:976, 1:737.

### a22_a2_bias_2

Comparison: `a21_a2_over_a1`. Mean IoU 0.838.

Aligned cloud, 1928186 points. Predicted label changed on 891 points.
Top transitions: A2->A1 871, A3->A2 13, B2->A2 4, B1->A2 3.
Changed points by pred_ring: 5:411, 7:245, 3:68, 9:62, 4:44, 6:36, 1:21, 8:3.

### a23_a2_over_a1_on_a17

Comparison: `a17_angle_650`. Mean IoU 0.850.

Aligned cloud, 1928186 points. Predicted label changed on 734 points.
Top transitions: A1->A2 734.
Changed points by pred_ring: 5:319, 7:230, 9:64, 3:58, 6:29, 1:18, 4:15, 0:1.

### a24_reverse_circ

Comparison: `a17_angle_650`. Mean IoU 0.850.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585718, K 144984, B1 349478, A1 195379, A2 80637, A3 174036, B2 397954.
Class counts curr: Bg 585103, K 145252, B1 349401, A1 195307, A2 80715, A3 173805, B2 398603.
Class delta: Bg -615, K +268, B1 -77, A1 -72, A2 +78, A3 -231, B2 +649.
Ring counts prev: {0: 21781, 1: 63227, 2: 46116, 3: 92906, 4: 194225, 5: 422426, 6: 310400, 7: 151536, 8: 74231, 9: 38892}.
Ring counts curr: {0: 21755, 1: 62551, 2: 46301, 3: 92900, 4: 194857, 5: 421736, 6: 310188, 7: 151641, 8: 74124, 9: 38861}.

### a25_a1_scale_090

Comparison: `a17_angle_650`. Mean IoU 0.832.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585718, K 144984, B1 349478, A1 195379, A2 80637, A3 174036, B2 397954.
Class counts curr: Bg 609497, K 144897, B1 350256, A1 169224, A2 81464, A3 174390, B2 398458.
Class delta: Bg +23779, K -87, B1 +778, A1 -26155, A2 +827, A3 +354, B2 +504.
Ring counts prev: {0: 21781, 1: 63227, 2: 46116, 3: 92906, 4: 194225, 5: 422426, 6: 310400, 7: 151536, 8: 74231, 9: 38892}.
Ring counts curr: {0: 21086, 1: 88050, 2: 44356, 3: 92266, 4: 189140, 5: 417254, 6: 302472, 7: 149168, 8: 71812, 9: 38400}.

### a26_a2_scale_110

Comparison: `a17_angle_650`. Mean IoU 0.841.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585718, K 144984, B1 349478, A1 195379, A2 80637, A3 174036, B2 397954.
Class counts curr: Bg 587774, K 144879, B1 349097, A1 193875, A2 82318, A3 171875, B2 398368.
Class delta: Bg +2056, K -105, B1 -381, A1 -1504, A2 +1681, A3 -2161, B2 +414.
Ring counts prev: {0: 21781, 1: 63227, 2: 46116, 3: 92906, 4: 194225, 5: 422426, 6: 310400, 7: 151536, 8: 74231, 9: 38892}.
Ring counts curr: {0: 21690, 1: 64460, 2: 45661, 3: 93117, 4: 193089, 5: 423272, 6: 308425, 7: 151359, 8: 75068, 9: 38541}.

### a27_swap_a1_a2_walk

Comparison: `a17_angle_650`. Mean IoU 0.632.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585718, K 144984, B1 349478, A1 195379, A2 80637, A3 174036, B2 397954.
Class counts curr: Bg 584838, K 145001, B1 349854, A1 81285, A2 194882, A3 174117, B2 398209.
Class delta: Bg -880, K +17, B1 +376, A1 -114094, A2 +114245, A3 +81, B2 +255.
Ring counts prev: {0: 21781, 1: 63227, 2: 46116, 3: 92906, 4: 194225, 5: 422426, 6: 310400, 7: 151536, 8: 74231, 9: 38892}.
Ring counts curr: {0: 21774, 1: 65041, 2: 45955, 3: 92578, 4: 194795, 5: 421652, 6: 310709, 7: 151806, 8: 74023, 9: 38930}.

### a28_multimask

Comparison: `a17_angle_650`. Mean IoU 0.850.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585718, K 144984, B1 349478, A1 195379, A2 80637, A3 174036, B2 397954.
Class counts curr: Bg 583141, K 145629, B1 351910, A1 195987, A2 80145, A3 172572, B2 398802.
Class delta: Bg -2577, K +645, B1 +2432, A1 +608, A2 -492, A3 -1464, B2 +848.
Ring counts prev: {0: 21781, 1: 63227, 2: 46116, 3: 92906, 4: 194225, 5: 422426, 6: 310400, 7: 151536, 8: 74231, 9: 38892}.
Ring counts curr: {0: 22238, 1: 65090, 2: 47265, 3: 93575, 4: 194874, 5: 420317, 6: 309755, 7: 150145, 8: 74002, 9: 39182}.

### a29_a1_over_b1_on_a17

Comparison: `a17_angle_650`. Mean IoU 0.849.

Aligned cloud, 1928186 points. Predicted label changed on 871 points.
Top transitions: B1->A1 871.
Changed points by pred_ring: 5:364, 3:333, 7:113, 9:44, 1:17.

### a30_padding_250

Comparison: `a17_angle_650`. Mean IoU 0.848.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585718, K 144984, B1 349478, A1 195379, A2 80637, A3 174036, B2 397954.
Class counts curr: Bg 584760, K 145283, B1 350105, A1 195445, A2 80193, A3 173876, B2 398524.
Class delta: Bg -958, K +299, B1 +627, A1 +66, A2 -444, A3 -160, B2 +570.
Ring counts prev: {0: 21781, 1: 63227, 2: 46116, 3: 92906, 4: 194225, 5: 422426, 6: 310400, 7: 151536, 8: 74231, 9: 38892}.
Ring counts curr: {0: 21842, 1: 64008, 2: 46902, 3: 93420, 4: 195391, 5: 420073, 6: 308023, 7: 151461, 8: 74080, 9: 38763}.

### a31_no_template_mask

Comparison: `a17_angle_650`. Mean IoU 0.782.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585718, K 144984, B1 349478, A1 195379, A2 80637, A3 174036, B2 397954.
Class counts curr: Bg 695756, K 132012, B1 336158, A1 178649, A2 55967, A3 148281, B2 381363.
Class delta: Bg +110038, K -12972, B1 -13320, A1 -16730, A2 -24670, A3 -25755, B2 -16591.
Ring counts prev: {0: 21781, 1: 63227, 2: 46116, 3: 92906, 4: 194225, 5: 422426, 6: 310400, 7: 151536, 8: 74231, 9: 38892}.
Ring counts curr: {0: 20014, 1: 197990, 2: 42870, 3: 84762, 4: 171049, 5: 381515, 6: 276516, 7: 138926, 8: 66451, 9: 35421}.

### a32_extra_ring_1

Comparison: `a17_angle_650`. Mean IoU 0.849.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585718, K 144984, B1 349478, A1 195379, A2 80637, A3 174036, B2 397954.
Class counts curr: Bg 584686, K 145273, B1 349164, A1 195725, A2 81135, A3 174174, B2 398029.
Class delta: Bg -1032, K +289, B1 -314, A1 +346, A2 +498, A3 +138, B2 +75.
Ring counts prev: {0: 21781, 1: 63227, 2: 46116, 3: 92906, 4: 194225, 5: 422426, 6: 310400, 7: 151536, 8: 74231, 9: 38892}.
Ring counts curr: {0: 21812, 1: 63975, 2: 46035, 3: 93050, 4: 194608, 5: 422626, 6: 310541, 7: 151862, 8: 74306, 9: 38869}.

### a33_a1_wrap_negatives

Comparison: `a17_angle_650`. Mean IoU 0.786.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585718, K 144984, B1 349478, A1 195379, A2 80637, A3 174036, B2 397954.
Class counts curr: Bg 632931, K 143782, B1 349908, A1 196587, A2 36386, A3 170113, B2 398479.
Class delta: Bg +47213, K -1202, B1 +430, A1 +1208, A2 -44251, A3 -3923, B2 +525.
Ring counts prev: {0: 21781, 1: 63227, 2: 46116, 3: 92906, 4: 194225, 5: 422426, 6: 310400, 7: 151536, 8: 74231, 9: 38892}.
Ring counts curr: {0: 20929, 1: 109442, 2: 44724, 3: 93187, 4: 184685, 5: 422850, 6: 292584, 7: 152431, 8: 55145, 9: 39032}.

### a34_ring2_label_shift

Comparison: `a17_angle_650`. Mean IoU 0.890.

Aligned cloud, 1928186 points. Predicted label changed on 44506 points.
Top transitions: B1->A1 14386, B2->K 11226, A1->A2 7372, K->B1 4968, A3->B2 4895, A2->A3 1659.
Changed points by pred_ring: 2:44506.
Changed r min/p50/max 2.7357/2.7532/2.7710.
Changed theta min/p50/max 1.940/8.836/15.408.
Changed intensity min/p50/max -1724/-1182/-568.
On pred_ring 2: 44506 changed; theta 1.940–15.408 (p50 8.836).
Ring-2 transitions: B1->A1 14386, B2->K 11226, A1->A2 7372, K->B1 4968, A3->B2 4895, A2->A3 1659.

### a35_min_forward_4

Comparison: `a17_angle_650`. Mean IoU 0.805.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585718, K 144984, B1 349478, A1 195379, A2 80637, A3 174036, B2 397954.
Class counts curr: Bg 621086, K 145010, B1 349433, A1 195909, A2 43827, A3 174581, B2 398340.
Class delta: Bg +35368, K +26, B1 -45, A1 +530, A2 -36810, A3 +545, B2 +386.
Ring counts prev: {0: 21781, 1: 63227, 2: 46116, 3: 92906, 4: 194225, 5: 422426, 6: 310400, 7: 151536, 8: 74231, 9: 38892}.
Ring counts curr: {0: 21831, 1: 99637, 2: 46276, 3: 87190, 4: 194683, 5: 402764, 6: 310588, 7: 142623, 8: 74376, 9: 37173}.

### a36_ring2_shift

Comparison: `a17_angle_650`. Mean IoU 0.888.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585718, K 144984, B1 349478, A1 195379, A2 80637, A3 174036, B2 397954.
Class counts curr: Bg 584619, K 151021, B1 340105, A1 202383, A2 86684, A3 171229, B2 392145.
Class delta: Bg -1099, K +6037, B1 -9373, A1 +7004, A2 +6047, A3 -2807, B2 -5809.
Ring counts prev: {0: 21781, 1: 63227, 2: 46116, 3: 92906, 4: 194225, 5: 422426, 6: 310400, 7: 151536, 8: 74231, 9: 38892}.
Ring counts curr: {0: 21622, 1: 63911, 2: 46140, 3: 92795, 4: 194809, 5: 422254, 6: 309942, 7: 151500, 8: 74049, 9: 38916}.

### a37_ring2_shift_after_proud

Comparison: `a36_ring2_shift`. Mean IoU 0.888.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 584619, K 151021, B1 340105, A1 202383, A2 86684, A3 171229, B2 392145.
Class counts curr: Bg 583107, K 151469, B1 340079, A1 202642, A2 87610, A3 170873, B2 392406.
Class delta: Bg -1512, K +448, B1 -26, A1 +259, A2 +926, A3 -356, B2 +261.
Ring counts prev: {0: 21622, 1: 63911, 2: 46140, 3: 92795, 4: 194809, 5: 422254, 6: 309942, 7: 151500, 8: 74049, 9: 38916}.
Ring counts curr: {0: 21723, 1: 61478, 2: 46556, 3: 93284, 4: 195280, 5: 423619, 6: 310538, 7: 151876, 8: 74028, 9: 38883}.

### a38_a34_proud_r10_5mm

Comparison: `a34_ring2_label_shift`. Mean IoU 0.889.

Aligned cloud, 1928186 points. Predicted label changed on 4548 points.
Top transitions: B2->Bg 1371, B1->Bg 1278, K->Bg 654, A3->Bg 481, A1->Bg 427, A2->Bg 337.
Changed points by pred_ring: 5:1592, 6:1147, 4:547, 3:418, 7:270, 2:226, 1:147, 8:121.
Changed r min/p50/max 2.7481/2.7595/2.7756.
Changed theta min/p50/max 1.951/8.576/15.370.
Changed intensity min/p50/max -1726/-1169/-77.
To background: 4548 (r p50 2.7595, intensity p50 -1169).
On pred_ring 2: 226 changed; theta 2.010–15.270 (p50 9.033).
Ring-2 transitions: K->Bg 62, A1->Bg 60, A2->Bg 44, B1->Bg 35, B2->Bg 15, A3->Bg 10.

### a39_a34_proud_r15_5mm

Comparison: `a34_ring2_label_shift`. Mean IoU 0.887.

Aligned cloud, 1928186 points. Predicted label changed on 7912 points.
Top transitions: B1->Bg 2812, B2->Bg 1883, K->Bg 1296, A3->Bg 694, A1->Bg 619, A2->Bg 608.
Changed points by pred_ring: 6:2803, 5:2373, 4:839, 7:542, 3:522, 2:303, 1:209, 8:175.
Changed r min/p50/max 2.7481/2.7597/2.7756.
Changed theta min/p50/max 1.951/8.575/15.335.
Changed intensity min/p50/max -1726/-1136/-77.
To background: 7912 (r p50 2.7597, intensity p50 -1136).
On pred_ring 2: 303 changed; theta 2.010–15.284 (p50 9.251).
Ring-2 transitions: A1->Bg 73, K->Bg 64, A2->Bg 57, B1->Bg 48, B2->Bg 45, A3->Bg 16.

### a40_a34_proud_r20_5mm

Comparison: `a34_ring2_label_shift`. Mean IoU 0.884.

Aligned cloud, 1928186 points. Predicted label changed on 12070 points.
Top transitions: B1->Bg 4865, B2->Bg 2418, K->Bg 2154, A2->Bg 918, A3->Bg 895, A1->Bg 820.
Changed points by pred_ring: 6:4997, 5:3175, 4:1170, 7:880, 3:663, 2:382, 8:265, 1:258.
Changed r min/p50/max 2.7483/2.7596/2.7756.
Changed theta min/p50/max 1.951/8.580/15.335.
Changed intensity min/p50/max -1726/-1105/-77.
To background: 12070 (r p50 2.7596, intensity p50 -1105).
On pred_ring 2: 382 changed; theta 2.008–15.284 (p50 9.248).
Ring-2 transitions: A1->Bg 88, B2->Bg 72, K->Bg 71, A2->Bg 64, B1->Bg 52, A3->Bg 35.

### a40_wrap_theta_on_a13

Comparison: `a13_a08_proud_radius_007`. Mean IoU 0.382.

Aligned cloud, 1928186 points. Predicted label changed on 853675 points.
Top transitions: B2->A3 362059, A3->A2 151135, B1->B2 150558, K->B2 36908, A2->A1 36600, K->A3 34644, B2->A2 33404, A3->A1 18244, Bg->A3 11876, Bg->B2 11537, Bg->A2 1006, B2->K 966.
Changed points by pred_ring: 5:316613, 6:160850, 7:106266, 4:101226, 3:67034, 9:28016, 2:25541, 8:18729.
Changed r min/p50/max 2.7210/2.7538/2.7758.
Changed theta min/p50/max 1.888/9.758/15.439.
Changed intensity min/p50/max -1727/-1077/487.
To background: 409 (r p50 2.7645, intensity p50 -1231).
On pred_ring 2: 25541 changed; theta 1.969–15.397 (p50 10.927).
Ring-2 transitions: B2->A3 9320, B1->B2 6286, A3->A2 4809, B2->A2 1785, K->B2 1292, K->A3 1155, Bg->B2 305, Bg->A3 245.

### a41_a34_proud_r10_6mm

Comparison: `a34_ring2_label_shift`. Mean IoU 0.890.

Aligned cloud, 1928186 points. Predicted label changed on 1176 points.
Top transitions: B1->Bg 386, B2->Bg 353, K->Bg 154, A3->Bg 120, A1->Bg 87, A2->Bg 76.
Changed points by pred_ring: 5:283, 6:267, 3:194, 4:170, 2:95, 1:83, 8:32, 7:28.
Changed r min/p50/max 2.7497/2.7609/2.7756.
Changed theta min/p50/max 1.988/8.539/15.302.
Changed intensity min/p50/max -1693/-1178/-826.
To background: 1176 (r p50 2.7609, intensity p50 -1178).
On pred_ring 2: 95 changed; theta 2.010–15.270 (p50 8.996).
Ring-2 transitions: K->Bg 25, A1->Bg 24, A2->Bg 23, B1->Bg 19, A3->Bg 2, B2->Bg 2.

### a42_a34_proud_r07_4mm

Comparison: `a34_ring2_label_shift`. Mean IoU 0.882.

Aligned cloud, 1928186 points. Predicted label changed on 19026 points.
Top transitions: B2->Bg 5763, B1->Bg 4644, A3->Bg 2390, A1->Bg 2340, K->Bg 2269, A2->Bg 1620.
Changed points by pred_ring: 5:7647, 6:4895, 4:2423, 7:1506, 3:1027, 8:529, 2:483, 1:209.
Changed r min/p50/max 2.7424/2.7577/2.7756.
Changed theta min/p50/max 1.911/8.607/15.398.
Changed intensity min/p50/max -1726/-1126/-77.
To background: 19026 (r p50 2.7577, intensity p50 -1126).
On pred_ring 2: 483 changed; theta 1.960–15.357 (p50 9.243).
Ring-2 transitions: A1->Bg 127, K->Bg 121, A2->Bg 92, B1->Bg 72, B2->Bg 55, A3->Bg 16.

### a43_ring2_shift_proud_r10_6mm

Comparison: `a34_ring2_label_shift`. Mean IoU 0.891.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585718, K 151242, B1 340060, A1 202393, A2 86350, A3 170800, B2 391623.
Class counts curr: Bg 579568, K 152196, B1 340967, A1 202908, A2 87206, A3 171787, B2 393554.
Class delta: Bg -6150, K +954, B1 +907, A1 +515, A2 +856, A3 +987, B2 +1931.
Ring counts prev: {0: 21781, 1: 63227, 2: 46116, 3: 92906, 4: 194225, 5: 422426, 6: 310400, 7: 151536, 8: 74231, 9: 38892}.
Ring counts curr: {0: 21740, 1: 62601, 2: 46575, 3: 93037, 4: 195242, 5: 422622, 6: 309474, 7: 151634, 8: 73973, 9: 38994}.

### a44_a13_ring2_b2theta

Comparison: `a13_a08_proud_radius_007`. Mean IoU 0.898.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585978, K 144280, B1 349871, A1 195143, A2 80268, A3 174141, B2 398505.
Class counts curr: Bg 585384, K 141859, B1 347799, A1 202584, A2 86576, A3 170773, B2 393211.
Class delta: Bg -594, K -2421, B1 -2072, A1 +7441, A2 +6308, A3 -3368, B2 -5294.
Ring counts prev: {0: 21851, 1: 60577, 2: 46468, 3: 93086, 4: 195201, 5: 421485, 6: 308960, 7: 151723, 8: 74103, 9: 38876}.
Ring counts curr: {0: 21921, 1: 59537, 2: 46611, 3: 92421, 4: 194958, 5: 422948, 6: 309768, 7: 152075, 8: 74281, 9: 38879}.

### a45_a44_intensity_m1400

Comparison: `a44_a13_ring2_b2theta`. Mean IoU 0.917.

Unaligned clouds (1928186 → 1928186 points).
Class counts prev: Bg 585384, K 141859, B1 347799, A1 202584, A2 86576, A3 170773, B2 393211.
Class counts curr: Bg 607333, K 142098, B1 347020, A1 197618, A2 78054, A3 165347, B2 390716.
Class delta: Bg +21949, K +239, B1 -779, A1 -4966, A2 -8522, A3 -5426, B2 -2495.
Ring counts prev: {0: 21921, 1: 59537, 2: 46611, 3: 92421, 4: 194958, 5: 422948, 6: 309768, 7: 152075, 8: 74281, 9: 38879}.
Ring counts curr: {0: 21705, 1: 60580, 2: 46368, 3: 92955, 4: 194814, 5: 424210, 6: 309656, 7: 151803, 8: 74038, 9: 38939}.

## Same-order supplements

Geom sampling marked some full-run pairs unaligned. Same-order label comparison still holds when `n` matches and the match rate is high. These supplements recover ring and intensity facts for the kept later stages.

### a34_ring2_label_shift versus a17 (aligned)

Predicted label changed on 44,506 points. Every changed point sits on pred_ring 2. No other ring changes.

Ring-2 transitions: B1→A1 14,386; B2→K 11,226; A1→A2 7,372; K→B1 4,968; A3→B2 4,895; A2→A3 1,659. That is the +1 lining cycle on pred_ring 2 only.

### a44 versus a13 (same-order, match rate 0.966)

Predicted label changed on 64,867 points. Of those, 44,944 sit on pred_ring 2.

Ring-2 transitions include B1→A1 14,501; B2→B1 7,565; A1→A2 7,442; K→B1 4,895; A3→B2 4,759; B2→K 3,550. The B2→B1 and B2→K split on the original B2 rows is the theta cut after the cycle. Stage log: shift 46,611, split 11,252.

### a45 versus a44 (same-order, match rate 0.979)

Predicted label changed on 40,738 points. Lining→background 26,071. Of those lining→background points, 22,914 have intensity below −1400 on the a44 cloud, and 3,157 sit at or above −1400. Intensity p50 of lining→background is −1480. Stage log dropped 23,387 dark points. Background class count rose by 21,949 in the unaligned summary.

### Sample proud (t29 / t30)

No arm directories. From `sample_orientation_and_bg_ceiling.md`: proud points are enriched for background relative to inset points of the same residual. The absolute 5 mm cut drops 4,021 true lining points and scores 0.899. The relative 5 mm proud cut scores 0.902 and spill 28,702.

