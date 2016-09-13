#! env python3
import sys
from docker import Client
from docker.errors import NotFound

CHECK_HELLO="/usr/bin/hello"
APT_HELLO="apt-get install hello"

def debian_docker_check(docker_image):
    """debian_docker_check will perform the following check:
    * check that hello (a simple sample debian package) is not installed
    * docker run "apt-get install hello"
    * commit the resulting run
    * check that hello is now installed
    hello is chosen because its a seamless package.
    """
    dclient = Client(base_url='unix://var/run/docker.sock', 
                        version="auto")
    container = dclient.create_container(image=docker_image, 
                                        command=CHECK_HELLO)
    success = False
    try:
        dclient.start(container["Id"])
    except NotFound:
        success = True
    if not success:
        raise AssertionError("hello is not missing from the image")
    dclient.remove_container(container["Id"])
    container = dclient.create_container(image=docker_image, 
                                        command=APT_HELLO)
    response = dclient.start(container["Id"])
    dclient.wait(container)
    dclient.commit(container["Id"], docker_image)
    container = dclient.create_container(image=docker_image, 
                                        command=CHECK_HELLO,)
    response = dclient.start(container["Id"])
    dclient.wait(container)
    if dclient.logs(container["Id"]) != b'Hello, world!\n':
        raise AssertionError("apt-get failed for this image")
    dclient.remove_container(container["Id"])


if __name__ == "__main__":
    options = sys.argv[1:]
    if len(options) != 1:
        print("please specify a docker image name")
        sys.exit()
    debian_docker_check(*options)
    
