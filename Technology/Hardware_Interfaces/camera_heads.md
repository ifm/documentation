
## Camera Heads

The camera heads mentioned above differ in their field of view, which has to be considered when selecting the correct hardware. The operational conditions and application use case are the two important factors to be considered for choosing a camera head.

### Operational Conditions

The `O3R2xx` camera heads are `IP54` rated, which means that with regular maintenance and cleaning, they can be used in some harsher environments, such as dusty conditions and mixed indoor/outdoor conditions. In all operating conditions, the cameras must be cleaned regularly to prevent dust or particles from building up on the surface of the camera head, which will gradually degrade the camera's measurement performance.

Please note that all O3R camera heads (O3R222 and O3R225) are designed for indoor use. Outdoor conditions may work depending on the application requirements but must be benchmarked by the customer.

Mixed indoor - outdoor conditions are understood by ifm to be conditions that are mainly indoors but may include bright illumination patterns of overhead skylights and windows on the floor and objects.

### Application use-case

Two application use cases can be differentiated depending on the O3R camera heads:
- The O3R222 has a narrow field of view which is ideal for applications focussing on detecting smaller objects and objects at longer ranges.
- Whereas, the O3R225 camera head has a wider field of view which is ideal for the applications focussing on perceiving the larger areas and minimizing dead zones due to non-adjacent or non-overlapping field of views.

### Port(s) overview

Within the ODS configuration and reception of data, several kinds of `port`s are used.

#### Hardware Ports
- There are the 6 hardware ports, where the O3R heads (e.g. O3R225) are connected
- There are communication ports (TCP/IP), which are partly mapped to the hardware ports. Depending on the actual head to port configuration, it might be useful to get the communication ports from the config. (Head1 @ port2, Head2 @ Port3 -> Used TCP/IP ports: 50012 & 50013)

- While it is good practice to check the PCIC port directly for the requested hardware port, we list below the correspondence between hardware ports and PCIC ports for reference.

   |Hardware port| TCP/IP port|
   |-:|:-|
   |Port 0|50010|
   |Port 1|50011|
   |Port 2|50012|
   |Port 3|50013|
   |Port 4|50014|
   |Port 5|50015|

#### IMU port

- Besides the hardware ports mentioned above, there is an additional non-configurable hardware port `PORT6` which is specific to `IMU` of the device. Therefore, the communication(TCP/IP) port mapped to `PORT6` is `50016`. 

:::{note} It is not possible to receive any data from the `IMU` at the moment.
:::

To retrieve the PCIC port number for any port, one can use ifm3d(py) API. The following code snippet serves as an example to retrieve the TCP/IP port for `PORT2`:

```python
from ifm3dpy import O3R
o3r = O3R()
pcic_port = o3r.get(["/ports/port2/data/pcicTCPPort"])["ports"]["port2"]["data"]["pcicTCPPort"]
>>>50012
```

:::{note} The `o3r.get` command shown above is provided as a subset of the JSON configuration. We do this to optimize the `get` process: we only retrieve the information we need instead of the whole configuration.
:::

#### Application ports

- When the user creates an application instance then the application output can be received from their dedicated communication ports, which can be retrieved similarly to the PCIC ports.
- The TCP/IP ports for applications increment from `51010`.
- Each ODS application instance has one communication port to forward its ODS information.
- For reference, below is the application number to PCIC port correspondence.

   |Application number| TCP/IP port|
   |-:|:-|
   |App 0|51010|
   |App 1|51011|
   |App x|5101x|
- The following code snippet serves as an example to retrieve the TCP/IP port of a first application instance.

```python
from ifm3dpy import O3R
o3r = O3R()
app_port = o3r.get(["/applications/instances/app1/data/pcicTCPPort"])["applications"]["instances"]["app0"]["data"]["pcicTCPPort"]
>>>51010
```
:::{note} With firmware versions `0.16.23` or higher, it is possible to receive the TCP/IP port bound to the hardware port or application. Use the ifm3d(py) helper function `ports` [in python](https://api.ifm3d.com/html/_autosummary/ifm3dpy.device.O3R.html#ifm3dpy.device.O3R.ports) or [c++](https://api.ifm3d.com/html/cpp_api/classifm3d_1_1O3R.html#ab82367443890c0526f2da7c79147e6b5).
:::

![mermaid](resources/mermaid-graph.png)

- It is possible to choose the ports from the available ports to be considered for application. For example, if `PORT2` and `PORT3` are connected to two camera heads then the user can choose any port/both ports from the above to be considered for application.
 
:::{note} However, if the receiving end is not fast enough in receiving data from the application-dependent ports, then the queue may fill up and the algorithm discards the old frames. This might lead to issues with running applications and results in low framerate. The ODS application operates at 20 fps by default.
:::{warning} It is possible to change several parameters of ports that are referenced by an ODS application. This is meant for debugging and the user must not change these parameters.
:::
:::