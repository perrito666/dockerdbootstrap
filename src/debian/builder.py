#! env python3

from shutil import which
from platform import system, machine
from logging import getLogger, basicConfig, DEBUG
from os import makedirs
from os.path import exists, isdir
import sys
try:
    from lsb_release import get_distro_information
except ImportError:
    get_distro_information=None

from .debootstrap import (DEBOOTSTRAP_COMMAND, Debootstrap,
        DebootstrapRuntimeError)

DEFAULT_ARCHITECTURE="amd64"
CURRENT_DEBIAN="jessie"
LINUX_SYSTEM="Linux"

log = getLogger("debootstrap.builder")

# This is by no means an exhaustive list, I dont know what less "traditional"
# architectures return, please be explicit when calling debootstrap if 
# not sure if running in one of the below architectures.
MACHINE_ARCH_MAP={"x86_64":"amd64",
                  "i386": "i386"}

class NotFoundError(BaseException):
    def __init__(self, message):
        self.message = "{:s} is not found".format(message)

class InvalidPathError(BaseException):
    def __init__(self, message):
        self.message = message


def check_debootstrap():
    """check_debootstrap will check if debootstrap is installed in the current
    machine and return an error if the dependency is not satisfied.
    """
    db_path = which(DEBOOTSTRAP_COMMAND)
    if db_path is None:
        raise NotFoundError(DEBOOTSTRAP_COMMAND)


def to_useful_arch(machine_arch):
    """to_useful_arch returns an architecture string useful to call debootstrap
    corresponding to <machine_arch> or None if its not possible to determine it.
    """
    return MACHINE_ARCH_MAP.get(machine_arch, None)


def maybe_determine_architecture():
    """maybe_determine_architecture will try to decide an architecture for the 
    debian folder to be created from the current machine.
    The determination process might fail especially if the current arch is
    rare or the OS not linux, in that case a default will be returned.
    """
    if system() != LINUX_SYSTEM:
        # no reliable info for dbootstrap most likely the intention
        # is not to run in place.
        return DEFAULT_ARCHITECTURE
    architecture = to_useful_arch(machine())
    if architecture is None:
        return DEFAULT_ARCHITECTURE
    return architecture


def ensure_doesnt_exists(destination):
    """ensure_doesnt_exists wil check for the existence of <destination> and
    raise an exception if it finds it.
    """
    if exists(destination):
        err = "{:s} exists but is not a directory"
        if isdir(destination):
            err = "{:s} directory exists and this process would overwrite it"
        raise InvalidPathError(err.format(destination))
    tgz = "{:s}.tar.gz".format(destination)


def maybe_determine_debian():
    """maybe_determine_debian will try to find out if the current running
    OS is a Debian GNU/Linux and return the version or the current debian
    version if not possible
    """
    if system() != LINUX_SYSTEM:
        return CURRENT_DEBIAN
    # if lsb_release is present we can assume that this is a linux distro
    # that can provide us with decent info.
    lsb_release = which("lsb_release")
    if lsb_release is None or get_distro_information is None:
        return CURRENT_DEBIAN
    distro_information = get_distro_information()
    if distro_information.get("ID", "") != "Debian":
        return CURRENT_DEBIAN
    return distro_information.get("CODENAME", CURRENT_DEBIAN)


def debootstrap(destination, target_version=None, arch=None):
    """debootstrap will try to create a debian chroot for debian version
    <target_version> in <destination> for arch <arch> if possible or raise
    an exception with information if not possible.
    """
    log.info("attempting to find debootstrap executable")
    check_debootstrap()
    if arch is None:
        arch = maybe_determine_architecture()
    ensure_doesnt_exists(destination)
    if target_version is None:
        target_version = maybe_determine_debian()
    debootstraper = Debootstrap(destination, target_version, arch)
    debootstraper.run()
    log.debug(debootstraper.runinfo())
    if debootstraper.result() != 0:
        # It would be interesting to have an output analisys tool built into
        # Debootstrap to produce the right exception according on the error.
        raise DebootstrapRuntimeError(debootstraper.result(), 
                                      debootstraper.runinfo())


if __name__ == "__main__":
    basicConfig(level=DEBUG)
    options = sys.argv[1:]
    if len(options) == 0:
        print("you must provide at least a destination")
        print("usage:")
        print("builder <imagename> [version_shortname] [arch]")
        print("note: .tar.gz extension will be added to imagename")
        sys.exit()
    debootstrap(*options)
