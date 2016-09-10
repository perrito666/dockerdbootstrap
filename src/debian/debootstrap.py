#! env python3
from pexpect import run, TIMEOUT
from shutil import which
from logging import getLogger

log = getLogger("debootstrap.debootstrap")

DEBOOTSTRAP_COMMAND="debootstrap"

class DebootstrapRuntimeError(Exception):
    def __init__(self, result, output):
        self._result = result
        self._output = output

    def result(self):
        return self._result

    def details(self):
        return self._ouput

def print_ticks(d):
    # some educated guessing should be done regarding the encoding.
    log.info(d.get("child_result_list", [""])[-1].decode("utf-8").strip("\r\n"))

class Debootstrap:
    def __init__(self, destination, target_version, arch):
        """Debootstrap is a convenience wrap around running debootstrap
        executable
        """
        self._destination = destination
        self._target_version = target_version
        self._arch = arch
        self._executable = which(DEBOOTSTRAP_COMMAND)
        #--- output
        self._result_stdout = ""
        self._result = 0
        
    def run(self):
        """run will execute debootstrap with the parameters configured
        for this wrapper and store the result"""
        command = " ".join([DEBOOTSTRAP_COMMAND, 
                "--arch", 
                self._arch, 
                self._target_version, 
                self._destination])
        self.result_stdout, self._result = run(command, withexitstatus=True, 
                                    events=[('\n',print_ticks)], timeout=None)

    def result(self):
        """result returns the exit status the last run of debootstrap command.
        """
        return self._result

    def runinfo(self):
        """runinfo returns the output of the last debootstrap run.
        """
        return self._result_stdout

