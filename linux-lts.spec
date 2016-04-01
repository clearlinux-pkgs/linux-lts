#
# This is a special configuration of the Linux kernel, based on linux package
# for long-term support
#

Name:           linux-lts
Version:        4.4.6
Release:        1
License:        GPL-2.0
Summary:        The Linux kernel
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.4.6.tar.xz
Source1:        config
Source2:        cmdline

%define kversion %{version}-%{release}.lts

BuildRequires:  bash >= 2.03
BuildRequires:  bc
# For bfd support in perf/trace
BuildRequires:  binutils-dev
BuildRequires:  elfutils
BuildRequires:  elfutils-dev
BuildRequires:  kmod
BuildRequires:  make >= 3.78
BuildRequires:  openssl-dev
BuildRequires:  flex
BuildRequires:  bison

# don't srip .ko files!
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

Patch1:  0001-init-don-t-wait-for-PS-2-at-boot.patch
Patch2:  0002-sched-tweak-the-scheduler-to-favor-CPU-0.patch
Patch3:  0003-kvm-silence-kvm-unhandled-rdmsr.patch
Patch4:  0004-i8042-decrease-debug-message-level-to-info.patch
Patch5:  0005-raid6-reduce-boot-time.patch
Patch6:  0006-net-tcp-reduce-minimal-ack-time-down-from-40-msec.patch
Patch7:  0007-init-do_mounts-recreate-dev-root.patch
Patch8:  0008-Increase-the-ext4-default-commit-age.patch
Patch9:  0009-silence-rapl.patch
Patch10: 0010-pci-pme-wakeups.patch
Patch11: 0011-ksm-wakeups.patch
Patch12: 0012-intel_idle-tweak-cpuidle-cstates.patch
Patch13: 0013-xattr-allow-setting-user.-attributes-on-symlinks-by-.patch
Patch14: 0014-init_task-faster-timerslack.patch
Patch15: 0015-KVM-x86-Add-hypercall-KVM_HC_RETURN_MEM.patch

# DPDK 2.1.0 integration
Patch51: 5001-dpdk-add-source-files.patch
Patch52: 5002-dpdk-Integrate-Kconfig-and-Makefiles.patch

# virtualbox modules
Patch8001: 8001-virtualbox-add-module-sources.patch
Patch8002: 8002-virtualbox-add-Kconfs-and-Makefiles.patch

%description
The Linux kernel.

%package extra
License:        GPL-2.0
Summary:        The Linux kernel extra files
Group:          kernel

%description extra
Linux kernel extra files

%package vboxguest-modules
License:        GPL-2.0
Summary:        Oracle VirtualBox guest additions modules
Group:          kernel

%description vboxguest-modules
Oracle VirtualBox guest additions modules

%prep
%setup -q -n linux-4.5

#%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1

# DPDK 2.1.0 integration
%patch51 -p1
%patch52 -p1

# virtualbox modules
%patch8001 -p1
%patch8002 -p1

cp %{SOURCE1} .

%build
BuildKernel() {
    MakeTarget=$1

    Arch=x86_64
    ExtraVer="-%{release}.lts"

    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = ${ExtraVer}/" Makefile

    make -s mrproper
    cp config .config

    make -s ARCH=$Arch oldconfig > /dev/null
    make -s CONFIG_DEBUG_SECTION_MISMATCH=y %{?_smp_mflags} ARCH=$Arch $MakeTarget %{?sparse_mflags}
    make -s CONFIG_DEBUG_SECTION_MISMATCH=y %{?_smp_mflags} ARCH=$Arch modules %{?sparse_mflags} || exit 1
}

BuildKernel bzImage

%install

InstallKernel() {
    KernelImage=$1

    Arch=x86_64
    KernelVer=%{kversion}
    KernelDir=%{buildroot}/usr/lib/kernel

    mkdir   -p ${KernelDir}
    install -m 644 .config    ${KernelDir}/config-${KernelVer}
    install -m 644 System.map ${KernelDir}/System.map-${KernelVer}
    install -m 644 %{SOURCE2} ${KernelDir}/cmdline-${KernelVer}
    cp  $KernelImage ${KernelDir}/org.clearlinux.lts.%{version}-%{release}
    chmod 755 ${KernelDir}/org.clearlinux.lts.%{version}-%{release}

    mkdir -p %{buildroot}/usr/lib/modules/$KernelVer
    make -s ARCH=$Arch INSTALL_MOD_PATH=%{buildroot}/usr modules_install KERNELRELEASE=$KernelVer

    rm -f %{buildroot}/usr/lib/modules/$KernelVer/build
    rm -f %{buildroot}/usr/lib/modules/$KernelVer/source
}

InstallKernel arch/x86/boot/bzImage

rm -rf %{buildroot}/usr/lib/firmware

# Erase some modules index and then re-crate them
for i in alias ccwmap dep ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols usbmap softdep devname
do
    rm -f %{buildroot}/usr/lib/modules/%{kversion}/modules.${i}*
done
rm -f %{buildroot}/usr/lib/modules/%{kversion}/modules.*.bin

# Recreate modules indices
depmod -a -b %{buildroot}/usr %{kversion}

ln -s org.clearlinux.lts.%{version}-%{release} %{buildroot}/usr/lib/kernel/default-lts

%files
%dir /usr/lib/kernel
%exclude  /usr/lib/modules/%{kversion}/kernel/arch/x86/virtualbox/
%dir /usr/lib/modules/%{kversion}
/usr/lib/kernel/config-%{kversion}
/usr/lib/kernel/cmdline-%{kversion}
/usr/lib/kernel/org.clearlinux.lts.%{version}-%{release}
/usr/lib/kernel/default-lts
/usr/lib/modules/%{kversion}/kernel
/usr/lib/modules/%{kversion}/modules.*

%files extra
%dir /usr/lib/kernel
/usr/lib/kernel/System.map-%{kversion}

%files vboxguest-modules
/usr/lib/modules/%{kversion}/kernel/arch/x86/virtualbox/
