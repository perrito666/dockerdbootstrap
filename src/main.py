#!env python3
import sys
import time
from os.path import join
from tempfile import TemporaryDirectory
from logging import basicConfig, DEBUG 

from debian.builder import debootstrap
from dockerwrap.builder import DockerBuilder

def parse_args():
    args = sys.argv[1:]
    if len(args) > 0:
        return args[0]

def main():
    basicConfig(level=DEBUG)
    debian_version = parse_args()
    with TemporaryDirectory() as tempdir:
        tempdir = join(tempdir, "build")
        debootstrap(tempdir, debian_version)
        img_name = "autodeb{:f}".format(time.time().real)
        db = DockerBuilder(tempdir, img_name)
        db.run()
        # TODO Test docker image and print test
        # do this by running hello, checking it fails and then installing
        # and committing the changes.
        print("{:s} image was added to docker".format(img_name))


if __name__ == "__main__":
    main()
