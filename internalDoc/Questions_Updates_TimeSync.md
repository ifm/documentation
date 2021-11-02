# Questions about update strategy:
## Updates
+ Update handling via their own update handler: update client handling on AGV main boards triggered from external update server
    + Updates on application level only: OS doesn't receive updates (no security updates / feature updates)
    + gets files which need to be replaced (board 1 running Windows): executables and config files for windows based applications
    + second board (also TX1 - exactly same board): runs a Linux distro L4T and calculates vision applications
    + typical file transfer speeds: 40 sec per 800 MB to 1 GB 
    + granular updates possible per application / configuration
    + at this point no immediate fall back strategy for failed updates: the update client takes last working application state and installs it again

## time sync
+ modem?? -> router acts as timeserver on AGV: supplies an NTP server for all other components boards 
+ the router is synced once on boot-up to outside NTP server in production facility
+ each other board only syncs once on it'a boot-up to router NTP server: 
    + Windows OS: rudimentary implementation via setting the system time once
    + Linux OS (vision board): NTP time is checked more often and can be set on an application specific level 
+ practical implementation: chrony in C++ code


## time synchronization
+ How do you manage time keeping between several devices, e.g. AGVs: external time keeping.  
*NTP via internal time keeping server and external time keeping server: internal modem / router, external NTP server*
+ How do you manage time keeping between several sensors, e.g. sonsars, angle encoders at higher framerate: internal time keeping  
*internal NTP server*
+ NTP server client:
  + What happens if the boot-up of the client is faster than the server?
  *The time sync between internal and external NTP server is only handled once at boot-up of AGV - afterwards time keeping is only internal*
  + Where is the NTP server situated? How many clients are served from one NTP server?
  + Do you have a fall-back NTP server?
  *Yes external NTP server has a local backup sever on premises*
  + Which implementation of a NTP client do you use to handle time signals in your language of choice (e.g. chrony in C++)?
  *chrony*

+ Do you keep time related information in your maps and for how long is this stored?  *NO. This is not even possible as the SLAM map and any object detection is done completely separate. No information is shared between both applications. The motor management gets information form both parties (current speed and angle of movement, object detection and their size and closest distance)*
  + Does the time related information also get a statistical "component" similar to the statistical estimation for 3D data in occupancy grids? *No information / description tracking over time is implemented*



## software deployment to embedded systems
+ How do you deploy your software code to an embedded system?
  + Is Docker a possible choice for deployment?
  *Yes. Currently not implemented on production AGVs but planned for new generation. Testing / Dev is already handled internally in Docker containers*
  + Do you use a local registry for downloading containers?
  *Not implemented yet*
+ What is your strategy for compiling for other architecture: ARM64 on VPU
+ Do you deploy non-Vision related software to the VPU Nvidia Tegra "vision board"?  
*This might be implemented in the future: they are currently using two identical TX1 boards but running different OS*
+ How much processing power do you use on your IPC and what architecture is it (CPU)?
*two TX1 boards processing capacities fully used*
+ Have you thought about how to streamline your software code for a GPU use?
*not discussed* 

