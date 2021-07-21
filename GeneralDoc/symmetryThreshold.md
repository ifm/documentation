# Symmetry threshold
## Abstract

The symmetry threshold is used for filtering motion artifacts. Increasing this value leads to more valid pixels around moving objects, but it also increases the chances of computing wrong distance measurements for some pixels in the scene.

## Description

The O3R camera heads are using the ifm ToF (Time Of Flight) technology for measuring the distance to objects. To calculate one single point cloud, the system takes several images. These images are correlated to each other (see [basic concepts](INSERT-LINK)). This correlation is represented as symmetry (it can be though of as the four modulated signals used for performing the *raw* measurement being ideally symmetrical to each other). 
If a low symmetry threshold value is set, only the pixels where the correlation images are highly symmetrical (no or little motion) are valid. Due to inherent noise, no perfect symmetry is possible. 
Increasing the symmetry threshold validates more pixels including noisy pixels and potential motion artifacts.

*[img static object | img fast moving object]*

## Dependencies/Related topics

+ [Dynamic symmetry](INSERT-LINK)