#
# This is a special configuration of the Linux kernel, based on linux package
# for long-term support
#

Name:           linux-lts
Version:        4.9.29
Release:        339
License:        GPL-2.0
Summary:        The Linux kernel
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.9.29.tar.xz
Source1:        config
Source2:        cmdline
Source3:        install-vbox-lga

%define kversion %{version}-%{release}.lts

BuildRequires:  bash >= 2.03
BuildRequires:  bc
BuildRequires:  binutils-dev
BuildRequires:  elfutils-dev
BuildRequires:  make >= 3.78
BuildRequires:  openssl-dev
BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  kmod
BuildRequires:  linux-firmware

# don't strip .ko files!
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

#    000X: cve, bugfixes patches

#    00XY: Mainline patches, upstream backports
Patch0011: 0011-drm-i915-fbc-sanitize-fbc-GEN-greater-than-9.patch

# Serie    01XX: Clear Linux patches
Patch0101: 0101-kvm-silence-kvm-unhandled-rdmsr.patch
Patch0102: 0102-i8042-decrease-debug-message-level-to-info.patch
Patch0103: 0103-init-do_mounts-recreate-dev-root.patch
Patch0104: 0104-Increase-the-ext4-default-commit-age.patch
Patch0105: 0105-silence-rapl.patch
Patch0106: 0106-pci-pme-wakeups.patch
Patch0107: 0107-ksm-wakeups.patch
Patch0108: 0108-intel_idle-tweak-cpuidle-cstates.patch
Patch0109: 0109-xattr-allow-setting-user.-attributes-on-symlinks-by-.patch
Patch0110: 0110-init_task-faster-timerslack.patch
Patch0112: 0112-fs-ext4-fsync-optimize-double-fsync-a-bunch.patch
Patch0113: 0113-overload-on-wakeup.patch
Patch0114: 0114-bootstats-add-printk-s-to-measure-boot-time-in-more-.patch
Patch0115: 0115-fix-initcall-timestamps.patch
Patch0116: 0116-smpboot-reuse-timer-calibration.patch
Patch0117: 0117-raid6-add-Kconfig-option-to-skip-raid6-benchmarking.patch
Patch0118: 0118-Initialize-ata-before-graphics.patch
Patch0119: 0119-reduce-e1000e-boot-time-by-tightening-sleep-ranges.patch
Patch0120: 0120-give-rdrand-some-credit.patch
Patch0121: 0121-e1000e-change-default-policy.patch
Patch0122: 0122-ipv4-tcp-allow-the-memory-tuning-for-tcp-to-go-a-lit.patch
Patch0123: 0123-igb-no-runtime-pm-to-fix-reboot-oops.patch
Patch0124: 0124-tweak-perfbias.patch
Patch0125: 0125-e1000e-increase-pause-and-refresh-time.patch

# Clear Linux KVM Memory Optimization
Patch0151: 0151-mm-Export-do_madvise.patch
Patch0152: 0152-x86-kvm-Notify-host-to-release-pages.patch
Patch0153: 0153-x86-Return-memory-from-guest-to-host-kernel.patch
Patch0154: 0154-sysctl-vm-Fine-grained-cache-shrinking.patch

# Serie    XYYY: Extra features modules
#    100X: Accelertor Abstraction Layer (AAL)
Patch1001: 1001-fpga-add-AAL-6.3.1.patch
Patch1002: 1002-fpga-add-AAL-to-fpga-Kconfig.patch
#          200Y: VirtualBox modules
Patch2001: 2001-virtualbox-add-module-sources.patch
Patch2002: 2002-virtualbox-setup-Kconfig-and-Makefiles.patch


%description
The Linux kernel.

%package extra
License:        GPL-2.0
Summary:        The Linux kernel extra files
Group:          kernel

%description extra
Linux kernel extra files

%prep
%setup -q -n linux-4.9.29

#     000X  cve, bugfixes patches

#     00XY  Mainline patches, upstream backports
%patch0011 -p1

#     01XX  Clear Linux patches
%patch0101 -p1
%patch0102 -p1
%patch0103 -p1
%patch0104 -p1
%patch0105 -p1
%patch0106 -p1
%patch0107 -p1
%patch0108 -p1
%patch0109 -p1
%patch0110 -p1
%patch0112 -p1
%patch0113 -p1
%patch0114 -p1
%patch0115 -p1
%patch0116 -p1
%patch0117 -p1
%patch0118 -p1
%patch0119 -p1
%patch0120 -p1
%patch0121 -p1
%patch0122 -p1
%patch0123 -p1
%patch0124 -p1
%patch0125 -p1

# Clear Linux KVM Memory Optimization
%patch0151 -p1
%patch0152 -p1
%patch0153 -p1
%patch0154 -p1

#     XYYY: Extra features modules
#     100X  Accelertor Abstraction Layer (AAL)
%patch1001 -p1
%patch1002 -p1
#     200Y: VirtualBox modules
%patch2001 -p1
%patch2002 -p1

cp %{SOURCE1} .

cp -a /usr/lib/firmware/i915 firmware/
cp -a /usr/lib/firmware/intel-ucode firmware/

%build
BuildKernel() {
    MakeTarget=$1

    Arch=x86_64
    ExtraVer="-%{release}.lts"

    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = ${ExtraVer}/" Makefile

    make -s mrproper
    cp config .config

    make -s ARCH=$Arch oldconfig > /dev/null
    make -s CONFIG_DEBUG_SECTION_MISMATCH=y %{?_smp_mflags} ARCH=$Arch %{?sparse_mflags}
}

BuildKernel bzImage

%install
mkdir -p %{buildroot}/usr/sbin
install -m 755 %{SOURCE3} %{buildroot}/usr/sbin

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

    # Erase some modules index
    for i in alias ccwmap dep ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols usbmap softdep devname
    do
        rm -f %{buildroot}/usr/lib/modules/${KernelVer}/modules.${i}*
    done
    rm -f %{buildroot}/usr/lib/modules/${KernelVer}/modules.*.bin
}

InstallKernel arch/x86/boot/bzImage

rm -rf %{buildroot}/usr/lib/firmware

# Recreate modules indices
depmod -a -b %{buildroot}/usr %{kversion}

ln -s org.clearlinux.lts.%{version}-%{release} %{buildroot}/usr/lib/kernel/default-lts

%files
%dir /usr/lib/kernel
%dir /usr/lib/modules/%{kversion}
/usr/lib/kernel/config-%{kversion}
/usr/lib/kernel/cmdline-%{kversion}
/usr/lib/kernel/org.clearlinux.lts.%{version}-%{release}
/usr/lib/kernel/default-lts
/usr/lib/modules/%{kversion}/kernel
/usr/lib/modules/%{kversion}/modules.*
/usr/sbin/install-vbox-lga

%files extra
%dir /usr/lib/kernel
/usr/lib/kernel/System.map-%{kversion}
