
**Customer Question list:**

## time synchronization
+ How do you manage time keeping between several devices, e.g. AGVs: external time keeping.
+ How do you manage time keeping between several sensors, e.g. sonsars, angle encoders at higher framerate: internal time keeping
+ NTP server client:
  + What happens if the boot-up of the client is faster than the server?
  + Where is the NTP server situated? How many clients are served from one NTP server?
  + Do you have a fall-back NTP server?
  + Which implementation of a NTP client do you use to handle time signals in your language of choice (e.g. chrony in C++)?

+ Do you keep time related information in your maps and for how long is this stored? 
  + Does the time related information also get a statistical "component" similar to the statistical estimation for 3D data in occupancy grids?


## software deployment to embedded systems
+ How do you deploy your software code to an embedded system?
  + Is Docker a possible choice for deployment?
  + Is there an alternative container system which you want to use? 
  + Do you use a local registry for downloading containers?
+ What is your strategy for compiling for other architecture: ARM64 on VPU
+ Do you deploy non-Vision related software to the VPU Nvidia Tegra "vision board"?
+ How much processing power do you use on your IPC and what architecture is it (CPU)?
+ Have you thought about how to streamline your software code for a GPU use?


## update strategy
### genereal
+ How do you deploy software updates? Online vs offline approach?
  + For how long are your robots typically offline (at night? While charging?)?
+ How do keep track of different software states for systems at your customer production plants?
  + Is the fleet status management handled by you or your customers themselves?
  + Can one robot change it's behavior depending on it's requested use case: therefore keep track of different applications (and OS)?

+ How do you test your updates before deploying to a larger set of robots?
  + Do you test your algorithmic changes on live data or is tested on recorded data sets in post only?
  + How do check interoperability in feed-back loops, i.e. safety zone triggering for new updates?
+ How do you handle required software update introduced via dependent libraries / OS?
+ Do you update your OS for security updates?
### current embedded OS redundancy 
+ Partition size handling? A B redundancy on VPU? Is space really so limited that we need to abandon a redundant partition concept?
  + The trade-off is between size and security for failed updates and runtime.

+ What is their update handling and fall back strategy when updating fails? How long does it take to transfer a 1 GB file via wireless data communication?
  - Granular updates?
  - How much RAM / ROM required? Quantitative results required.
  - How often do you update?
  - Fleet concept or proven use case? Do they have a proven update strategy which works in field case use: what does this look like?

## ROS related questions (partially copied from Polarion)
**initial questions**
+ What are your expectations about a ROS driver?
+ What do you regard as no go features/implementation topics of ROS drivers?
+ Which `general` ROS packages do you use? Dependencies to other ROS packages? Rather keep it lightweight or more features? 3D light weight vs 3D + 2D full feature ROS wrapper.
+ Which other ROS packages (system and tools) do you use to handle perception -> object tracking, SLAM, ...
+ What ROS drivers for other cameras are you using?
+ What do you like/dislike about them?
+ Do you prefer to have a standard ROS package on the ROS index? Or alternatively build from source (have access to latest features: dev branch equivalent) yourself?

**broader questions**
+ Which ROS distribution do you use? Do you regularly update the ROS distro?
  + If you update between ROS distrobutions how do you handle the underlying OS Ubuntu update?
+ Do you prefer ROS1? Have you thought about updating your workspace to ROS2?Do you run ROS on ARM (Arch 64) architectures?
+ How often do you update your ROS packages? Bug fixes only? ROS industrial -> production ready / deployment
+ What is your typical use of ROS launch files?
+ Do you use Docker compose for different configurations? Do you use Docker in the context of ROS versions and ROS distros at all? In our mind it can be a good test environment before releasing it on a deployment level. Do you deploy your algorithms via ROS / ROS industrial / ... ?
+ How do you maintain / service your robots / software code once the are out in the field?
+ Do you have an automatized software feedback loop for reporting malfunctioning / bugs?
+ What are key parameters to rate the efficacy of you robot software code and therefore the success of you fleet?

**most current questions:**
+ Typical ROS docker size: The current Docker image size is limited to 3.6 GB: Is this enough for your ROS package selection? 
  + How big is their typical Docker images size depending on the use case?
  + Do you use independent ROS image builds depending on the exact use case or just have one standard one?

