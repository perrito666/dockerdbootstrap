# Autodock #

### Rationale ###
Autodock aims to be a base for debian-based docker image automation.
As a list of components its ideal to leverage to automate several kind
of images in a reproducible manner.
As a side effect it can be used to build isolated environments to test
software packaging automatically (you can just build, patch, add your package
and then run a set of tests).

### Components ###
Autodock is a set of utilities that aim to:
* Produce a debian chroot
* Turn the debian chroot into a docker image.
* Test the docker debian image.

### Layout ###
The tooling is organized as follows:
* debian image creator lib debian: produces the debian chroot.
* docker image creator lib docker: produces the docker image.
* resulting imge tester docktest: checks that the image is a working debian by apt-getting hello.
The separation is to allow pluggability, on a usual project lifetime one of the clearly separate parts of the tooling
might be replaced such as docker images or debian as a distro.

### Requirements ###
To run the main script in this project you will need:
* python => 3.4 (with the requirements.txt packages installed)
* debootstrap
* docker (on ubuntu the package is called docker.io)
* sudo or equivalent permissions (debootstrap requires it for chrooting)
* On certain versions of ubuntu (such as aws), you might need to install:
```
debian-archive-keyring debian-keyring debian-ports-archive-keyring
```

### Running ###
The tools are bundled as a script that should run in autonomous way and output
some useful log information.
In the future, it would be good to be able to write reporting/logs into an output
digests.
A basic run of this tool can be achieved by running the supplied main.py script:
```bash
# remember that sudo is required by debootstrap
sudo python main.py
```
A run will:
* Create a temp folder.
* Build a debian chroot inside the temp folder.
* Create a docker image from the chroot.
* run apt-get install hello in a container for the generated image.
* commit the resulting container
* check the apt-get command was succesful.
To simplify running a bash runner is provided that will put the module in the 
pytho path and run with some default parameters.
```bash
# remember that sudo is required by debootstrap
sudo ./runner.sh
```

The separate components can be used as standalone utils too:
_Note_: the following commands assume that repository/src is on your pytho path.
*debootstrap chroot*:
```bash
sudo python -m debian.builder <image folder> [version shortname] [arch]
```
*docker image*
```bash
sudo python -m docker.builder <chroot folder> <image name>
```

### Testing ###
There are tests available for the relevant parts of the code and can be run with.
```bash
python -m unittest <path to repo>/src/tests/debootstrapbuilder.py
```

### Considerations ###
*Docker*: The connection to docker is quite crude and assumes you are just connecting as root
on a vanilla docker install in ubuntu.

*Security*: The debian image is based on a basic debian debootstrap, this is by no means secure
its just a vanilla debian.

*Repeatability*: If you want this to work fast and reliably I would suggest having a proxy for
packages, this program takes no special measures to prevent debootstrap from failing due to
a network issue (plus it downloads a hefty ~250M per run)

*Memory*: Even if is not a big number for today de facto standards, bear in mind that this program
will load, when used via the main.py, a tar file containing the size of the debootrsaped chroot
in memory at some point in the run.
If used as a library, the same consideration applies, the passed image folder will be loaded in
memory as a tar file.
