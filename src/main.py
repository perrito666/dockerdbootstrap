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
        debootstrap(join(tempdir, "build"), debian_version)
        img_name = "autodeb{:f}".format(time.time().real)
        db = DockerBuilder(tempdir, img_name)
        db.run()
        print("{:s} image was added to docker".format(img_name))


if __name__ == "__main__":
    main()
