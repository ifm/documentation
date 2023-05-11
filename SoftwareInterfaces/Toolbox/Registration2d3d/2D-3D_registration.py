#############################################
# Copyright 2023-present ifm electronic, gmbh
# SPDX-License-Identifier: Apache-2.0
#############################################

# This file can be run interactively, section by section in sequential order:
# Sections are delimited by '#%%'
# Several editors including Spyder and vscode+python are equipped to run these cells
# by simply pressing shift-enter

#%%
import numpy as np
import cv2
import open3d as o3d
import matplotlib.pyplot as plt

from transforms import (
    intrinsic_projection,
    inverse_intrinsic_projection,
    translate,
    rotate_xyz,
    rectify,
)

from pathlib import Path
import os
from pprint import pprint
from datetime import datetime
from transforms import rotMat


#%%
USE_IFM_IVA_H5 = False
SHOW_OPEN3D = True

if USE_IFM_IVA_H5:
    # load data: ifm h5 data container - e.g. recording from ifm Vision Assistant
    import h5py

    # If multiple frames are available, then the first frame will be used.
    file_name_of_recording = "scene.h5"

    current_dir = Path(__file__).parent.resolve()

    # Unpack all data required to 2d3d registration
    hf1 = h5py.File(str(current_dir / file_name_of_recording), "r")
    rgb = hf1["streams"]["o3r_rgb_0"]
    tof = hf1["streams"]["o3r_tof_0"]

    jpg = rgb[0]["jpeg"]
    jpg = cv2.imdecode(jpg, cv2.IMREAD_UNCHANGED)
    jpg = cv2.cvtColor(jpg, cv2.COLOR_BGR2RGB)
    modelID2D = rgb[0]["intrinsicCalibModelID"]
    intrinsic2D = rgb[0]["intrinsicCalibModelParameters"]
    invIntrinsic2D = rgb[0]["invIntrinsicCalibModelParameters"]
    extrinsic2D = rgb[0]["extrinsicOpticToUserTrans"]
    extrinsic2D = np.append(extrinsic2D, rgb[0]["extrinsicOpticToUserRot"])

    dis = tof[0]["distance"]
    amp = tof[0]["amplitude"]
    modelID3D = tof[0]["intrinsicCalibModelID"]
    intrinsics3 = tof[0]["intrinsicCalibModelParameters"]
    inv_intrinsic3 = tof[0]["invIntrinsicCalibModelParameters"]
    extrinsic3D = tof[0]["extrinsicOpticToUserTrans"]
    extrinsic3D = np.append(extrinsic3D, tof[0]["extrinsicOpticToUserRot"])

    hf1.close()

else:
    # live data from connected o3r system...
    from ifm3dpy import O3R

    from collect_calibrations import PortCalibrationCollector
    from loop_to_collect_frame import FrameCollector

    # Define where the current camera-of-interest is plugged in and where VPU is
    IP_ADDR = "192.168.0.69"  # This is the default address
    PORT2D = 0
    PORT3D = 2

    o3r = O3R(IP_ADDR)
    current_VPU_state = o3r.get()

    # Collect specified calibration data from specified ports
    camera_ports = [PORT2D, PORT3D]
    port_handles = {
        port_n: PortCalibrationCollector(
            o3r, port_n, current_VPU_state["ports"][f"port{port_n}"]
        )
        for port_n in camera_ports
    }
    calibrations = {
        port_n: port_handle.calibrations for port_n, port_handle in port_handles.items()
    }
    for port_n, port_handle in calibrations.items():
        print(f"\nPort {port_n} calibrations:")
        pprint(calibrations)

    # Record sample frames for registration
    frame_collector = FrameCollector(o3r, ports=[0, 2])
    frame_collector.loop(timeout=10000)

    # Close any remaining opencv windows
    cv2.destroyAllWindows()

    # Unpack all data relevent to 2d3d registration
    most_recent_saved_buffers = frame_collector.saved_buffer_sets[-1]

    rgb = most_recent_saved_buffers[PORT2D]["rgb"]
    jpg = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
    modelID2D = calibrations[PORT2D]["intrinsic_calibration"][0]
    intrinsic2D = calibrations[PORT2D]["intrinsic_calibration"][1:]
    invIntrinsic2D = calibrations[PORT2D]["inverse_intrinsic_calibration"][1:]
    extrinsic2D = calibrations[PORT2D]["ext_optic_to_user"]

    tof = most_recent_saved_buffers[PORT3D]["dist"]
    dis = tof
    amp = most_recent_saved_buffers[PORT3D]["NAI"]
    modelID3D = calibrations[PORT3D]["intrinsic_calibration"][0]
    intrinsics3 = calibrations[PORT3D]["intrinsic_calibration"][1:]
    inv_intrinsic3 = calibrations[PORT3D]["inverse_intrinsic_calibration"][1:]
    extrinsic3D = calibrations[PORT3D]["ext_optic_to_user"]

    ts = datetime.now().strftime("%d.%m.%Y_%H.%M.%S")

#%%
# Review sample data using matplotlib

fig = plt.figure(1)
plt.clf()

plt.subplot(2, 2, 1)
plt.title("log(Amplitude) image")
plt.imshow(np.log10(amp + 0.001), cmap="gray", interpolation="none")
plt.colorbar()

plt.subplot(2, 2, 3)
plt.title("Distance image")
plt.imshow(dis, cmap="jet", interpolation="none")
plt.colorbar()

plt.subplot(1, 2, 2)
plt.title("RGB image")
plt.imshow(jpg, interpolation="none")

#%%
# Point cloud calculations

# calculate 3D unit vectors corresponding to each pixel of depth camera
ux, uy, uz = intrinsic_projection(modelID3D, intrinsics3, *tof.shape[::-1])

# multiply unit vectors by depth of corresponding pixel
x = (ux * dis).flatten()
y = (uy * dis).flatten()
z = (uz * dis).flatten()
valid = dis.flatten() > 0.05
print(f"{round(sum(valid)/x.size*100)}% valid pts")
for i, pt_valid in enumerate(valid):
    if not pt_valid:
        x[i] = y[i] = z[i] = 0.0

#%%
# Restructure point cloud as sequence of points
pcd_o3 = np.stack((x, y, z), axis=0)

#%%

# Transform from optical coordinate system to user coordinate system
pcd_u = translate(rotate_xyz(pcd_o3, *extrinsic3D[3:6]), *extrinsic3D[:3])

# Visualize point cloud using matplotlib
fig = plt.figure(1)
plt.clf()
ax = fig.add_subplot(projection="3d")
idx = pcd_o3[2, :] > 0  # plot only valid pixels
plt.plot(pcd_o3[0, idx], pcd_o3[1, idx], -pcd_o3[2, idx], ".", markersize=1)
plt.title("Point cloud")

#%%
# Visualize 3D-Pointcloud colored with log(amplitude)
# The amplitude image is good for visualizing the reflectivity of various materials
pointcloud = o3d.geometry.PointCloud()
pointcloud.points = o3d.utility.Vector3dVector(pcd_o3[:, valid].T)
colors = np.log10(amp + 0.001).flatten()
colors = (colors - np.min(colors)) / (np.max(colors) - np.min(colors))
colors = np.stack((colors, colors, colors), axis=1)
pointcloud.colors = o3d.utility.Vector3dVector(colors[valid])

# render 3D pointcloud
if SHOW_OPEN3D:
    o3d.visualization.draw_geometries(
        [pointcloud], window_name="Amplitude - Head coordinate system"
    )

#%%
# Do rectification of 3D amplitude image using intrinsic parameters
fig = plt.figure(1)
plt.clf()
im_rect = rectify(inv_intrinsic3, modelID3D, np.log10(amp + 0.001))

plt.subplot(1, 2, 1)
plt.imshow(np.log10(amp + 0.001))
plt.title("log(Amplitude)")
plt.subplot(1, 2, 2)
plt.imshow(im_rect)
plt.title("Rectified log(Amplitude)")
plt.show()

#%%
# Do rectification of 2D image using intrinsic parameters
fig = plt.figure(1)
plt.clf()

im_rect = rectify(invIntrinsic2D, modelID2D, jpg)

plt.subplot(1, 2, 1)
plt.imshow(jpg)
plt.title("Raw Color Im.")
plt.subplot(1, 2, 2)
plt.imshow(im_rect)
plt.title("Rectified Color Im.")
plt.show()

#%%
# Color each 3D point with it's corresponding 2D pixel

# convert to points in optics space
# reverse internalTransRot
r = np.array(extrinsic2D[3:6])
t = np.array(extrinsic2D[:3])

# pcd = rotate_zyx(translate(pcd,*t),*r)
pcd_o2 = rotMat(r).T.dot(pcd_u - np.array(t)[..., np.newaxis])

# Calculate 2D pixel coordinates for each 3D pixel
pixels = np.round(inverse_intrinsic_projection(pcd_o2, invIntrinsic2D, modelID2D))

# Get 2D jpg-color for each 3D-pixel
colors = np.zeros((len(pixels[0]), 3))  # shape is Nx3 (for open3d)
for i in range(len(colors)):
    idxX = int(pixels[1][i])
    idxY = int(pixels[0][i])
    # Ignore invalid values
    if idxY > 1279 or idxX > 799 or idxY < 0 or idxX < 0:
        colors[i, 0] = 126
        colors[i, 1] = 126
        colors[i, 2] = 126
    else:
        colors[i, 0] = jpg[idxX, idxY, 0]
        colors[i, 1] = jpg[idxX, idxY, 1]
        colors[i, 2] = jpg[idxX, idxY, 2]


# save results for later display using open3d
results_dir = Path(__file__).parent / "results"
if not results_dir.exists():
    os.mkdir(results_dir)
cam_sn = current_VPU_state["ports"][f"port{PORT3D}"]["info"]["partNumber"]

colored_pointcloud_valid = o3d.geometry.PointCloud()
colored_pointcloud_valid.points = o3d.utility.Vector3dVector(pcd_u[:, valid].T)
colored_pointcloud_valid.colors = o3d.utility.Vector3dVector(colors[valid] / 255)
dst_valid = str(results_dir / f"{ts}_{cam_sn}_{tof.shape[1]}x{tof.shape[0]}_valid_.pcd")
o3d.io.write_point_cloud(dst_valid, colored_pointcloud_valid, print_progress=True)
colored_pointcloud_all = o3d.geometry.PointCloud()
colored_pointcloud_all.points = o3d.utility.Vector3dVector(pcd_u.T)
colored_pointcloud_all.colors = o3d.utility.Vector3dVector(colors / 255)
dst_all = str(results_dir / f"{ts}_{cam_sn}_{tof.shape[1]}x{tof.shape[0]}_all_.pcd")
o3d.io.write_point_cloud(dst_all, colored_pointcloud_all, print_progress=True)

#%%
# review results
colored_pointcloud_valid = o3d.io.read_point_cloud(dst_valid)
print(colored_pointcloud_valid)
print(np.asarray(colored_pointcloud_valid.points))
if SHOW_OPEN3D:
    o3d.visualization.draw_geometries(
        [colored_pointcloud_valid], window_name=f"Colored points - {cam_sn} "
    )

# %%
# review samples or other results...
src_dir = Path(__file__).parent / "samples"
fname = "boxes_on_floor.pcd"
src = results_dir / fname
pcd = o3d.io.read_point_cloud(src)
print(pcd)
print(np.asarray(pcd.points))
if SHOW_OPEN3D:
    o3d.visualization.draw_geometries(
        [pcd], window_name="Colored points - Head coordinate system"
    )
