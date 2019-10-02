# -- using OCV remove small nonzero clusrters
# drop noisy (blurry) images from dataset at all
# align color of remaining images somehow

import open3d as o3d
import cv2
import copy
import numpy as np

# import the necessary packages
from sklearn.cluster import MiniBatchKMeans
from tqdm import tqdm

from matplotlib import pyplot as plt
import sys, os
from time import time

sys.path.append("../utils")
from object_reconstruction_config import get_config

from file import get_file_list, make_clean_folder

def display_inlier_outlier(cloud, ind):
    # TODO for pointcloud clustering
    inlier_cloud = cloud.select_down_sample(ind)
    outlier_cloud = cloud.select_down_sample(ind, invert=True)

    print("Showing outliers (red) and inliers (gray): ")
    outlier_cloud.paint_uniform_color([1, 0, 0])
    inlier_cloud.paint_uniform_color([0.5, 0.5, 0.5])
    o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud])

# returns list of masks, all exept of largest contour blob is ignored
def make_masks_from_countures(depth_images_filenames):
    depth_images = [cv2.imread(fname, cv2.CV_8UC1)
                    for fname in depth_images_filenames]
    depth_preprocessed = [ cv2.GaussianBlur(im, (5, 5), 5)
                           for im in depth_images ]

    # other approaches for thresholding https://docs.opencv.org/master/d7/d4d/tutorial_py_thresholding.html#gsc.tab=0
    binary_masks = [(cv2.threshold(d, 0, 255, cv2.THRESH_OTSU))[1]
                     for d in depth_preprocessed]

    countours = [(cv2.findContours(bm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE))[0]
                  for bm in binary_masks]
    largest_contour = [max(contours_list, key=lambda x: cv2.contourArea(x))
                       for contours_list in countours]
    masks = [ np.zeros_like(dp_im)
              for dp_im in depth_images]
    for i, mask in enumerate(masks):
        cv2.drawContours(mask, [largest_contour[i]], -1, (255), cv2.FILLED)
    return masks

def make_masks_from_countures_for_loop(depth_images_filenames):
    masks = []
    for fname in depth_images_filenames:
        depth_image = cv2.imread(fname, cv2.CV_8UC1)
        depth_preprocessed = cv2.GaussianBlur(depth_image, (7, 7), 2)
        _, binary_mask = cv2.threshold(depth_preprocessed, 0, 255, cv2.THRESH_OTSU)
        contours = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        largest_contour = [
            max(contours[0], key=lambda x: cv2.contourArea(x))
        ]
        mask = np.zeros_like(depth_image)
        cv2.drawContours(mask, largest_contour, -1, (255), cv2.FILLED)
        masks.append(mask)
    return masks


def filter_pointcloud(depth_image_path, color_image_path, config=None, debug_mode = False):
    # TODO try adding RGBD preprocessing to this stage instead of processing integrated image
    if config is None:
        config = {"": ""}
    rgbd_images = []
    first = False
    for i in range( 1 ):
        print(os.path.join(depth_image_path[i]))
        depth = o3d.io.read_image(os.path.join(depth_image_path[i]))
        depth_images.append(depth)
        color = o3d.io.read_image(os.path.join(color_image_path[i]))
        color_images.append(color)
        rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
            color, depth, convert_rgb_to_intensity=False)

        if debug_mode and first:
            first = False
            pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
                rgbd_image,
                o3d.camera.PinholeCameraIntrinsic(camera_intrinsics))
            o3d.visualization.draw_geometries([pcd])

        rgbd_images.append(rgbd_image)
    return rgbd_images




# idea to expect that all artifacts will have the same color and therefore we can drop them out
def color_based_clustering_masks(image_filename, color_clustering_config, debug_mode = False):
    # from https://www.pyimagesearch.com/2014/07/07/color-quantization-opencv-using-k-means-clustering/
    image = cv2.imread(image_filename)
    (h, w) = image.shape[:2]

    # convert the image from the RGB color space to the L*a*b*
    # color space -- since we will be clustering using k-means
    # which is based on the euclidean distance, we'll use the
    # L*a*b* color space where the euclidean distance implies
    # perceptual meaning
    image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # reshape the image into a feature vector so that k-means
    # can be applied
    image = image.reshape((image.shape[0] * image.shape[1], 3))

    # apply k-means using the specified number of clusters and
    # then create the quantized image based on the predictions

    clt = MiniBatchKMeans(n_clusters=color_clustering_config['n_clusters'])
    labels = clt.fit_predict(image)
    unique, counts = np.unique(labels, return_counts=True)
    cluster_sizes = dict(zip(unique, counts))

    biggest_cluster_index, biggest_cluster_n_elements = max(cluster_sizes.items(), key= lambda pair: pair[1])
    masking = np.array((labels == biggest_cluster_index), dtype=np.uint8)
    _, mask = cv2.threshold(masking, 0, 255, cv2.THRESH_BINARY_INV)
    masking = mask.flatten()
    masking = masking.reshape((h, w))

    masking = cv2.GaussianBlur(masking, (5, 5), 5) # todo tune this place
    contours, _ = cv2.findContours(masking, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    cont_len_thresh = color_clustering_config['blob_contour_min_length']
    filtered_controus = [ contour for contour in contours
                          if cv2.contourArea(contour) > cont_len_thresh ]

    masking_filtered = np.zeros_like(masking)
    cv2.drawContours(masking_filtered, filtered_controus, -1, (255), cv2.FILLED)

    if debug_mode:
        masking = np.zeros_like(masking)
        cv2.drawContours(masking, contours, -1, (255), cv2.FILLED)

        print("Largest cluster Index : [{}], has_points: [{}] "
              .format(biggest_cluster_index, biggest_cluster_n_elements))

        # assume that max size cluster is the background
        quant = clt.cluster_centers_.astype("uint8")[labels]
        # quant_masks = clt.cluster_centers_.astype("uint8")[mask]

        print("labels shape: [{}]".format(labels.shape))

        print("Shapes after clusteting :")
        print("mask : [{}]".format(masking.shape))
        print("quantized image : [{}]".format(masking.shape))
        print()

        # reshape the feature vectors to images
        quant = quant.reshape((h, w, 3))
        image = image.reshape((h, w, 3))

        print("Reshaped back to pictures :")
        print("mask : [{}]".format(masking.shape))
        print("quantized image : [{}]".format(masking.shape))
        print()


        # convert from L*a*b* to RGB
        quant = cv2.cvtColor(quant, cv2.COLOR_LAB2BGR)
        image = cv2.cvtColor(image, cv2.COLOR_LAB2BGR)

        # display the images and wait for a keypress
        cv2.imshow("image", np.hstack([image,
                                       quant,
                                       cv2.cvtColor(masking, cv2.COLOR_GRAY2BGR)
                                       ]))
        cv2.waitKey(0)
    return masking_filtered

DEFAULT_CONFIFG_FILENAME = '../../cfg/reconstruction/default/preprocessing_raw_images.json'

def list_dataset_files(config):
    input_color_path = os.path.join(config['path_dataset'], config['color_dir'])
    input_depth_path = os.path.join(config['path_dataset'], config['depth_dir'])

    assert os.path.exists(config['path_dataset']) and \
           os.path.exists(input_color_path) and \
           os.path.exists(input_depth_path), \
        "Attempt to read dataset failed"

    depth_im_filenames = get_file_list(input_depth_path,
                                     extension=".png")
    color_im_filenames = get_file_list(input_color_path,
                                     extension=".jpg")

    assert (len(depth_im_filenames) == len(color_im_filenames)), \
        "Expected equal number of depth and rgb images"

    return color_im_filenames, depth_im_filenames

if __name__ == "__main__":

    config = get_config(DEFAULT_CONFIFG_FILENAME)
    debug_mode = config['debug']
    if debug_mode:
        o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)

    output_color_path = os.path.join(config['path_dataset'], config['color_result_dir'])
    output_depth_path = os.path.join(config['path_dataset'], config['depth_result_dir'])

    make_clean_folder(output_color_path)
    make_clean_folder(output_depth_path)

    camera_intrinsics = o3d.io.read_pinhole_camera_intrinsic(config['path_intrinsic'])

    input_rgb_images_files, input_depth_images_files = list_dataset_files(config)

    if not config['process_all_images']:
        input_rgb_images_files = input_rgb_images_files[config['dataset_range'][0]:config['dataset_range'][1]]
        input_depth_images_files = input_depth_images_files[config['dataset_range'][0]:config['dataset_range'][1]]

    first = True

    # blob_detectot = cv2.SimpleBlobDetector()
    # TODO try using blob detection

    print("Start computing masks")

    start_time = time()

    masks = []
    if config['color_clusters_thresholding']:

        color_clustering_config = config['threshold_colored_clusters']

        if config["python_multi_threading"]:
            from joblib import Parallel, delayed
            import multiprocessing
            MAX_THREAD = min(multiprocessing.cpu_count(),
                             max(len(input_rgb_images_files), 1))
            print("[Running in [{}] threads mode]".format(MAX_THREAD))

            results = Parallel(n_jobs=MAX_THREAD)(delayed(
                color_based_clustering_masks)(col_im_path, color_clustering_config)
                                                  for col_im_path in tqdm(input_rgb_images_files))
            masks.extend(results)
        else:
            print("[Running in single thread mode]")
            for col_im_path in tqdm(input_rgb_images_files):
                masks.append(color_based_clustering_masks(
                    col_im_path,
                    color_clustering_config,
                    debug_mode=debug_mode
                )
                )

    elif config['blobs_border_len_thresholding']:
        print("blobs_border_len_thresholding")
        masks = make_masks_from_countures(input_depth_images_files)


    print("End computing masks {}".format(time() - start_time))
    depth_images = [cv2.imread(fname, cv2.IMREAD_ANYDEPTH) for fname in input_depth_images_files]
    color_images = [cv2.imread(fname,cv2.COLOR_BGR2RGB) for fname in input_rgb_images_files]

    print("Applying mask to depth")
    masked_depth_images = [
        cv2.bitwise_and(im, im, mask=mask)
        for im, mask in tqdm(zip(depth_images, masks))
    ]

    print("Applying mask to color")
    masked_color_images = [
        cv2.bitwise_and(im, im, mask=mask)
        for im, mask in tqdm(zip(color_images, masks))
    ]

    if config['show_all_results']:
        for mask in masked_color_images:
            plt.imshow(mask)
            plt.show()

    print("started writing results")
    for i, (rgb, dpth) in enumerate(zip(masked_color_images, masked_depth_images)):
        cv2.imwrite(os.path.join(output_depth_path, "depth%06d.png" % i), dpth)
        cv2.imwrite(os.path.join(output_color_path, "rgb%06d.png" % i), rgb)
    print("finished writing results")

