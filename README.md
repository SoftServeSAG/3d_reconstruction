# object_3d_reconstruction
Demo on object reconstruction using Open3D pipeline for the environment reconstruction 

Object reconstruction pipeline for Consumer Depth Cameras
 
###Introduction
TODO

---


## Stages of reconstruction process
- Registration

- (Optional) registered images preprocessing
    - depth and color images pair alignment
    - removing blurry images (#todo)
    - cropping background (#todo (greenscreen version))
    - removing secondary objects and artifacts to leave single object on image (done)

- color + depth --> integrated pointcloud
    - Refinement of obtained pointclouds.
    - Filtering intermediate pointcloud.
    - Matching pointclouds to produce final mash.

- Filtering and postprocessing resulting mash.
- Colormap optimization to achieve better texturing.

---

## Registration

   Generaly used reconstruction pipeline proposed by OpneCV is oriented on the setting with static environment and moving camera, but in this case we have a flaw -- hand-captured images suffer from lack of stabilisation while moving around with tripod taking images frame-by-frame is exhausting. Capturing from video also require careful camera operating, because fast jerky moves between frames can cause unwishful artifacts in resulting model or even fail the whole dataset process.

As object of reconstruction has to be static usually we can't apply it to the reconstruction of the moving objects: there should be match of the observed state of reconstructing environment from frame to frame. 

Here we modelled case when we reconstructed the dynamical object with algorithm serving for the static object reconstruction only by removing its surrounding environment from the observation.

Issues solved : reconstruction of a small object in large environment could suffer as background matching priority could result in ignorance of flaws on the object surface.
Perform recording of good data with hand-held rgbd camera is tricky.


 1. Registration using absorbing material.
 - RGBD cameras share common principle in work.
 - We used its flaws in our favour.
 - As such case is far from prescribed usage pattern -- it has lots of places when process can go wrong:
  -- distance span
  -- visible part of environment captured ruins presumption that target object is the world itself
  -- number of artifacts is too hight and result in misalightnment of resulting pointclouds
 2. Registration using familiar greenscreen.
 TODO
 
## Preprocessing images

Cleaning outlier blobs:
<!--  <Show images with filtering and failcase without it> -->
    In process of reconstruction using "invisible material" reconstruction does not require filterign background and preprocessing generaly can be ommited. But as working environment always imperfect, due to lighting conditions, used material, its angle and wrinkles some parts of it are occasionaly captured. Those non-informative artifacts harm reconstruction pipeline as if they belong to reconstruction fragments they can make the resulting matching impossible.
    As background generally clearly distinguishable from the object itself we can manage it with pretty straitforward pipeline of preprocessing methods. 
    - Filtering registration artifacts
    - Improve balance of colour
    - Drop frames of bad quality

### Filtering registration artifacts:
- TODO: move it here from notes

### Improve balance of colour:
- TODO

### Drop bad frames:
- TODO

---

## Reconstruction object from images
- TODO
---

## Filtering and postprocessing mash
- TODO
---

## Colormap optimisation
- TODO
---

## Files content
- /cfg : config files. Try not to use hardcoded parameters in scripts.
- /scripts Object reconstruction scripts
- /Open3D : subrepo Open3D should be placed linked into the main directory of this repo. If you want to use another place, please use symlinks.
- /srs 
    - /srs/scripts : scripts related to Object 3D reconstruction
      - /srs/scripts/run_object_reconstruction.py : entry point for the whole pipeline
    - /src/utils : 
- /datasets link to directrories with data and where processed results are stored by default
   structure is the same as proposed by Open3D:
   - /datasets/<dataset_name>/[color | rgb | image ] -- directory for rgb images, naming should contain valid index of fixed length to provide absolute ordering when sorted in lexicographical orgder:
   
        Ok: {... 000008.jpg, 000009.jpg, 000010.jpg } 
      
      Wrong: { ... 8.jpg, 9.jpg, 10.jpg (sorted will be: 1.jpg, 10.jpg, 2.jpg ... ) }
    - /datasets/<dataset_name>/depth : Storing depth images. Format is uint16. Values mean absolute metric distance in proportion 1000:1 -- 1000 units = 1m distance, therefore 1 utit = 1 mm.
    - /datasets/<dataset_name>/fragnents : intermediate point cloud files and metadata..
    - /datasets/<dataset_name>/scene :  results of the registration process: mesh.ply file - 3D mesh, other artifacts like a log with camera trajectory and etc. metadata...
    - /datasets/<dataset_name>/camera_intrinsic.json : a conventional place to store the file with registering camera parameters. (#TODO add to gitWiki about it)
    - /datasets/<dataset_name>/<some_directory_name> : used to store results of preprocessing not to conflict with original filenames. 
    - /datasets/<dataset_name>_downloader.sh : scripts for downloading samples [#TODO provide example, now only for partners (private before release)]

- /requirements.txt : file with required packages for python.
    
   ``` $ pip install -r requirements.txt ```
