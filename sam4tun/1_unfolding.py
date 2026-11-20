#!/usr/bin/env python3
                                                                 
                     
import sys
import os
import matplotlib
matplotlib.use("Agg")

_SAM4TUN_DIR = os.path.dirname(os.path.abspath(__file__))
_SAM_PKG = os.path.join(_SAM4TUN_DIR, "segment-anything")
for _p in (_SAM4TUN_DIR, _SAM_PKG):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from helpers.design_blueprint import load_design_blueprint
from helpers.pipeline_io import ensure_dir
from helpers.pipeline_state import load_state, save_state

import family_io

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon
import cv2
import random
import time
import math
from tqdm.auto import tqdm
from sklearn.linear_model import RANSACRegressor
from sklearn.preprocessing import PolynomialFeatures
from numba import njit, prange
import faiss
from joblib import Parallel, delayed

tunnel_id = sys.argv[1]


params, param_file, family_mode = family_io.load_stage_params("unfolding")
print(f"[unified] stage=unfolding family_mode={family_mode}")
expected_keys = [
    "delta",
    "ransac_threshold", "ransac_probability", "ransac_inlier_ratio",
    "ransac_sample_size", "ransac_initial_iterations", "ransac_inlier_threshold_multiplier",
    "polynomial_degree", "num_samples_factor", "t_extrapolation_start", "t_extrapolation_end",
    "batch_size", "n_jobs",
]
for key in expected_keys:
    if key not in params:
        sys.exit(f"Missing required parameter '{key}' in {param_file}")
blueprint = load_design_blueprint()
diameter = float(blueprint["inner_diameter_m"])
ring_length_m = float(blueprint["ring_length_m"])
design_ring_count = int(blueprint["ring_count"])
drive_xy = np.asarray(blueprint["orientation_xy"], dtype=float)
slice_spacing_factor = ring_length_m
print(
    f"Design blueprint subset={blueprint['subset_id']}: "
    f"diameter={diameter} ring_length={ring_length_m} "
    f"ring_count={design_ring_count} "
    f"orientation=({drive_xy[0]:+.6f},{drive_xy[1]:+.6f})"
)
delta = params["delta"]
ransac_threshold = params["ransac_threshold"]
ransac_probability = params["ransac_probability"]
ransac_inlier_ratio = params["ransac_inlier_ratio"]
ransac_sample_size = params["ransac_sample_size"]
ransac_initial_iterations = params["ransac_initial_iterations"]
ransac_inlier_threshold_multiplier = params["ransac_inlier_threshold_multiplier"]
polynomial_degree = params["polynomial_degree"]
num_samples_factor = params["num_samples_factor"]
t_extrapolation_start = params["t_extrapolation_start"]
t_extrapolation_end = params["t_extrapolation_end"]
batch_size = params["batch_size"]
n_jobs = params["n_jobs"]
                                                                          
                                                                  
swap_tunnel_centers = bool(params.get("swap_tunnel_centers", False))
                                                                           
                                                                        
_use_top_tube = ("top_tube_radius" in params) or (family_mode == "complex")
top_tube_radius = float(params.get("top_tube_radius", 3.5))
top_tube_top_n = int(params.get("top_tube_top_n", 10))
                                                                              
vertical_filter_window = params.get("vertical_filter_window")
                                                                            
deterministic_theta_orientation = bool(params.get("deterministic_theta_orientation", False))
                                                                               
                                                                   
canonical_orientation = bool(params.get("canonical_orientation", False))
                                                                          
                                                                               
theta_sign = int(params.get("theta_sign", 1))
if theta_sign not in (-1, 1):
    sys.exit("theta_sign must be +1 or -1")
if canonical_orientation:
    deterministic_theta_orientation = True
residual_recentre = bool(params.get("residual_recentre", False))
recentre_bin_size = float(params.get("recentre_bin_size", 0.5))
recentre_r_tolerance = float(params.get("recentre_r_tolerance", 0.35))
recentre_min_bin_points = int(params.get("recentre_min_bin_points", 500))
                                                                     
                                                                        
random_seed = params.get("random_seed")
if random_seed is not None:
    random_seed = int(random_seed)
    random.seed(random_seed)
    np.random.seed(random_seed)
    print(f"Random seed pinned: {random_seed}")

paths = ensure_dir(tunnel_id)
                                                                          
                                                                            
point_cloud_data = np.loadtxt(paths["input_txt"], usecols=(0, 1, 2, 3))
print(point_cloud_data.shape)
points_xyz = point_cloud_data[:, :3]
intensity = point_cloud_data[:, 3]
df_point_cloud = pd.DataFrame({
    'x': points_xyz[:, 0], 'y': points_xyz[:, 1], 'z': points_xyz[:, 2],
    'intensity': intensity,
})

points_2d_xoy = points_xyz[:, :2]
convex_hull = ConvexHull(points_2d_xoy)
convex_hull_points = points_2d_xoy[convex_hull.vertices]
convex_polygon = Polygon(convex_hull_points)
min_bounding_rect = convex_polygon.minimum_rotated_rectangle
rect_vertices = np.array(min_bounding_rect.exterior.coords)[:-1]
edges = [np.linalg.norm(rect_vertices[i] - rect_vertices[(i + 1) % 4]) for i in range(4)]
short_edge_index = np.argmin(edges)
center1 = (rect_vertices[short_edge_index] + rect_vertices[(short_edge_index + 1) % 4]) / 2
center2 = (rect_vertices[(short_edge_index + 2) % 4] + rect_vertices[(short_edge_index + 3) % 4]) / 2

if canonical_orientation:
    axis_xy = np.asarray(center2 - center1, dtype=float)
    drive_dot = float(np.dot(axis_xy, drive_xy))
    swapped = drive_dot < 0
    if swapped:
        center1, center2 = center2, center1
    print(
        f"Metadata orientation: drive=({drive_xy[0]:+.4f},{drive_xy[1]:+.4f}) "
        f"dot={drive_dot:+.4f} -> {'swapped' if swapped else 'kept'} centres "
        f"(ring column not read; swap_tunnel_centers ignored)"
    )
elif swap_tunnel_centers:
    center1, center2 = center2, center1
vector = center2 - center1
print(vector)

plt.figure(figsize=(8, 8))
sample_size = 10000
indices = np.random.choice(len(points_2d_xoy), size=sample_size, replace=False)
sampled_points = points_2d_xoy[indices]
plt.scatter(sampled_points[:, 0], sampled_points[:, 1], s=1, c='blue', label='Projected Points')
for simplex in convex_hull.simplices:
    plt.plot(points_2d_xoy[simplex, 0], points_2d_xoy[simplex, 1], 'k-')
rect_x, rect_y = zip(*(np.array(min_bounding_rect.exterior.coords)))
plt.plot(rect_x, rect_y, 'r-', label='Minimum Bounding Rectangle')
plt.plot(center1[0], center1[1], 'go', label='Center 1 of Short Edge')
plt.plot(center2[0], center2[1], 'mo', label='Center 2 of Short Edge')
plt.arrow(center1[0], center1[1], vector[0], vector[1], head_width=1, head_length=1, fc='green', ec='green', label='Direction Vector')
plt.xlabel('X-axis'); plt.ylabel('Y-axis')
plt.title('Projected Point Cloud and Bounding Rectangle')
plt.legend(); plt.axis('equal'); plt.grid(True)
plt.savefig(os.path.join(os.path.dirname(paths["state"]), "projected_point_cloud_bbox.png"), dpi=150, bbox_inches='tight')

def generate_slicing_planes_point_cloud(center1, center2, points_xyz, delta, ring_count, ring_length):

                                                                        
    l = np.linalg.norm(center2[:2] - center1[:2])
    implied_n = round(l / ring_length) if ring_length > 0 else ring_count
    optimal_n = int(ring_count)
    if implied_n != optimal_n:
        print(
            f"Design ring_count={optimal_n} used; span/ring_length implies {implied_n} "
            f"(span={l:.3f}m ring_length={ring_length})"
        )

                                                
    points_on_plane = []
    planes = []
    origin = []

                                                   
    direction = (center2 - center1) / np.linalg.norm(center2 - center1)
    total_distance = np.linalg.norm(center2 - center1)
    first_distance = total_distance / (2 * optimal_n)
    last_distance = total_distance - first_distance

                     
    for i in range(optimal_n):
        if i == 0:
            segment_length = first_distance
        elif i == optimal_n - 1:
            segment_length = last_distance
        else:
            segment_length = first_distance + (i * (last_distance - first_distance)) / (optimal_n - 1)

        point_on_plane = center1 + (segment_length / total_distance) * (center2 - center1)
        points_on_plane.append(point_on_plane)
        origin.append(np.append(point_on_plane, 0))                                              

        normal_vector = np.append(direction, 0)
        d = -np.dot(normal_vector[:2], point_on_plane)
        plane = np.append(normal_vector, d)
        planes.append(plane)

                                   
    slicing_cloud = []
    Delta = delta                                

    points_xyz = np.asarray(points_xyz)                                      

                                               
    for plane in tqdm(planes, desc="Processing planes"):
        a, b, c, d = plane
        Wr = a * points_xyz[:, 0] + b * points_xyz[:, 1] + c * points_xyz[:, 2] + d - Delta
        Wl = a * points_xyz[:, 0] + b * points_xyz[:, 1] + c * points_xyz[:, 2] + d + Delta
        mask = (Wr * Wl <= 0)
        slicing_cloud.append(points_xyz[mask])

    return origin, planes, slicing_cloud
origin, planes, slicing_cloud = generate_slicing_planes_point_cloud(
    center1, center2, points_xyz, delta, design_ring_count, ring_length_m
)
print(f"Number of sliced clouds: {len(slicing_cloud)}")
ring_count = len(slicing_cloud)
if ring_count != design_ring_count:
    sys.exit(f"slice count {ring_count} != design ring_count {design_ring_count}")
                                                      
import numpy as np

def project_to_plane(point_cloud, center, normal):

    
    shifted_point_cloud = np.array(point_cloud) - np.array(center)
    
                                                                               
    projection = np.dot(shifted_point_cloud, normal)
    
                                                                     
    projected_points = shifted_point_cloud - np.outer(projection, normal)
    
                                                   
    x_axis = np.array([-normal[1], normal[0], 0])
    x_axis /= np.linalg.norm(x_axis)

                                                         
    y_axis = np.cross(normal, x_axis)

                                                                                     
    x_coords = np.dot(projected_points, x_axis)
    y_coords = np.dot(projected_points, y_axis)
    
    return np.vstack((x_coords, y_coords)).T
                                                    
normal = np.array([planes[0][0], planes[0][1], 0])

                                                    
point2ds = []
for i in range(len(origin)):
    point2ds_temp = project_to_plane(slicing_cloud[i], origin[i], normal)
    point2ds.append(point2ds_temp)

filtered_point2ds = []
if _use_top_tube:
                                                                           
                                              
    print(
        f"Slice filter: remove_top_tube radius={top_tube_radius} top_n={top_tube_top_n}"
    )

    def _stable_extreme(points, coord_index, top_n):
        sorted_points = sorted(points, key=lambda p: p[coord_index], reverse=True)
        top_points = sorted_points[:top_n]
        bottom_points = sorted_points[-top_n:]
        if not top_points or not bottom_points:
            return None, None
        max_val = top_points[0][coord_index]
        min_val = bottom_points[-1][coord_index]
        threshold = (max_val - min_val) * 0.1
        stable_top = [p for p in top_points if abs(p[coord_index] - max_val) <= threshold]
        stable_bottom = [p for p in bottom_points if abs(p[coord_index] - min_val) <= threshold]
        stable_max = max(p[coord_index] for p in stable_top) if stable_top else max_val
        stable_min = min(p[coord_index] for p in stable_bottom) if stable_bottom else min_val
        return stable_max, stable_min

    for points in point2ds:
        x_max, x_min = _stable_extreme(points, 0, top_tube_top_n)
        y_max, y_min = _stable_extreme(points, 1, top_tube_top_n)
        if None in (x_max, x_min, y_max, y_min):
            filtered_point2ds.append(list(points))
            continue
        x_mid = (x_max + x_min) / 2.0
        y_mid = (y_max + y_min) / 2.0
        filtered_points = [
            point
            for point in points
            if ((point[0] - x_mid) ** 2 + (point[1] - y_mid) ** 2) > top_tube_radius ** 2
        ]
        filtered_point2ds.append(filtered_points)
elif vertical_filter_window is not None:
                                                                              
                                                                       
    print(f"Slice filter: y_max window <= {vertical_filter_window}")
    for points in point2ds:
        y_max = max(point[1] for point in points)
        filtered_points = [
            point for point in points if abs(point[1] - y_max) <= vertical_filter_window
        ]
        filtered_point2ds.append(filtered_points)
else:
    sys.exit(
        "No slice filter configured: provide top_tube_radius (complex mode) or "
        "vertical_filter_window (staggered/continuous)."
    )
                         
import matplotlib.pyplot as plt

x_coords = [point[0] for point in filtered_point2ds[8]]
y_coords = [point[1] for point in filtered_point2ds[8]]

plt.scatter(x_coords, y_coords, c='blue', s=1, marker='o', label='Point Cloud')

plt.title('2D Point Cloud Visualization')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.legend()
plt.axis('equal')
plt.grid(True)
plt.savefig(os.path.join(os.path.dirname(paths["state"]), "slice_point_cloud_2d.png"), dpi=150, bbox_inches='tight')
            
import cv2
import random
import time

class RANSAC:
    def __init__(self, data, threshold, P, S, N, initial_iterations=999, inlier_threshold_multiplier=0.8):
        self.point_data = data                          
        self.error_threshold = threshold                             
        self.N = N                              
        self.S = S                
        self.P = P                                          
        self.max_inliers = len(data) * S                             
        self.items = initial_iterations                        
        self.inlier_threshold_multiplier = inlier_threshold_multiplier
        self.count = 0                     
        self.best_model = ((0, 0), (1e-6, 1e-6), 0)                      

    def random_sampling(self, n):

        return np.asarray(random.sample(list(self.point_data), n))

    def Geometric2Conic(self, ellipse):

        (x0, y0), (bb, aa), phi_b_deg = ellipse
        a, b = aa / 2, bb / 2                                  
        phi_b_rad = np.radians(phi_b_deg)                            
        ax, ay = -np.sin(phi_b_rad), np.cos(phi_b_rad)                          

                          
        a2, b2 = a * a, b * b
        if a2 > 0 and b2 > 0:
            A = ax * ax / a2 + ay * ay / b2
            B = 2 * ax * ay / a2 - 2 * ax * ay / b2
            C = ay * ay / a2 + ax * ax / b2
            D = (-2 * ax * ay * y0 - 2 * ax * ax * x0) / a2 + (2 * ax * ay * y0 - 2 * ay * ay * x0) / b2
            E = (-2 * ax * ay * x0 - 2 * ay * ay * y0) / a2 + (2 * ax * ay * x0 - 2 * ax * ax * y0) / b2
            F = (2 * ax * ay * x0 * y0 + ax * ax * x0 * x0 + ay * ay * y0 * y0) / a2 + \
                (-2 * ax * ay * x0 * y0 + ay * ay * x0 * x0 + ax * ax * y0 * y0) / b2 - 1
        else:
            A, B, C, D, E, F = 1, 0, 1, 0, 0, -1e-6                                

        return np.array([A, B, C, D, E, F])

    def eval_model(self, ellipse):

        a, b, c, d, e, f = self.Geometric2Conic(ellipse)
        E = 4 * a * c - b * b
        if E <= 0:
            return 0, np.array([])                  

        (x, y), (LAxis, SAxis), Angle = ellipse
        LAxis, SAxis = LAxis / 2, SAxis / 2
        if SAxis > LAxis:
            SAxis, LAxis = LAxis, SAxis                                  

                        
        Axis = math.sqrt(LAxis**2 - SAxis**2)
        f1_x = x - Axis * math.cos(math.radians(Angle))
        f1_y = y - Axis * math.sin(math.radians(Angle))
        f2_x = x + Axis * math.cos(math.radians(Angle))
        f2_y = y + Axis * math.sin(math.radians(Angle))

                                   
        f1, f2 = np.array([f1_x, f1_y]), np.array([f2_x, f2_y])
        f1_distance = np.sum((self.point_data - f1)**2, axis=1)
        f2_distance = np.sum((self.point_data - f2)**2, axis=1)
        all_distance = np.sqrt(f1_distance) + np.sqrt(f2_distance)

                          
        Z = np.abs(2 * LAxis - all_distance)
        delta = np.sqrt(np.mean((Z - np.mean(Z))**2))
        inliers = np.where(Z < self.inlier_threshold_multiplier * delta)[0]
        inlier_points = self.point_data[inliers]

        return len(inlier_points), inlier_points

    def execute_ransac(self):

        start_time = time.time()
        use_legacy = family_mode in ("staggered", "continuous")
        if use_legacy:
            while math.ceil(self.items):
                select_points = self.random_sampling(self.N)
                select_points_list = [(point[0], point[1]) for point in select_points]
                ellipse = cv2.fitEllipse(np.array(select_points_list, dtype=np.float32))
                inliers_count, inliers_set = self.eval_model(ellipse)
                inliers_set = np.array([tuple(point) for point in inliers_set], dtype=np.float32)
                if inliers_count > self.count:
                    self.count = inliers_count
                    if len(inliers_set) >= 5:
                        self.best_model = cv2.fitEllipse(inliers_set)
                    if self.count > self.max_inliers:
                        print('Inlier ratio: ', self.count / len(self.point_data))
                        break
                    self.items = math.log(1 - self.P) / math.log(
                        1 - (inliers_count / len(self.point_data)) ** self.N
                    )
        else:
                                                                             
                                                                              
            remaining = max(int(math.ceil(self.items)), 1)
            hard_cap = max(remaining, int(self.items) if self.items else 999)
            remaining = min(remaining, hard_cap)
            while remaining > 0:
                remaining -= 1
                select_points = self.random_sampling(self.N)
                select_points_list = [(point[0], point[1]) for point in select_points]
                ellipse = cv2.fitEllipse(np.array(select_points_list, dtype=np.float32))
                inliers_count, inliers_set = self.eval_model(ellipse)
                inliers_set = np.array([tuple(point) for point in inliers_set], dtype=np.float32)
                if inliers_count > self.count:
                    self.count = inliers_count
                    if len(inliers_set) >= 5:
                        self.best_model = cv2.fitEllipse(inliers_set)
                    if self.count > self.max_inliers:
                        print('Inlier ratio: ', self.count / len(self.point_data))
                        break
                    ratio = inliers_count / max(len(self.point_data), 1)
                    if 0 < ratio < 1:
                        denom = 1 - ratio ** self.N
                        if 0 < denom < 1:
                            remaining = min(
                                remaining,
                                max(int(math.ceil(math.log(1 - self.P) / math.log(denom))), 1),
                            )
            if self.count <= self.max_inliers:
                print(
                    f"Inlier ratio (best, below target): "
                    f"{self.count / max(len(self.point_data), 1):.4f}"
                )
        if self.best_model is None:
            raise RuntimeError(
                f"RANSAC failed: no ellipse model with >=5 inliers ({len(self.point_data)} points)"
            )
        return self.best_model, inliers_set
                                           
X_center = []
Y_center = []

LAxis_sets = []
SAxis_sets = []
Angle_sets = []
in_sets = []

for i in range(len(slicing_cloud)):
                                   
    points_data = np.reshape(filtered_point2ds[i], (-1, 2))                       

                                              
    ransac = RANSAC(data=points_data, threshold=ransac_threshold, P=ransac_probability, S=ransac_inlier_ratio, N=ransac_sample_size, initial_iterations=ransac_initial_iterations, inlier_threshold_multiplier=ransac_inlier_threshold_multiplier)
    ellipse_params, inliers_set = ransac.execute_ransac()

                                                    
    refine_pts = np.reshape(inliers_set, (-1, 2))
    if len(refine_pts) >= 5:
        ransac_refine = RANSAC(
            data=refine_pts, threshold=ransac_threshold, P=ransac_probability,
            S=ransac_inlier_ratio, N=ransac_sample_size,
            initial_iterations=ransac_initial_iterations,
            inlier_threshold_multiplier=ransac_inlier_threshold_multiplier,
        )
        ellipse_params, _ = ransac_refine.execute_ransac()
    else:
        print(f"  Plane {i}: skipping refine RANSAC ({len(refine_pts)} inliers < 5)")

                                
    ((X, Y), (LAxis, SAxis), Angle) = ellipse_params

    X_center.append(X)
    Y_center.append(Y)

    LAxis_sets.append(LAxis)
    SAxis_sets.append(SAxis)
    Angle_sets.append(Angle)
    in_sets.append(inliers_set)

print('done')
                                      
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
i = 8
ip1 = in_sets[i][:,0]
ip2 = in_sets[i][:,1]

ellipse = Ellipse(xy=(X_center[i],Y_center[i]), width=LAxis_sets[i], height=SAxis_sets[i], angle=Angle_sets[i], edgecolor='b', fc='None')
print(ellipse)
plt.figure('Draw')
plt.scatter(ip1,ip2,s=3,color='green')
plt.scatter(X_center[i],Y_center[i],color='red')
plt.gca().add_patch(ellipse)
plt.axis('equal')
plt.title('cross section - 2d points')
plt.grid(True)
plt.draw()
def get_3dcoordinates_from_plane(point2d,plane_params,origin):

    xp,yp = point2d
    A,B,C,D = plane_params
    x0,y0,z0 = origin
    
                                
    N = np.array([A, B, C])
    N = N / np.linalg.norm(N)
    
                                                                         
    Vx = -B
    Vy = A
    Vz = 0
    V = np.array([Vx, Vy, Vz])
    V = V / np.linalg.norm(V)
    
                                                                         
    U = np.cross(N, V)
    U = U / np.linalg.norm(U)
    
                              
    x = x0+xp*V[0]+yp*U[0]
    y = y0+xp*V[1]+yp*U[1]
    z = z0+xp*V[2]+yp*U[2]
    
    return [x,y,z]
                                         
cps = []

                                              
for i in range(len(slicing_cloud)):
    point2d_cp = np.array([X_center[i], Y_center[i]])
    cp = get_3dcoordinates_from_plane(point2d_cp, planes[i], origin[i])
    cps.append(cp)

                                     
cps_arr= np.array(cps)

len(cps_arr)                                       
                  
from mpl_toolkits.mplot3d import Axes3D

x = cps_arr[:, 0]
y = cps_arr[:, 1]
z = cps_arr[:, 2]

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

sc = ax.scatter(x, y, z, c=z, cmap='viridis', s=100)

cbar = plt.colorbar(sc)
cbar.set_label('Value of z')

ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_zlabel('Z axis')
ax.set_title('3D Scatter Plot')

ax.view_init(elev=15, azim=0)
ax.set_aspect('auto')
ax.set_box_aspect([1,1,1])
plt.savefig(os.path.join(os.path.dirname(paths["state"]), "ellipse_centres_3d.png"), dpi=150, bbox_inches='tight')
            
                                             
import numpy as np
from sklearn.linear_model import RANSACRegressor
from sklearn.preprocessing import PolynomialFeatures
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

                                                                    
t = np.arange(ring_count)

                                        
degree = polynomial_degree
poly = PolynomialFeatures(degree)

                                                        
t_poly = poly.fit_transform(t.reshape(-1, 1))
x_poly = t_poly
y_poly = t_poly
z_poly = t_poly

                                         
ransac_x = RANSACRegressor(random_state=random_seed)
ransac_y = RANSACRegressor(random_state=random_seed)
ransac_z = RANSACRegressor(random_state=random_seed)

                                             
ransac_x.fit(x_poly, cps_arr[:, 0])
ransac_y.fit(y_poly, cps_arr[:, 1])
ransac_z.fit(z_poly, cps_arr[:, 2])

                                            
x_coef = ransac_x.estimator_.coef_
y_coef = ransac_y.estimator_.coef_
z_coef = ransac_z.estimator_.coef_
x_intercept = ransac_x.estimator_.intercept_
y_intercept = ransac_y.estimator_.intercept_
z_intercept = ransac_z.estimator_.intercept_

                                                   
x_params = x_coef.copy()
x_params[0] = x_intercept

y_params = y_coef.copy()
y_params[0] = y_intercept

z_params = z_coef.copy()
z_params[0] = z_intercept

                                    
print("X parameters:", x_params)
print("Y parameters:", y_params)
print("Z parameters:", z_params)

                             
t_extend = np.linspace(-2, ring_count+1, 100)
t_extend_poly = poly.transform(t_extend.reshape(-1, 1))

                                            
x_fit_extend = ransac_x.predict(t_extend_poly)
y_fit_extend = ransac_y.predict(t_extend_poly)
z_fit_extend = ransac_z.predict(t_extend_poly)

                                                      
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

                                                    
ax.scatter(cps_arr[:, 0], cps_arr[:, 1], cps_arr[:, 2], color='blue', label='Data Points')
ax.plot(x_fit_extend, y_fit_extend, z_fit_extend, color='orange', label='Fitted Curve')

                 
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.legend()

                
ax.view_init(elev=90, azim=-90)                                                              

                                
xlim = ax.get_xlim()
ylim = ax.get_ylim()
zlim = ax.get_zlim()

                                                                
max_range = np.array([xlim[1] - xlim[0], ylim[1] - ylim[0], zlim[1] - zlim[0]]).max()
mid_x = np.mean(xlim)
mid_y = np.mean(ylim)
mid_z = np.mean(zlim)

ax.set_xlim(mid_x - max_range / 2, mid_x + max_range / 2)
ax.set_ylim(mid_y - max_range / 2, mid_y + max_range / 2)
ax.set_zlim(mid_z - max_range / 2, mid_z + max_range / 2)

plt.savefig(os.path.join(os.path.dirname(paths["state"]), "tunnel_centre_curve_3d.png"), dpi=150, bbox_inches='tight')
            
import numpy as np
from numba import njit, prange
import faiss
from joblib import Parallel, delayed
from tqdm.auto import tqdm
import time

@njit
def poly_eval(coeffs, x):
    result = 0.0
    for coeff in coeffs:
        result = result * x + coeff
    return result

@njit(parallel=True)
def curve_func(t, x_params, y_params, z_params):
    result = np.empty((len(t), 3))
    for i in prange(len(t)):
        result[i, 0] = poly_eval(x_params[::-1], t[i])
        result[i, 1] = poly_eval(y_params[::-1], t[i])
        result[i, 2] = poly_eval(z_params[::-1], t[i])
    return result

@njit
def poly_deriv(coeffs):
    return np.array([i * c for i, c in enumerate(coeffs[:0:-1])][::-1])

@njit(parallel=True)
def curve_deriv(t, x_params, y_params, z_params):
    result = np.empty((len(t), 3))
    dx_params = poly_deriv(x_params[::-1])
    dy_params = poly_deriv(y_params[::-1])
    dz_params = poly_deriv(z_params[::-1])
    for i in prange(len(t)):
        result[i, 0] = poly_eval(dx_params, t[i])
        result[i, 1] = poly_eval(dy_params, t[i])
        result[i, 2] = poly_eval(dz_params, t[i])
    return result
    
@njit
def calculate_angle_with_direction(A, B, C, T, deterministic_orientation, theta_sign_local):

    AB = B - A
    BC = C - B
    
    dot_product = np.dot(AB, BC)
    norm_AB = np.sqrt(np.dot(AB, AB))
    norm_BC = np.sqrt(np.dot(BC, BC))
    
    if norm_AB == 0 or norm_BC == 0:
        return 0.0, np.linalg.norm(AB)
    
    cos_angle = dot_product / (norm_AB * norm_BC)
    angle_radians = np.arccos(cos_angle)
    angle_degrees = angle_radians * (180.0 / np.pi)
    if deterministic_orientation:
        side = AB[0] * T[1] - AB[1] * T[0]
    else:
        cross_product = np.cross(AB, BC)
        side = cross_product[2]
    if theta_sign_local < 0:
        side = -side
    if side < 0:
        angle_degrees = 360 - angle_degrees

    return angle_degrees, np.linalg.norm(AB)

@njit
def compute_C_points_and_arc_length(B_points, T_vectors, arc_lengths):
    C_points = np.empty_like(B_points)
    for i in range(B_points.shape[0]):
        B = B_points[i]
        T = T_vectors[i]
        lambda_ = -T[2] / (T[0]**2 + T[1]**2)
        C = B + lambda_ * np.array([T[0], T[1], 0]) + np.array([0, 0, 1])
        C_points[i] = C

                            
        if i > 0:
            prev_B = B_points[i-1]
            arc_lengths[i] = arc_lengths[i-1] + np.linalg.norm(B - prev_B)
        else:
            arc_lengths[i] = 0.0
    
    return C_points, arc_lengths

                                                                                       
num_samples = ring_count * num_samples_factor                      
t_samples = np.linspace(t_extrapolation_start, ring_count + t_extrapolation_end, num_samples)
B_points = curve_func(t_samples, x_params, y_params, z_params)
T_vectors = curve_deriv(t_samples, x_params, y_params, z_params)
arc_lengths = np.zeros(num_samples, dtype=np.float32)

C_points, arc_lengths = compute_C_points_and_arc_length(B_points, T_vectors, arc_lengths)
print(
    f"Theta orientation: {'deterministic (travel direction)' if deterministic_theta_orientation else 'legacy (notebook, Tz-sign dependent)'}; "
    f"theta_sign={theta_sign:+d}; median centreline Tz={np.median(T_vectors[:, 2]):.5f}"
)

                   
index = faiss.IndexFlatL2(3)
index.add(B_points)

start_time = time.time()

                                                           
def process_batch(points_batch):

    _, idx_batch = index.search(points_batch, 1)
    results = []
    
    for i in range(points_batch.shape[0]):
        A = points_batch[i]
        idx = idx_batch[i][0]
        B = B_points[idx]
        C = C_points[idx]
        T = T_vectors[idx]
        angle_ABC, distance_AB = calculate_angle_with_direction(
            A, B, C, T, deterministic_theta_orientation, theta_sign
        )
        arc_length_B = arc_lengths[idx]
        results.append((distance_AB, angle_ABC, arc_length_B))
    
    return results

                                                   
num_batches = (len(points_xyz) + batch_size - 1) // batch_size
points_batches = np.array_split(points_xyz, num_batches)

                                            
cylindrical_coords_batches = Parallel(n_jobs=n_jobs)(
    delayed(process_batch)(batch) for batch in tqdm(points_batches, desc="Calculating cylindrical coordinates", total=len(points_batches))
)

cylindrical_coords = []
for batch_result in cylindrical_coords_batches:
    cylindrical_coords.extend(batch_result)

end_time = time.time()

print(f"Total computation time: {end_time - start_time:.6f} seconds")
                
import pandas as pd

df_point_cloud['r'] = np.array(cylindrical_coords)[:,0]
df_point_cloud['theta'] = np.array(cylindrical_coords)[:,1]* (np.pi*diameter / 360)
df_point_cloud['h'] = np.array(cylindrical_coords)[:,2]
df_point_cloud.head()

if canonical_orientation:
                                                                                       
                                                                                         
    _pts = df_point_cloud[["x", "y", "z"]].to_numpy(dtype=float)
    _centred = _pts - _pts.mean(axis=0)
    if len(_centred) > 50_000:
        _idx = np.random.default_rng(0).choice(len(_centred), 50_000, replace=False)
        _sample = _centred[_idx]
    else:
        _sample = _centred
    _, _, _vt = np.linalg.svd(_sample, full_matrices=False)
    _axis = _vt[0]
    _k = int(np.argmax(np.abs(_axis)))
    if _axis[_k] < 0:
        _axis = -_axis
    _t = _centred @ _axis
    h_axis_corr = float(pd.Series(_t).corr(df_point_cloud["h"]))
    _drive_proj = float(np.dot(_axis[:2], drive_xy))
    expected_sign = 1 if _drive_proj >= 0 else -1
    print(
        f"Canonical invariant (label-free): corr(h, axis)={h_axis_corr:+.4f} "
        f"(expected sign {expected_sign:+d})"
    )
    if not (abs(h_axis_corr) >= 0.5 and np.sign(h_axis_corr) == expected_sign):
        sys.exit(
            "Canonical orientation invariant violated: corr(h, axis) = "
            f"{h_axis_corr:+.4f} but expected sign = {expected_sign:+d}; "
            "h axis is not aligned with the metadata drive direction"
        )

if residual_recentre:
    nominal_R = diameter / 2.0
    circumference = np.pi * diameter
    h_vals = df_point_cloud['h'].to_numpy()
    r_vals = df_point_cloud['r'].to_numpy()
    phi_vals = df_point_cloud['theta'].to_numpy() / circumference * 2 * np.pi

    span = h_vals.max() - h_vals.min()
    n_bins = max(int(round(span / recentre_bin_size)), 4)
    edges = np.linspace(h_vals.min(), h_vals.max(), n_bins + 1)
    bin_centers = 0.5 * (edges[:-1] + edges[1:])

    r0_fit = np.full(n_bins, np.nan)
    a_fit = np.full(n_bins, np.nan)
    b_fit = np.full(n_bins, np.nan)
    for i in range(n_bins):
        m = (
            (h_vals >= edges[i]) & (h_vals < edges[i + 1])
            & (np.abs(r_vals - nominal_R) < recentre_r_tolerance)
        )
        if m.sum() < recentre_min_bin_points:
            continue
        A = np.column_stack((np.ones(m.sum()), np.cos(phi_vals[m]), np.sin(phi_vals[m])))
        coef, *_ = np.linalg.lstsq(A, r_vals[m], rcond=None)
                                                                             
        res = r_vals[m] - A @ coef
        w = np.abs(res) < 3 * np.median(np.abs(res)) + 1e-9
        if w.sum() >= recentre_min_bin_points // 2:
            coef, *_ = np.linalg.lstsq(A[w], r_vals[m][w], rcond=None)
        r0_fit[i], a_fit[i], b_fit[i] = coef

    ok = ~np.isnan(a_fit)
    if ok.sum() >= 2:
        a_i = np.interp(h_vals, bin_centers[ok], a_fit[ok])
        b_i = np.interp(h_vals, bin_centers[ok], b_fit[ok])
        r0_i = np.interp(h_vals, bin_centers[ok], r0_fit[ok])
        df_point_cloud['r'] = (
            r_vals - (a_i * np.cos(phi_vals) + b_i * np.sin(phi_vals)) - (r0_i - nominal_R)
        )
        offsets_cm = np.hypot(a_fit[ok], b_fit[ok]) * 100
        print(
            f"Residual recentre: {ok.sum()}/{n_bins} bins fitted, "
            f"centre offset removed max={offsets_cm.max():.1f}cm median={np.median(offsets_cm):.1f}cm"
        )
    else:
        print("Residual recentre skipped: not enough populated axial bins")

df_point_cloud.to_csv(paths["unwrapped_csv"],index=False)
                                                                   
import numpy as np


df_point_cloud.to_csv(paths["unwrapped_csv"], index=False)
save_state(paths["state"], {
    "df_point_cloud": df_point_cloud,
    "ring_count": ring_count,
    "resolution": 0.005,
})
print(f"Upfolding complete -> {paths['unwrapped_csv']}")

