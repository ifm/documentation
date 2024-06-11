# Appendix - Changing the projection volume

If the default projection volume doesn't meet your needs, you have two options:
1. Adjust the coordinates of the projection volume.
  
    This is the preferred method but requires careful handling. It involves sliding the entire volume without altering its size. For example, if you change the maximum and minimum Y coordinates, you should adjust both by the same amount: `ymax_new = ymax + a` and `ymin_new = ymin + a`, ensuring `ymax_new - ymin_new` remains constant.

    We recommend adjusting the projection volume directly if you need to detect pallets that aren't directly in front of the camera but shifted in the Y direction, like shown in the image below:

    ![shifted](./resources/shifted.svg)

2. Edit the extrinsic calibration.

   Adjust the extrinsic calibration of the camera so that the calibrated camera coordinate system has a X axis that is parallel to the Y axis of the RCS.
   This ensures that the pallet's front face is perpendicular to the camera's X axis, which is what is required by the PDS algorithm.
   The results provided by PDS then need to be transformed to the RCS.

   This approach is the only one available in cases where the camera is mounted sideways on the robot, as shown in the image below:
    
    ![sideway](./resources/sideway.svg)