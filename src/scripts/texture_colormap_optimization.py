

import open3d as o3d
from open3d.open3d.camera import *
# from trajectory_io import *
import os, sys
import numpy as np
import argparse
import json
from Open3D.examples.Python.Advanced.trajectory_io import CameraPose

sys.path.append("../utils")

from object_reconstruction_config import get_config

from file import *

def posegraph_to_trajectory(posegraph, intrinsic, to_invert):
    inframe_posegraph = []

    for node in posegraph.nodes:
        pin_pars = PinholeCameraParameters()
        if to_invert:
            pin_pars.extrinsic = np.linalg.inv(node.pose)
        else:
            pin_pars.extrinsic = node.pose

        pin_pars.intrinsic = intrinsic
        inframe_posegraph.append(pin_pars)

    print(inframe_posegraph)

    pinhole_camera_trajectory = PinholeCameraTrajectory()
    pinhole_camera_trajectory.parameters = inframe_posegraph

    return pinhole_camera_trajectory


DEFAULT_CONFIFG_FILENAME = "../../cfg/reconstruction/default/colormap_optimization.json"

def get_trajectory(config):

    path = config['path_dataset']
    path_intrinsic = config['path_intrinsic']
    fragments_dir = config['fragments_dir']
    scene_dir = config['scene_dir']
    global_registration_trajectory_filename = config['global_registration_trajectory_filename']
    fragments_image_path = get_file_list(os.path.join(path, fragments_dir),
                                         extension=".json")
    fragments_image_path = filter(lambda x: "optimized" in x, fragments_image_path)
    # read posegraph
    # posegraph_path = os.path.join(path, fragments_dir, fragments_template.format("000"))
    # print(posegraph_path)
    # posegraph = o3d.io.read_pose_graph(posegraph_path)

    global_fragments_poses_file = os.path.join(path, scene_dir, global_registration_trajectory_filename)
    global_fragments_poses = o3d.io.read_pose_graph(global_fragments_poses_file)

    intrinsic = o3d.io.read_pinhole_camera_intrinsic(path_intrinsic)

    global_trajectories = posegraph_to_trajectory(global_fragments_poses, intrinsic, to_invert=False)

    # print(global_trajectories)
    pinhole_camera_trajectory_shifted = PinholeCameraTrajectory()

    camera_poses = []
    for single_fragment_path, global_pose_shift in zip(fragments_image_path, global_trajectories.parameters):
        local_posegraph = o3d.io.read_pose_graph(single_fragment_path)
        local_pinhole_cam_trajectory = posegraph_to_trajectory(local_posegraph, intrinsic, to_invert=False)
        for node in local_pinhole_cam_trajectory.parameters:
            # print(node.extrinsic)
            # print(global_pose_shift.extrinsic)
            pin_pars = PinholeCameraParameters()
            pin_pars.extrinsic = np.linalg.inv(global_pose_shift.extrinsic @ node.extrinsic)
            pin_pars.intrinsic = intrinsic
            camera_poses.append(pin_pars)

    pinhole_camera_trajectory_shifted.parameters = camera_poses  # don't know why but it can be only assigned, not appended one-by-one  (DK)
    return pinhole_camera_trajectory_shifted


def read_rgbd_images(config):
    debug_mode = config['debug']
    path = config['path_dataset']
    depth_dir = config['depth_dir']
    color_dir = config['color_dir']
    depth_image_path = get_file_list(os.path.join(path, depth_dir),
                                     extension=".png")
    color_image_path = get_file_list(os.path.join(path, color_dir),
                                     extension=".jpg")
    assert (len(depth_image_path) == len(color_image_path))

    rgbd_images = [o3d.geometry.RGBDImage.create_from_color_and_depth(
            o3d.io.read_image(color_im_fname), o3d.io.read_image(depth_im_fname), convert_rgb_to_intensity=False) for depth_im_fname, color_im_fname in zip (depth_image_path, color_image_path)]

    if debug_mode:
        camera_intrinsics = o3d.io.read_pinhole_camera_intrinsic(
            config["path_intrinsic"])
        pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
                    rgbd_images[0],
                    o3d.camera.PinholeCameraIntrinsic(camera_intrinsics))
        o3d.visualization.draw_geometries([pcd])

    return rgbd_images


def run_colormap_optimisarion(config):

    debug_mode = config['debug']
    if debug_mode:
        o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)

    path = config['path_dataset']
    store_results_dir = config['store_result_path']

    mesh_filename = os.path.join(path, config['mesh_file'])
    assert os.path.exists(mesh_filename), "mesh file [{}] failed to detect".format(mesh_filename)

    local_pinhole_cam_trajectory = get_trajectory(config)

    # OUR GOAL OBJECT
    mesh = o3d.io.read_triangle_mesh(mesh_filename)
    if debug_mode:
        o3d.visualization.draw_geometries([mesh])

    rgbd_images = read_rgbd_images(config=config)

    if not os.path.exists(os.path.join(path, store_results_dir)):
        os.mkdir(os.path.join(path, store_results_dir))

    option = o3d.color_map.ColorMapOptimizationOption()
    option.maximum_iteration = 0
    o3d.color_map.color_map_optimization(mesh, rgbd_images, local_pinhole_cam_trajectory, option)
    if debug_mode:
        o3d.visualization.draw_geometries([mesh])
    o3d.io.write_triangle_mesh(
        os.path.join(path, store_results_dir, "color_map_before_optimization.ply"), mesh)

    option = o3d.color_map.ColorMapOptimizationOption()
    option.maximum_iteration = config['max_iters']
    option.non_rigid_camera_coordinate = config['use_nonrigid']
    o3d.color_map.color_map_optimization(mesh, rgbd_images, local_pinhole_cam_trajectory, option)
    if debug_mode:
        o3d.visualization.draw_geometries([mesh])
    o3d.io.write_triangle_mesh(
        os.path.join(path, store_results_dir, "color_map_after_optimization_nonrigid.ply"), mesh)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Object reconstruction pipeline launcher")
    parser.add_argument("--config", help="path to the config file")
    args = parser.parse_args()

    if args.config is not None:
        config_filename = args.config
    else:
        config_filename = DEFAULT_CONFIFG_FILENAME

    config = get_config(config_filename)

    run_colormap_optimisarion(config)