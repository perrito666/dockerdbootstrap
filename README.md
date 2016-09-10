Autodock is a set of utilities that aim to:
* Produce a debian image folder
* Turn the debian image into a docker one
* Test the docker debian image.
The tools are bundled as a script that should run in autonomous way and provide reporting after the process.
The tooling is organized as follows:
* debian image creator lib: explain
* docker image creator lib: explain
* debian docker image tests: explain
* report gathering: explain
The separation is to allow pluggability, on a usual project lifetime one of the clearly separate parts of the tooling
might be replaced such as docker images or debian as a distro.
