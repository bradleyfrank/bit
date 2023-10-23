#!/usr/bin/env python3

import subprocess

class CmdProc():
    def __init__(self, command: str) -> None:
        self.cmd = command.split()
        try:
            self.result = subprocess.run(self.cmd, capture_output=True, check=False)
        except Exception as err:
            print(err)
        self.rc = self.result.returncode
        self.stdout = self.result.stdout.decode("UTF-8")
        self.stderr = self.result.stderr.decode("UTF-8")
