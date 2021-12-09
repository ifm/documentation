# FAQ

__Q: Is it necessary to shut down the camera before switching off the power?__  
__A:__ No, the O3R system can be switched off at anytime (except during firmware update).  

__Q: What kind of certificates does the O3R fullfil?__  
__A:__ CE (Europe) and UL(USA) will be fulfilled at the release of the system (October 2021).

__Q: VPU? Camera heads?__  
__A:__ `VPU` - Video Processing Unit. The O3R is using the NVidia TX2 as a base computing platform and free CPU and GPU resources can be used for customer algorithms. You can connect our camera heads directly to the VPU and you do not need to take care of communication, power etc. separately. These heads come in different flavors. 2D/3D, 38k or VGA resolution, 105° or 60° opening angle. 

__Q: Are there any plans to include the O3R platform into the ifmVisionAssistant?__  
__A:__ Absolutely! The ifmVA will be available sometime after the official release of the O3R (October 2021). 

__Q: What ports are used and can I change them?__  
__A:__ The O3R system is using the ports 8080,8888,50010-50025. Right now, it is not possible to change the ports, but this will be possible in the future.
>Note: Ports 8080 and 8888 are reserved ports for specific ifm applications and can't be changed.

__Q: How can I define the extrinsic calibration for my different heads?__  
__A:__ There are several ways to do that and we do not recommend any one over the other. At ifm, we manly use the checkerboard method, but you can also manually measure everything or use other tools. If you want to know more, please get in touch with us and read our documentation.

__Q: Is it possible to change the extrinsic calibration?__
__A:__ Indeed! You have the possibility to change the extrinsic calibration for each head. The calibration will be saved on the VPU and is also available after an reboot (see [configuring the camera](INSERT-LINK)). To know more, check out our [calibration documentation *coming soon*](INSERT-LINK).

__Q: Okay, so you have the ability to set the extrinsic calibration. Do we also need to intrinsically calibrate the camera?__  
__A:__ No, don't worry about this. We are calibrating each head individually in production. You can, however, receive the intrinsic calibration if you need it (it is sent in the `distance_image_info`, see the [images description *coming soon*](INSERT-LINK)).  
> Note: Our calibration also includes temperature, lens position, etc. There is no need for an additional calibration on your side. 

__Q: Unfortunately, one of the heads was destroyed in dubious circumstances. Can I replace the head?__  
__A:__ Sure thing! Just get a new one and replace the broken one. We recommend performing a sanity check of the extrinsic calibration of the newly mounted head (the mounting of the camera might have shifted a few millimeters or degrees in the replacement process). But that's it. Just keep in mind that we have different kind of heads. 

__Q: Can I replace a head with another type of head (60 degrees vs. 105 degrees for instance):__  
__A:__ Yes! The VPU does not need any new information about the new head. It might be that the VPU needs a bit longer after the first start with the new head. The VPU will query different information from the head to work properly. We are talking about seconds here, not minutes.

__Q: Are there any debug or logging capabilities within the VPU?__  
__A:__ The system is logging a lot of information all the time. You can receive this *trace* with our [ifm3d-library](INSERT-LINK) for the official launch).

__Q: How often do I have to update the firmware/software? Do I always need them?__  
__A:__ We are in a phase were we will release a new firmware fairly often (around once a month). This will most likely change after the official release. We recommend to always update to the newest firmware (due to bug fixes, but also because of security). We know that most of our customers use the approach "never touch a running system" and we get that. Our changelog and release notes will tell you exactly what changed and you can decide if it is worth the risk to update or not. If in doubt, just get in touch with us!

__Q: What kind of connection protocols can I use?__
__A:__ Well, the default would be TCP/IP. This is also the default protocol for our libraries. You will, however, get access to the VPU itself at a certain point. Then, you can use other protocols, e.g., UDP. Ad UDP is not yet officially supported by ifm, you will need to implement it by yourself, but you are free to do so. You also can use the CAN interface.

__Q: How do I get access to the VPU in general?__  
__A:__ You have access via ssh and a customer account. 

__Q: Can I use the VPU with its CPU/GPU and let my program run on it?__  
__A:__ 100%! You will be able to upload your program and/or develop directly on the VPU. The VPU will already run the docker engine, which will enable you to have an easy deployment. You can first develop on your machine, build the container and forward it to the VPU. We can provide to you some base images for the development if needed.

__Q: Do you support ROS1 & ROS2?__  
__A:__ We have two ROS-Wrappers for our ifm3D libraries, for ROS1 and ROS2. You can easily test the set up using containers, running the roscore on the VPU for instance, or just connect the VPU as a ROS client to your roscore or other nodes. Whatever suits you best. If you want to know more, you can read our [documentation](INSERT-LINK) or get in touch with us.

