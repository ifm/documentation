# SSH usage

To connect to the VPU through SSH or deploy software to the VPU with SCP, it is necessary 1. have an SSH key pair, 2. Have the public key copied to the VPU configuration.

Follow instructions below to configure SSH on the VPU via either the CLI or via python3


## Setup via CLI

:::{note}
The following instructions are tailored towards a bash (Unix shell). When deploying on a Windows based architecture, please modify the instructions sets for your shell accordingly, or try the setup instructions for Python instead
:::

### Generate an SSH key-pair

All user specific SSH keys are located at `~/.ssh`. This is the place where the private key for the connection to the VPU should be stored.

To generate an SSH key-pair, use `ssh-keygen` and follow the prompts:

```bash
$ cd ~/.ssh/
$ ssh-keygen -t rsa -b 4096 -C "<Some comment to remember what the key is for>"
Generating public/private rsa key pair.
Enter file in which to save the key (~/.ssh/id_rsa): id_o3r
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
...
```

A passphrase is optional. After that command, two new keys are generated within the `~/.ssh` directory. With the example above it would be `id_o3r` and `id_o3r.pub`.


### Upload the public key to the VPU

Uploading the public (`.pub`) SSH key to the VPU is achieved via the ifm3d library.
The device configuration includes a parameter for authorized keys: `authorized_keys`. It is empty by default.

```bash
$ ifm3d ovp8xx config get --path "/device/network"
{
  "device": {
    "network": {
      "authorized_keys": "",
      "firewall": {
        "active": false
      },
      "interfaces": {
        "can0": {
          "active": false,
          "bitrate": "125K",
          "restart-ms": 10000
        },
        "eth0": {
          "firewall": {
            "userPorts": []
          },
          "ipv4": {
            "address": "192.168.0.69",
            "dns": "0.0.0.0",
            "gateway": "192.168.0.201",
            "mask": 24
          },
          "mac": "48:B0:2D:87:1B:C9",
          "networkSpeed": 1000,
          "useDHCP": false
        },
        "eth1": {
          "firewall": {
            "userPorts": []
          },
          "ipv4": {
            "address": "192.168.42.69",
            "dns": "0.0.0.0",
            "gateway": "0.0.0.0",
            "mask": 24
          },
          "mac": "00:02:01:44:EB:07",
          "networkSpeed": 10,
          "useDHCP": false
        }
      }
    }
  }
}
```

To add a new key, the VPU configuration needs to be changed. The easiest way in this case is to use the `jq` command along with the ifm3d API CLI:

To install `jq` library, follow the instructions mentioned in [./jq website](https://jqlang.org/download/)

:::::{tabs}
::::{group-tab} Linux
```bash
$ echo {} | jq --arg id "$(< ~/.ssh/id_o3r.pub)" '.device.network.authorized_keys=$id' | ifm3d ovp8xx config set
```
::::
::::{group-tab} Windows
```powershell
>$publicKey = Get-Content -Raw <path\to\id_o3r.pub>
>echo "{}" | jq --arg id "$publicKey" '.device.network.authorized_keys=$id' | ifm3d config
```
::::
:::::

- `jq --arg id "$(< ~/.ssh/id_o3r.pub)"` - This loads the public key into the variable `id` and provides it to the `jq` command
- `'.device.network.authorized_keys=$id'` - Here the JSON value from `authorized_keys` is changed for the public key within the variable `id`
- `ifm3d config` - The new JSON is now used to change the configuration of the VPU via `ifm3d config`

Now, the content of the `authorized_keys` should look something like:
```bash
$ ifm3d ovp8xx config get --path "/device/network/authorized_keys"
"ssh-rsa AAAAB3NzaC.....wZ9l3iSUaPPWOeFVz+xwlw== Some comment"
```

Note that the `authorized_keys` is a persistent parameter: it does not require a call to [`save_init`](../configuration.md#persistent-settings-without-save_init) to be persistent over reboots.


## Setup via Python script

This method will require a Python 3 environment with ifm3dpy and Paramiko installed via pip

```
pip install ifm3dpy paramiko
```

The Python script [ssh_key_gen.py](https://github.com/ifm/ifm3d-examples/blob/main/ovp8xx/python/ovp8xxexamples/core/ssh_key_gen.py) can be used on both Windows and Linux

Run the script with "--help" for optional arguments

``` bash
python ssh_key_gen.py --help
usage: ssh_key_gen.py [-h] [--IP IP] [--key_title KEY_TITLE] [--key_size KEY_SIZE] [--target_dir TARGET_DIR] [--log-file LOG_FILE]

ssh key generator script for OVP8xx

options:
  -h, --help            show this help message and exit
  --IP IP               IP address to be used, default: 192.168.0.69
  --key_title KEY_TITLE
                        Title of the key, default: id_o3r
  --key_size KEY_SIZE   Size of the key, default: 4096
  --target_dir TARGET_DIR
                        Directory to save the key, default: ~/.ssh
  --log-file LOG_FILE   The file to save relevant output
```

Running the file will generate the key-pair as specified, if unavailable, copy the public key to the VPU, and run a test command via SSH.

```bash
2024-10-30 11:49:25,348 [MainThread  ] [INFO ]  Connecting to 192.168.0.69 to verify the keys are set correctly.
2024-10-30 11:49:25,707 [MainThread  ] [INFO ]  Hello, world! (echoed back from the device)
```

## Connect to the VPU using the private key

After the key is uploaded, it is possible to connect with SSH and the username `oem` to the VPU:

```bash
$ ssh oem@192.168.0.69 -i ~/.ssh/id_o3r
The authenticity of host '192.168.0.69 (192.168.0.69)' can't be established.
ECDSA key fingerprint is SHA256:8gjC9za45TTRZNz5JCMwaNJ27BLfsPyDtjBaBQ2vyHw.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '192.168.0.69' (ECDSA) to the list of known hosts.
o3r-vpu-c0:~$
```

The -i "identity" argument is required on some shells for the private key to be used.

There will be a prompt for the passphrase, if this was configured when running `ssh-keygen`.

If successful with the setup, the user will be logged into a shell on the VPU as the OEM user.
