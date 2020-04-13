# object_3d_reconstruction
Demo on object reconstruction using Open3D pipeline for the environment reconstruction 

Object reconstruction pipeline for Consumer Depth Cameras
 
### Introduction
Selected technology:

Open3D library by Intel labs. Open3D project is similar to the famous OpenCV, accepts the opensource contribution.
 Now is in a stage of active development, but the current version (0.8.0) provides decent useful functionality to work with. 
 This project proposes a version of 3D environment reconstruction pipeline as a use-case example for this their lib.
  Whereas we alter it to use for reconstruction of an object instead of the environment.

---

## How to use

1. Clone this project code using following:
```bash
git clone --recurse-submodules https://github.com/SoftServeSAG/3d_reconstruction
``` 
1. Install required libraries for python.
1. Download sample dataset using script from /datasets or register own data. # TODO add support for data collection
1. Run pipeline:
```bash
cd <project_git_repo>/src
python launch_object_reconstruction.py --config <full_cfg_filename>.json
```

---
### Installation and deployment
#### Easy way:
As there are version of open3d available from standard package management systems as pip or conda you can just run
```bash
pip install open3d
```
but for new features the best is to compile it from sources published on [the Open3D project GitHub page](https://github.com/intel-isl/Open3D) . Following [compiling instructions](http://www.open3d.org/docs/release/compilation.html).
Open3D repo version is available here as module.

- TODO : add detailed guide, mention CUDA version


## Files content
- /**cfg** : config files. We are trying not to use hardcoded parameters in scripts.
    - /cfg/**camera_presets** : files with settings (presets) for the cameras to use in registration part (#TODO add description and explain)
- /**Open3D** : subrepo Open3D should be placed linked into the main directory of this repo. If you want to use another place, please use symlinks.
- /**srs** 
    - /srs/**scripts** : scripts related to Object 3D reconstruction
      - /srs/scripts/**run_object_reconstruction.py** : entry point for the whole pipeline
      - /src/scripts/**<other_scripts_names>** : slave scripts for processing stages and features
    - /src/**utils** : general-purpose scripts for work with filesystem and plumbing for main pipeline scripts
- /**datasets** : link to directories with data and where processed results are stored by default
   the structure is similar to used by Open3D:
   - /datasets/<dataset_name>/**[color | rgb | image ]** -- directory for RGB images, naming should contain a valid index of fixed length to provide absolute ordering when sorted in lexicographical order:
   
   
```jaml
 Ok: {... 000008.jpg, 000009.jpg, 000010.jpg } 

 Wrong: { ... 8.jpg, 9.jpg, 10.jpg (sorted will be: 1.jpg, 10.jpg, 2.jpg ... ) }
```
   
- /datasets/<dataset_name>/**depth** : Storing depth images. Format is uint16. Values mean absolute metric distance in proportion 1000:1 -- 1000 units = 1m distance, therefore 1 utit = 1 mm.
- /datasets/<dataset_name>/**fragnents** : intermediate point cloud files and metadata..
- /datasets/<dataset_name>/**scene** :  results of the registration process: mesh.ply file - 3D mesh, other artifacts like a log with camera trajectory and etc. metadata... #TODO maybe change "scene" to an "object" or so?
- /datasets/<dataset_name>/**logs** :  directory for stroring expreiment runtime data a.e. execution time and configuration used
- /datasets/<dataset_name>/**camera_intrinsic**.json : a conventional place to store the file with registering camera parameters. (#TODO add to gitWiki about it)
- /datasets/<dataset_name>/**<_some_directory_name_with_suffix_>** : used to store results of preprocessing not to conflict with original filenames. 
- /datasets/**<dataset_name>_downloader.sh** : scripts for downloading samples [#TODO provide example, now only for partners (private before release)]

- /**requirements.txt** : file with required packages for python listed.
    
   ```bash
    $ pip install -r requirements.txt 
  ```


### Config policy
- TODO : write about 

--- 


## Stages of the reconstruction process
- Registration of a dataset

- (Optional) registered images preprocessing
    - depth and color images pairwise alignment
    - removing blurry images (#todo)
    - cropping background (#todo (greenscreen version))
    - removing secondary objects and artifacts to leave single object on image (done)

- color + depth --> integrated pointcloud
    - Refinement of obtained point clouds.
    - Filtering the intermediate point cloud.
    - Matching point clouds to produce a final mash.

- Filtering and postprocessing the resulting mash.
- Colormap optimization to achieve better texturing.


---
## Registration

   Generally used reconstruction pipeline proposed by Open3D is oriented on the setting with the static environment and moving camera. But in this case, we have a flaw -- hand-captured images suffer from lack of stabilization while moving around with tripod taking pictures frame-by-frame is exhausting. Capturing from the video also require smooth camera operating. Fast jerky moves between frames can cause malignant artifacts in a resulting model or even fail the whole dataset process.

When trying to apply this method to the reconstruction of the moving object, we face the problem of frame-to-frame matching and tracking failure.

Here we modeled case when we reconstructed the dynamical object with algorithm serving for the static object reconstruction only by removing its surrounding environment from the observation.

Issues aimed: reconstruction of a small object in a large environment could suffer as background matching priority could result in ignorance of flaws on the object surface.
Perform recording of good data with hand-held RGB-D camera is tricky but possible using proposed procedures.

#### Registration using absorbing material.
- RGBD cameras share common principle in work.
- We used its flaws in our favor.
- As such case is far from prescribed usage pattern -- it has lots of places when the process can go wrong:
 -- distance span
 -- visible part of the environment captured ruins presumption that target object is the world itself
 -- a number of artifacts are too hight and result in misalignment of resulting point clouds
#### Registration using familiar greenscreen.
 - TODO
 
## RGB-D cameras overview and deployment tips
 - RealSense D415
 - RealSense SR340
 - KinectV2
 - RealSense R200
 
## Preprocessing images

- ### TODO add images representing effect
- Cleaning outlier blobs:

    In the process of reconstruction using "invisible material" reconstruction does not require filtering background and preprocessing suppose to be omitted. But as a real-world working environment is always imperfect, due to lighting conditions, using the material, its angle, and wrinkles some parts of it are occasionally captured. Those non-informative artifacts harm reconstruction pipeline as if they belong to reconstruction fragments they can make the resulting matching impossible.
    
    As background generally clearly distinguishable from the object itself we can manage it with a pretty straightforward pipeline of preprocessing methods. 

#### Filtering registration artifacts:
1. **Based on the length of a blob (spot) contour:**
This approach is the fastest.

   1. Load depth image data in uint16 format
   1. Using thresholding create a mask which will contain the object of interest together with all false registrations
   1. Apply some blur (used Gaussian) to make this mask smoother and filter noisy edges 
   1. Compute length of each mask contour.
   1. Leave only one with maximum length (assume that reconstruction target is effectively the biggest one blob captured and all other are noises and artifacts)
   1. Use this mask to drop other elements from color and depth images.

References:
- [Loading images](https://stackoverflow.com/questions/10969585/opencv-reading-a-16-bit-grayscale-image)
- [Blurring](https://www.opencv-srf.com/2018/03/gaussian-blur.html)
- [Thresholding](https://docs.opencv.org/master/d7/d4d/tutorial_py_thresholding.html#gsc.tab=0)
- [Contour calculation](https://docs.opencv.org/master/d4/d73/tutorial_py_contours_begin.html#gsc.tab=0)

2. The K-means clustering for image colors.

   1. Load colored images
   1. Transform them from the RBG domain to other, a.e. LaB domain, where the euclidian distance in the colorspace corresponds to perceptual meaning.
   1. Using the k-means algorithm to cluster point by color into several separate clusters.
        
        _When we use a black light-absorbing canvas background, the regions where the absorption is good and the image contains 0 as color values. Black parts of the canvas which were registered overall tend to be clustered together with those parts, then with pixels representing target object itself._
   1. Select all the pixels except the biggest one (which is presumably background and noise).
   1. Apply some blurring to make the edges smooth.
   1. Take blobs borders via selection, only the outer border.
   1. Use space within those borders as the mask for selection.

References:
- [K-means clustering](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)
- [Colorspace transformation](https://www.learnopencv.com/color-spaces-in-opencv-cpp-python/)
- [Blurring](https://docs.opencv.org/2.4/doc/tutorials/imgproc/gausian_median_blur_bilateral_filter/gausian_median_blur_bilateral_filter.html)
- [Select outermost borders](https://docs.opencv.org/3.4/d9/d8b/tutorial_py_contours_hierarchy.html)

3. Based on Blob-detector - __Not implemented__
4. Using RGB-D pointcloud - __Not implemented__

#### Improve balance of colour:
- TODO

#### Drop bad frames:
- TODO

#### Reduce size of raw pictures by cropping

---

## Reconstruction object from images
Here we mostly rely on pipeline proposed by Open3D specifying only config files (#todo fragments postprocessing hypotheisis)

---

## Filtering and postprocessing mash
 #### Outliers removal
 - TODO
 #### DBSCAN clustering 
 - TODO
---

## Colormap optimisation
- TODO
---
