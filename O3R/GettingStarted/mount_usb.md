# Using an usb drive with the VPU

The VPU provides two `USB` interfaces, `USB-A` (USB 3.0) and `USB mini`. This ports can be used e.g. for automatic firmware updates, etc. It is also possible to increase the VPU memory size with it. To use the usb drive, it is necessary to mount the drive first.

## Preparing the usb drive

It is possible to use almost any typical usb drive, as long as they have no special formatting. A typical drive (with ext4 or FAT32) just needs to be plugged into the USB port. If an O3R firmware is stored on the drive, the system will start automatically an update. Therefore, an empty drive is preferred.

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

If the mount is successful you can find the drive at `/run/media/system/IFM/`.

```bash
o3r-vpu-c0:~$ ls -la /run/media/system/IFM/
total 957660
drwxr-xr-x 6 oem  oem       4096 Jan  1  1970 .
drwxr-xr-x 3 root root        60 Feb  7 15:54 ..
...
```