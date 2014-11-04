from __future__ import print_function
import os
import subprocess


class Process(object):
    def __init__(self, command):
        self.command = command
        self._stdin = None
        self._stdout = None
        self._stdout_text = None
        self._returncode = None

    def set_stdin(self, stdin):
        self._stdin = stdin

    def set_stdout(self, stdout):
        self._stdout = stdout

    @property
    def stdin(self):
        return 'stdin'

    @property
    def stdout(self):
        if self._stdout_text is not None:
            return self._stdout_text

    @property
    def returncode(self):
        if self._returncode is not None:
            return self._returncode

    @property
    def subprocess(self):
        if self._subprocess is not None:
            return self._subprocess

    def start(self):
        self._subprocess = subprocess.Popen(
            args=self.command,
            shell=True,
            stdin=self._stdin if self._stdin else subprocess.PIPE,
            stdout=self._stdout if self._stdout else subprocess.PIPE,
        )

    def wait(self):
        self._returncode = self._subprocess.wait()
        if self._subprocess.stdout is not None:
            self._stdout_text = self._subprocess.stdout.read().decode()


    def run(self):
        self.start()
        self.wait()


    def __or__(self, other):
        return Chain([self, other])


    def __repr__(self):
        return '<Process: {command}>'.format(command=self.command)


class Chain(object):

    def __init__(self, processes):
        self.processes = processes


    def run(self):
        for proc, next_proc in zip(self.processes, self.processes[1:]):
            read, write = os.pipe()
            proc.set_stdout(write)
            next_proc.set_stdin(read)
        for proc in self.processes:
            proc.start()
        for proc in self.processes:
            proc.wait()
            if proc._stdout is not None:
                os.close(proc._stdout)


    @property
    def returncode(self):
        return self.processes[-1].returncode


    @property
    def stdout(self):
        return self.processes[-1].stdout



def chain():
    return Chain()


def process(command, env=None, clean_env=False, cwd=None, wait=False):
    p = Process(command)

    if wait:
        p.start()
        p.wait()


def run(command, env=None, cwd=None, clean_environ=False):
    pass
