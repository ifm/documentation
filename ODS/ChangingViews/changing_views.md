# How to switch cameras used for ODS

:::{note}
The support for camera switching with ODS was introduced for firmware version 1.1.X., alleviating the need to switch between instances of ODS as implemented in prior firmware.
:::

## Reconfigure application to use a different subset of ports

ODS running on the OVP800 is currently limited to 3 cameras running simultaneously so switching active cameras is required to see in all directions for most vehicles. Additionally, selectively deactivating cameras provides the advantage of energy savings. 


```py title="Application active camera changes"
# Update the app with a new set of active cameras and an updated set of zones
updated_app_config = {
    'applications': {
        'instances': {
            'app0': {
                "configuration": {
                    "activePorts": ["port3", "port6"] # list of ports should include port6 (the IMU)
                    "grid": {
                        "maxHeight": 1.4,    # optional
                    },
                    "zones": {
                        "zoneConfigID": 20,  # optional
                        "zoneCoordinates": [ # optional
                            [[0.0,-1],[1.0,-1],[1.0,1],[0.0,1]],
                            [[1.0,-1],[2.0,-1],[2.0,1],[1.0,1]],
                            [[2.0,-1],[3.0,-1],[3.0,1],[2.0,1]],
                        ]
                    },
                }
            }
        }
    },
o3r.set(updated_app_config)

```

:::{warning}
The set() function will throw an exception if the number of 3d ports specified in "activePorts" exceeds the "maxNumSimultaneousCameras" specified when the application was initialized or the 3d port was not present in the "ports" parameter of the application.
:::

