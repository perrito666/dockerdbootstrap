import unittest
from tempfile import mkdtemp
from shutil import rmtree
from os.path import join
from importlib import import_module
from ..debian.builder import (ensure_doesnt_exists, InvalidPathError)
from ..debian.debootstrap import DebootstrapRuntimeError

LATEST_DEBIAN="jessie"

class TestPathChecking(unittest.TestCase):
    def setUp(self):
        self._temp_dir = mkdtemp()

    def tearDown(self):
        rmtree(self._temp_dir) 

    def test_path_exists_succeeds(self):
        # No assertions where, this test will fail if the success case 
        # is broken.
        ensure_doesnt_exists("/i/am/sure/this/is/fake")

    def test_path_exists_fails(self):
        err = ".* directory exists and this process would overwrite it"
        with self.assertRaisesRegex(InvalidPathError, err):
            ensure_doesnt_exists(self._temp_dir) 

    def test_path_exists_isfile(self):
        testfile = join(self._temp_dir, "afile")
        with open(testfile, "w") as afile:
                afile.write("a content")

        err = ".* exists but is not a directory"
        with self.assertRaisesRegex(InvalidPathError, err):
            ensure_doesnt_exists(testfile) 

class TestMaybeDetermineDebian(unittest.TestCase):
    def setUp(self):
        self.debian = import_module("debian.builder")

    def test_not_linux(self):
        def not_linux():
            return "NotLinux"
        self.debian.system = not_linux
        debian_version = self.debian.maybe_determine_debian()
        self.assertEqual(debian_version, LATEST_DEBIAN)

    def test_no_lsb_release(self):
        def no_lsb_which(cmd):
            return None
        self.debian.which = no_lsb_which
        debian_version = self.debian.maybe_determine_debian()
        self.assertEqual(debian_version, LATEST_DEBIAN)

    def test_no_distro_information(self):
        def lsb_which(cmd):
            return "/a/fake/path"
        def linux():
            return "Linux"
        self.debian.system = linux
        self.debian.which = lsb_which
        self.debian.get_distro_information = None
        debian_version = self.debian.maybe_determine_debian()
        self.assertEqual(debian_version, LATEST_DEBIAN)

    def test_distro_info_no_debian(self):
        def lsb_which(cmd):
            return "/a/fake/path"
        def distro_info_no_debian():
            return {}
        def linux():
            return "Linux"
        self.debian.system = linux
        self.debian.which = lsb_which
        self.debian.get_distro_information = distro_info_no_debian
        debian_version = self.debian.maybe_determine_debian()
        self.assertEqual(debian_version, LATEST_DEBIAN)

    def test_distro_info_debian(self):
        def lsb_which(cmd):
            return "/a/fake/path"
        def distro_info_debian():
            return {"ID":"Debian", "CODENAME":"willie"}
        def linux():
            return "Linux"
        self.debian.system = linux
        self.debian.which = lsb_which
        self.debian.get_distro_information = distro_info_debian
        debian_version = self.debian.maybe_determine_debian()
        self.assertEqual(debian_version, "willie")


class TestMaybeDetermineArch(unittest.TestCase):
    def setUp(self):
        self.debian = import_module("debian.builder")

    def test_not_linux(self):
        def not_linux():
            return "NotLinux"
        self.debian.system = not_linux
        debian_version = self.debian.maybe_determine_architecture()
        self.assertEqual(debian_version, "amd64")

    def test_useful_architecture(self):
        def not_linux():
            return "Linux"
        def machine_x86_64():
            return "i386"
        self.debian.system = not_linux
        self.debian.machine = machine_x86_64
        debian_version = self.debian.maybe_determine_architecture()
        self.assertEqual(debian_version, "i386")

    def test_useless_architecture(self):
        def not_linux():
            return "Linux"
        def machine():
            return "UltraSpark"
        self.debian.system = not_linux
        self.debian.machine = machine
        debian_version = self.debian.maybe_determine_architecture()
        self.assertEqual(debian_version, "amd64")


class TestDebootstrap(unittest.TestCase):
    def setUp(self):
        self.debian = import_module("debian.builder")

    def test_debootstrap_failure(self):
        def check_bootstrap():
            return 
        def determine_arch():
            return "amd64"
        def determine_debian():
            return "jessie"
        class fake_debootstrap:
            def __init__(self, *args, **kwargs):
                pass 
            def run(self):
                return None
            def result(self):
                return 1
            def runinfo(self):
                return "it ran not so well"
        self.debian.check_debootstrap = check_bootstrap
        self.debian.determine_arch = determine_arch
        self.debian.determine_debian = determine_debian
        self.debian.Debootstrap = fake_debootstrap
        with self.assertRaisesRegex(DebootstrapRuntimeError, "it ran not so well"):
            self.debian.debootstrap("/a/fake/path", "jessie", "amd64")


    def test_debootstrap_failure(self):
        def check_bootstrap():
            return 
        def determine_arch():
            return "amd64"
        def determine_debian():
            return "jessie"
        class fake_debootstrap:
            def __init__(self, *args, **kwargs):
                pass 
            def run(self):
                return None
            def result(self):
                return 0
            def runinfo(self):
                return ""
        self.debian.check_debootstrap = check_bootstrap
        self.debian.determine_arch = determine_arch
        self.debian.determine_debian = determine_debian
        self.debian.Debootstrap = fake_debootstrap
        self.debian.debootstrap("/a/fake/path", "jessie", "amd64")

