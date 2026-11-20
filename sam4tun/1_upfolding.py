#!/usr/bin/env python3
import sys
import os
import matplotlib
matplotlib.use('Agg')
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
from helpers.design_blueprint import load_design_blueprint
from helpers.pipeline_io import ensure_dir
from helpers.pipeline_state import save_state
tunnel_id = sys.argv[1]
paths = ensure_dir(tunnel_id)
import numpy as np
import pandas as pd
import os
_SAM4TUN_ROOT = os.path.dirname(os.path.abspath(__file__))
_DATA_ROOT = os.path.join(_SAM4TUN_ROOT, 'data')
_MONOLITH_DIR = os.path.join(_DATA_ROOT, 'monolith')
os.makedirs(_MONOLITH_DIR, exist_ok=True)

def _out(name: str) -> str:
    return os.path.join(_MONOLITH_DIR, name)
blueprint = load_design_blueprint()
diameter = float(blueprint['inner_diameter_m'])
ring_length_m = float(blueprint['ring_length_m'])
design_ring_count = int(blueprint['ring_count'])
drive_xy = np.asarray(blueprint['orientation_xy'], dtype=float)
print(f"Design blueprint subset={blueprint['subset_id']}: diameter={diameter} ring_length={ring_length_m} ring_count={design_ring_count} orientation=({drive_xy[0]:+.6f},{drive_xy[1]:+.6f})")
_input_override = (os.environ.get('PROXY4TUN_INPUT_TXT') or '').strip()
_input_txt = _input_override or os.path.join(_DATA_ROOT, 'sample.txt')
point_cloud_data = np.loadtxt(_input_txt, usecols=(0, 1, 2, 3))
print(f'Input point cloud: {_input_txt}')
print(point_cloud_data.shape)
points_xyz = point_cloud_data[:, :3]
intensity = point_cloud_data[:, 3]
df_point_cloud = pd.DataFrame({'x': points_xyz[:, 0], 'y': points_xyz[:, 1], 'z': points_xyz[:, 2], 'intensity': intensity})
df_point_cloud.head()
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon
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
axis_xy = np.asarray(center2 - center1, dtype=float)
if float(np.dot(axis_xy, drive_xy)) < 0:
    center1, center2 = (center2, center1)
vector = center2 - center1
print(vector)
import matplotlib.pyplot as plt
plt.figure(figsize=(8, 8))
sample_size = 10000
indices = np.random.choice(len(points_2d_xoy), size=sample_size, replace=False)
sampled_points = points_2d_xoy[indices]
plt.scatter(sampled_points[:, 0], sampled_points[:, 1], s=1, c='blue', label='Projected Points')
for simplex in convex_hull.simplices:
    plt.plot(points_2d_xoy[simplex, 0], points_2d_xoy[simplex, 1], 'k-')
rect_x, rect_y = zip(*np.array(min_bounding_rect.exterior.coords))
plt.plot(rect_x, rect_y, 'r-', label='Minimum Bounding Rectangle')
plt.plot(center1[0], center1[1], 'go', label='Center 1 of Short Edge')
plt.plot(center2[0], center2[1], 'mo', label='Center 2 of Short Edge')
plt.arrow(center1[0], center1[1], vector[0], vector[1], head_width=1, head_length=1, fc='green', ec='green', label='Direction Vector')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Projected Point Cloud and Bounding Rectangle')
plt.legend()
plt.axis('equal')
plt.grid(True)
plt.savefig(os.path.join(os.path.dirname(paths['state']), 'projected_point_cloud_bbox.png'), dpi=150, bbox_inches='tight')
import numpy as np
import math
from tqdm.notebook import tqdm

def generate_slicing_planes_point_cloud(center1, center2, points_xyz, delta, ring_count, ring_length):
    l = np.linalg.norm(center2[:2] - center1[:2])
    implied_n = round(l / ring_length) if ring_length > 0 else ring_count
    optimal_n = int(ring_count)
    if implied_n != optimal_n:
        print(f'Design ring_count={optimal_n} used; span/ring_length implies {implied_n} (span={l:.3f}m ring_length={ring_length})')
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
            segment_length = first_distance + i * (last_distance - first_distance) / (optimal_n - 1)
        point_on_plane = center1 + segment_length / total_distance * (center2 - center1)
        points_on_plane.append(point_on_plane)
        origin.append(np.append(point_on_plane, 0))
        normal_vector = np.append(direction, 0)
        d = -np.dot(normal_vector[:2], point_on_plane)
        plane = np.append(normal_vector, d)
        planes.append(plane)
    slicing_cloud = []
    Delta = delta
    points_xyz = np.asarray(points_xyz)
    for plane in tqdm(planes, desc='Processing planes'):
        a, b, c, d = plane
        Wr = a * points_xyz[:, 0] + b * points_xyz[:, 1] + c * points_xyz[:, 2] + d - Delta
        Wl = a * points_xyz[:, 0] + b * points_xyz[:, 1] + c * points_xyz[:, 2] + d + Delta
        mask = Wr * Wl <= 0
        slicing_cloud.append(points_xyz[mask])
    return (origin, planes, slicing_cloud)
delta = 0.005
origin, planes, slicing_cloud = generate_slicing_planes_point_cloud(center1, center2, points_xyz, delta, design_ring_count, ring_length_m)
print(f'Number of sliced clouds: {len(slicing_cloud)}')
ring_count = len(slicing_cloud)
if ring_count != design_ring_count:
    raise SystemExit(f'slice count {ring_count} != design ring_count {design_ring_count}')
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
for points in point2ds:
    y_max = max((point[1] for point in points))
    filtered_points = [point for point in points if abs(point[1] - y_max) <= 4.5]
    filtered_point2ds.append(filtered_points)
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
plt.savefig(os.path.join(os.path.dirname(paths['state']), 'slice_point_cloud_2d.png'), dpi=150, bbox_inches='tight')
import cv2
import random
import time

class RANSAC:

    def __init__(self, data, threshold, P, S, N):
        self.point_data = data
        self.error_threshold = threshold
        self.N = N
        self.S = S
        self.P = P
        self.max_inliers = len(data) * S
        self.items = 999
        self.count = 0
        self.best_model = ((0, 0), (1e-06, 1e-06), 0)

    def random_sampling(self, n):
        return np.asarray(random.sample(list(self.point_data), n))

    def Geometric2Conic(self, ellipse):
        (x0, y0), (bb, aa), phi_b_deg = ellipse
        a, b = (aa / 2, bb / 2)
        phi_b_rad = np.radians(phi_b_deg)
        ax, ay = (-np.sin(phi_b_rad), np.cos(phi_b_rad))
        a2, b2 = (a * a, b * b)
        if a2 > 0 and b2 > 0:
            A = ax * ax / a2 + ay * ay / b2
            B = 2 * ax * ay / a2 - 2 * ax * ay / b2
            C = ay * ay / a2 + ax * ax / b2
            D = (-2 * ax * ay * y0 - 2 * ax * ax * x0) / a2 + (2 * ax * ay * y0 - 2 * ay * ay * x0) / b2
            E = (-2 * ax * ay * x0 - 2 * ay * ay * y0) / a2 + (2 * ax * ay * x0 - 2 * ax * ax * y0) / b2
            F = (2 * ax * ay * x0 * y0 + ax * ax * x0 * x0 + ay * ay * y0 * y0) / a2 + (-2 * ax * ay * x0 * y0 + ay * ay * x0 * x0 + ax * ax * y0 * y0) / b2 - 1
        else:
            A, B, C, D, E, F = (1, 0, 1, 0, 0, -1e-06)
        return np.array([A, B, C, D, E, F])

    def eval_model(self, ellipse):
        a, b, c, d, e, f = self.Geometric2Conic(ellipse)
        E = 4 * a * c - b * b
        if E <= 0:
            return (0, np.array([]))
        (x, y), (LAxis, SAxis), Angle = ellipse
        LAxis, SAxis = (LAxis / 2, SAxis / 2)
        if SAxis > LAxis:
            SAxis, LAxis = (LAxis, SAxis)
        Axis = math.sqrt(LAxis ** 2 - SAxis ** 2)
        f1_x = x - Axis * math.cos(math.radians(Angle))
        f1_y = y - Axis * math.sin(math.radians(Angle))
        f2_x = x + Axis * math.cos(math.radians(Angle))
        f2_y = y + Axis * math.sin(math.radians(Angle))
        f1, f2 = (np.array([f1_x, f1_y]), np.array([f2_x, f2_y]))
        f1_distance = np.sum((self.point_data - f1) ** 2, axis=1)
        f2_distance = np.sum((self.point_data - f2) ** 2, axis=1)
        all_distance = np.sqrt(f1_distance) + np.sqrt(f2_distance)
        Z = np.abs(2 * LAxis - all_distance)
        delta = np.sqrt(np.mean((Z - np.mean(Z)) ** 2))
        inliers = np.where(Z < 0.8 * delta)[0]
        inlier_points = self.point_data[inliers]
        return (len(inlier_points), inlier_points)

    def execute_ransac(self):
        start_time = time.time()
        inliers_set = np.empty((0, 2), dtype=np.float32)
        iterations = 0
        max_iterations = max(1000, int(self.items) if math.isfinite(self.items) else 1000)
        while iterations < max_iterations and math.ceil(self.items):
            iterations += 1
            if len(self.point_data) < self.N:
                break
            select_points = self.random_sampling(self.N)
            select_points_list = [(point[0], point[1]) for point in select_points]
            ellipse = cv2.fitEllipse(np.array(select_points_list, dtype=np.float32))
            inliers_count, inliers_set_raw = self.eval_model(ellipse)
            inliers_set = np.array([tuple(point) for point in inliers_set_raw], dtype=np.float32)
            if inliers_count > self.count and inliers_count >= 5:
                self.count = inliers_count
                self.best_model = cv2.fitEllipse(inliers_set)
                if self.count > self.max_inliers:
                    print('Inlier ratio: ', self.count / len(self.point_data))
                    break
                ratio = inliers_count / len(self.point_data)
                if 0.0 < ratio < 1.0:
                    self.items = math.log(1 - self.P) / math.log(1 - ratio ** self.N)
        return (self.best_model, inliers_set)
X_center = []
Y_center = []
LAxis_sets = []
SAxis_sets = []
Angle_sets = []
in_sets = []
for i in range(len(slicing_cloud)):
    points_data = np.reshape(filtered_point2ds[i], (-1, 2))
    if len(points_data) < 5:
        print(f'Skip slice {i}: fewer than 5 edge points ({len(points_data)})')
        continue
    ransac = RANSAC(data=points_data, threshold=1.0, P=0.9, S=0.75, N=5)
    _, inliers_set = ransac.execute_ransac()
    if inliers_set is None or len(inliers_set) < 5:
        print(f'Skip slice {i}: RANSAC returned fewer than 5 inliers')
        continue
    points_data = np.reshape(inliers_set, (-1, 2))
    ransac = RANSAC(data=points_data, threshold=1.0, P=0.9, S=0.75, N=5)
    ellipse_params, _ = ransac.execute_ransac()
    if ellipse_params is None:
        print(f'Skip slice {i}: refined RANSAC produced no ellipse')
        continue
    (X, Y), (LAxis, SAxis), Angle = ellipse_params
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
ip1 = in_sets[i][:, 0]
ip2 = in_sets[i][:, 1]
ellipse = Ellipse(xy=(X_center[i], Y_center[i]), width=LAxis_sets[i], height=SAxis_sets[i], angle=Angle_sets[i], edgecolor='b', fc='None')
print(ellipse)
plt.figure('Draw')
plt.scatter(ip1, ip2, s=3, color='green')
plt.scatter(X_center[i], Y_center[i], color='red')
plt.gca().add_patch(ellipse)
plt.axis('equal')
plt.title('cross section - 2d points')
plt.grid(True)
plt.draw()

def get_3dcoordinates_from_plane(point2d, plane_params, origin):
    xp, yp = point2d
    A, B, C, D = plane_params
    x0, y0, z0 = origin
    N = np.array([A, B, C])
    N = N / np.linalg.norm(N)
    Vx = -B
    Vy = A
    Vz = 0
    V = np.array([Vx, Vy, Vz])
    V = V / np.linalg.norm(V)
    U = np.cross(N, V)
    U = U / np.linalg.norm(U)
    x = x0 + xp * V[0] + yp * U[0]
    y = y0 + xp * V[1] + yp * U[1]
    z = z0 + xp * V[2] + yp * U[2]
    return [x, y, z]
cps = []
for i in range(len(slicing_cloud)):
    point2d_cp = np.array([X_center[i], Y_center[i]])
    cp = get_3dcoordinates_from_plane(point2d_cp, planes[i], origin[i])
    cps.append(cp)
cps_arr = np.array(cps)
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
ax.set_box_aspect([1, 1, 1])
plt.savefig(os.path.join(os.path.dirname(paths['state']), 'ellipse_centres_3d.png'), dpi=150, bbox_inches='tight')
import numpy as np
from sklearn.linear_model import RANSACRegressor
from sklearn.preprocessing import PolynomialFeatures
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
t = np.arange(ring_count)
degree = 3
poly = PolynomialFeatures(degree)
t_poly = poly.fit_transform(t.reshape(-1, 1))
x_poly = t_poly
y_poly = t_poly
z_poly = t_poly
ransac_x = RANSACRegressor()
ransac_y = RANSACRegressor()
ransac_z = RANSACRegressor()
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
print('X parameters:', x_params)
print('Y parameters:', y_params)
print('Z parameters:', z_params)
t_extend = np.linspace(-2, ring_count + 1, 100)
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
plt.savefig(os.path.join(os.path.dirname(paths['state']), 'tunnel_centre_curve_3d.png'), dpi=150, bbox_inches='tight')
import numpy as np
from numba import njit, prange
import faiss
from joblib import Parallel, delayed
from tqdm.notebook import tqdm
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
def calculate_angle_with_direction(A, B, C):
    AB = B - A
    BC = C - B
    dot_product = np.dot(AB, BC)
    norm_AB = np.sqrt(np.dot(AB, AB))
    norm_BC = np.sqrt(np.dot(BC, BC))
    if norm_AB == 0 or norm_BC == 0:
        return (0.0, np.linalg.norm(AB))
    cos_angle = dot_product / (norm_AB * norm_BC)
    angle_radians = np.arccos(cos_angle)
    angle_degrees = angle_radians * (180.0 / np.pi)
    cross_product = np.cross(AB, BC)
    if cross_product[2] < 0:
        angle_degrees = 360 - angle_degrees
    return (angle_degrees, np.linalg.norm(AB))

@njit
def compute_C_points_and_arc_length(B_points, T_vectors, arc_lengths):
    C_points = np.empty_like(B_points)
    for i in range(B_points.shape[0]):
        B = B_points[i]
        T = T_vectors[i]
        lambda_ = -T[2] / (T[0] ** 2 + T[1] ** 2)
        C = B + lambda_ * np.array([T[0], T[1], 0]) + np.array([0, 0, 1])
        C_points[i] = C
        if i > 0:
            prev_B = B_points[i - 1]
            arc_lengths[i] = arc_lengths[i - 1] + np.linalg.norm(B - prev_B)
        else:
            arc_lengths[i] = 0.0
    return (C_points, arc_lengths)
num_samples = ring_count * 1210
t_samples = np.linspace(-20, ring_count + 20, num_samples)
B_points = curve_func(t_samples, x_params, y_params, z_params)
T_vectors = curve_deriv(t_samples, x_params, y_params, z_params)
arc_lengths = np.zeros(num_samples, dtype=np.float32)
C_points, arc_lengths = compute_C_points_and_arc_length(B_points, T_vectors, arc_lengths)
index = faiss.IndexFlatL2(3)
index.add(B_points)
start_time = time.time()
batch_size = 1000000

def process_batch(points_batch):
    _, idx_batch = index.search(points_batch, 1)
    results = []
    for i in range(points_batch.shape[0]):
        A = points_batch[i]
        idx = idx_batch[i][0]
        B = B_points[idx]
        C = C_points[idx]
        angle_ABC, distance_AB = calculate_angle_with_direction(A, B, C)
        arc_length_B = arc_lengths[idx]
        results.append((distance_AB, angle_ABC, arc_length_B))
    return results
num_batches = (len(points_xyz) + batch_size - 1) // batch_size
points_batches = np.array_split(points_xyz, num_batches)
cylindrical_coords_batches = Parallel(n_jobs=12)((delayed(process_batch)(batch) for batch in tqdm(points_batches, desc='Calculating cylindrical coordinates', total=len(points_batches))))
cylindrical_coords = []
for batch_result in cylindrical_coords_batches:
    cylindrical_coords.extend(batch_result)
end_time = time.time()
print(f'Total computation time: {end_time - start_time:.6f} seconds')
import pandas as pd
df_point_cloud['r'] = np.array(cylindrical_coords)[:, 0]
df_point_cloud['theta'] = np.array(cylindrical_coords)[:, 1] * (np.pi * diameter / 360)
df_point_cloud['h'] = np.array(cylindrical_coords)[:, 2]
df_point_cloud.head()
df_point_cloud.to_csv(paths['unwrapped_csv'], index=False)
import numpy as np
df_point_cloud.to_csv(paths['unwrapped_csv'], index=False)
save_state(paths['state'], {'df_point_cloud': df_point_cloud, 'ring_count': ring_count, 'resolution': 0.005})
print(f"Upfolding complete -> {paths['unwrapped_csv']}")
