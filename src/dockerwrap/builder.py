#! env python3

from io import BytesIO
from docker import Client
import tarfile
import sys

class DockerBuilder:
    def __init__(self, chroot_path, image_name):
        """DockerBuilder provides a simple way to import a docker image from
        a folder on disk
        """
        self._chroot_path = chroot_path
        self._in_memory_tar = BytesIO()
        self._image_name=image_name

    def _build_tar(self):
        """_build_tar will load the contents of the folder passed on
        instantiation into an in-memory tar held in a bytes buffer
        """
        with tarfile.open(mode="w", fileobj=self._in_memory_tar) as tar:
            tar.add(self._chroot_path, arcname="/", recursive=True)
        # I am not sure that context closing will do this.
        self._in_memory_tar.seek(0)
            
    def run(self):
        """run creates the in-nemory tar from the passed folder and imports
        the image into docker
        """
        # lets try if connection to the server is even possible 
        # before building tar
        dclient = Client(base_url='unix://var/run/docker.sock', 
                        version="auto")
        self._build_tar()
        dclient.import_image_from_data(self._in_memory_tar.read(), 
                                       repository=self._image_name)
        dclient.import_image_from_stream

if __name__=="__main__":
    options = sys.argv[1:]
    db = DockerBuilder(*options)
    db.run()
