# Using a USB drive with the VPU

The VPU provides two `USB` interfaces, `USB-A` (USB 3.0) and `USB mini`.
It is possible to increase the VPU memory size by utilizing USB thumb drives or USB SSDs on the `USB-A` interface. To use any USB storage device, it is necessary to mount the drive first.


.. note::
The USB auto mount service mounts your USB mass storage device to `/run/media/system/<USB_name>/`. See the details below.

## Preparing the usb drive

The VPU's operating system supports two file formats:
+ FAT32
+ EXT4

These can be auto-mounted via the `mount` command and its respective daemon.

**FAT32:**
For FAT32 formatted devices no additional steps are required. It can be directly mounted via the auto-mount daemon to the VPU.

**EXT4:**
For EXT4 formatted devices the user needs to perform additional steps to match the OEM users `uid` and `gid` on the VPU's embedded OS.
Otherwise only read permissions are granted when mounting the USB storage device. This is a design that is introduced by the handling of access rights to EXT4 formatted devices on Linux systems.
If you are an experience EXT4 user feel free to skip the following instructions steps:

### EXT4 format USB mounting preparation

**Option 1:**
"The crude way"

The easiest option is to mount the EXT4 formatted device to your Linux laptop of choice and relax the write and read permissions to be accessible by any user:
1. Mount the SSD to your laptop
2. Change the mount point to be accessible by all users:
```bash
user@laptop:~$ chmod 777 /media/<mount_point>
```
Please be aware that the `chmod` command only affects the existing files within `/media/<mount_point>`.


**Option 2:**
"Setting the VPUs oem user UID and GID specifically"

Please be aware that setting user specific GID and UID has to be done **PER** user.
This means, that is has to be done for the oem user on the VPU to write to the device, as well as any specific users created inside your own Docker container.

Below an exemplary workflow is shown for setting the VPUs oem users UID and GID.

On the VPU:
1. Find out the requested users UID and GID on the VPU or inside the Docker container
```bash
oem@o3r-vpu-c0:~# id -u oem
989
oemt@o3r-vpu-c0:~# id -g oem
987
```
On your Linux laptop of choice:
1. Change the USB mount point on your **Linux Laptop** via chown
```bash
user@laptop:~$ sudo chown 989:987 -R /media/<mount_point>
```

.. note::
Please be aware that changing the GID and UID mountpoints may result in missing read access on your laptop. To restore read access on your laptop to the USB storage device, change the GID and UID back to match your personal user accounts ones.


## Plug in and mounting

After plugging in the drive, the mount is started by using the command `mount`

```bash
o3r-vpu-c0:~$ mount
proc on /proc type proc (rw,relatime)
none on /dev type devtmpfs (rw,relatime,size=1578060k,nr_inodes=394515,mode=755)
sysfs on /sys type sysfs (rw,relatime)
/dev/mmcblk0p1 on / type ext4 (rw,relatime,data=ordered)
tmpfs on /dev/shm type tmpfs (rw,nosuid,nodev)
devpts on /dev/pts type devpts (rw,relatime,gid=5,mode=620,ptmxmode=666)
tmpfs on /run type tmpfs (rw,nosuid,nodev,mode=755)
tmpfs on /sys/fs/cgroup type tmpfs (ro,nosuid,nodev,noexec,mode=755)
cgroup2 on /sys/fs/cgroup/unified type cgroup2 (rw,nosuid,nodev,noexec,relatime)
cgroup on /sys/fs/cgroup/systemd type cgroup (rw,nosuid,nodev,noexec,relatime,xattr,name=systemd)
pstore on /sys/fs/pstore type pstore (rw,nosuid,nodev,noexec,relatime)
cgroup on /sys/fs/cgroup/pids type cgroup (rw,nosuid,nodev,noexec,relatime,pids)
cgroup on /sys/fs/cgroup/net_cls,net_prio type cgroup (rw,nosuid,nodev,noexec,relatime,net_cls,net_prio)
cgroup on /sys/fs/cgroup/cpuset type cgroup (rw,nosuid,nodev,noexec,relatime,cpuset)
cgroup on /sys/fs/cgroup/freezer type cgroup (rw,nosuid,nodev,noexec,relatime,freezer)
cgroup on /sys/fs/cgroup/memory type cgroup (rw,nosuid,nodev,noexec,relatime,memory)
cgroup on /sys/fs/cgroup/cpu,cpuacct type cgroup (rw,nosuid,nodev,noexec,relatime,cpu,cpuacct)
cgroup on /sys/fs/cgroup/debug type cgroup (rw,nosuid,nodev,noexec,relatime,debug)
cgroup on /sys/fs/cgroup/hugetlb type cgroup (rw,nosuid,nodev,noexec,relatime,hugetlb)
cgroup on /sys/fs/cgroup/blkio type cgroup (rw,nosuid,nodev,noexec,relatime,blkio)
cgroup on /sys/fs/cgroup/devices type cgroup (rw,nosuid,nodev,noexec,relatime,devices)
cgroup on /sys/fs/cgroup/perf_event type cgroup (rw,nosuid,nodev,noexec,relatime,perf_event)
mqueue on /dev/mqueue type mqueue (rw,nosuid,nodev,noexec,relatime)
hugetlbfs on /dev/hugepages type hugetlbfs (rw,relatime)
debugfs on /sys/kernel/debug type debugfs (rw,nosuid,nodev,noexec,relatime)
tmpfs on /tmp type tmpfs (rw,nosuid,nodev)
configfs on /sys/kernel/config type configfs (rw,nosuid,nodev,noexec,relatime)
tmpfs on /var/volatile type tmpfs (rw,relatime)
/dev/mmcblk0p33 on /opt/ifm/data type ext4 (rw,relatime,data=ordered)
overlay on /etc/systemd/network type overlay (rw,relatime,lowerdir=/etc/systemd/network,upperdir=/opt/ifm/data/overlayfs/upper/network,workdir=/opt/ifm/data/overlayfs/work/network)
tmpfs on /run/user/989 type tmpfs (rw,nosuid,nodev,relatime,size=392056k,mode=700,uid=989,gid=987)
systemd-1 on /run/media/system/IFM type autofs (rw,relatime,fd=79,pgrp=1,timeout=3,minproto=5,maxproto=5,direct)
```

If the mount is successful you can find the drive at `/run/media/system/<USB_name>/`.

```bash
o3r-vpu-c0:~$ ls -la /run/media/system/IFM/
total 957660
drwxrwxrwx 6 oem  oem       4096 Jan  1  1970 .
drwxrwxrwx 3 root root        60 Feb  7 15:54 ..
...
```