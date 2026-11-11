#!/usr/bin/env python
# Small wrapper script for weeder2, which needs the FreqFiles directory
# where it is executed. This script allows running weeder2 from anywhere.
import os
import sys
import argparse
import subprocess as sp

# Weeder install dir
weeder_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "share", "weeder2"))
weeder_exe = "weeder2"

weeder_help = sp.check_output(
        os.path.join(weeder_dir, weeder_exe),
        stderr=sp.STDOUT).decode()
parser = argparse.ArgumentParser()
parser.add_argument("-f", dest="fname")
args, unknownargs = parser.parse_known_args()
if not args.fname:
    print(weeder_help)
    sys.exit()

fname = os.path.abspath(args.fname)
# Pass the arguments as a list: joining them into a command string and running
# that with shell=True executed shell metacharacters inside file names and
# options, and split paths that contain spaces into several arguments.
cmd = [os.path.join(".", weeder_exe), "-f", fname] + list(unknownargs)
sys.exit(sp.call(cmd, cwd=weeder_dir))
