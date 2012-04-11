import subprocess
import sys
import os
import hashlib
import time

os.system('rm -f tmp.txt')

#Setup I/O (Green = 45, Red = 60)
#Door = 44

os.system('echo 44 > /sys/class/gpio/export')
os.system('echo out > /sys/class/gpio/gpio44/direction')
os.system('echo 0 > /sys/class/gpio/gpio44/value')

os.system('echo 45 > /sys/class/gpio/export')
os.system('echo out > /sys/class/gpio/gpio45/direction')
os.system('echo 0 > /sys/class/gpio/gpio45/value')

os.system('echo 60 > /sys/class/gpio/export')
os.system('echo out > /sys/class/gpio/gpio60/direction')
os.system('echo 1 > /sys/class/gpio/gpio60/value')

#Start ZBar Process Externally; It will send most recent reading into tmp.txt
print "Starting ZBar"
os.system('./exec_zbar.sh &')
print "ZBar is Running"

#if there's a valid file here, delete it
os.system('rm -f valid.txt')
#in a while loop, compare current tmp.txt QR hash with the approved hash from the web

curr_size = 0
old_size = 0
mode = -1 #notes the state of the last trial
while (1):
	os.system('wget --quiet http://www.libetech.com/valid.txt')
	val = subprocess.check_output(["tail", "-n", "1", "tmp.txt"]).strip()
	curr_size = os.path.getsize('tmp.txt')
	if curr_size != old_size:
		mode = -1
	#print curr_size, old_size
	#print "Key from ZBAR QR Reading: %s" % val
	val_hash = hashlib.md5(val).hexdigest()
	#print "Hashed Key from ZBAR QR Reading: %s" % val_hash
	approved = subprocess.check_output(["tail", "-n", "1", "valid.txt"])
	#print "Approved Hash from Web: %s" % approved
	os.system('rm valid.txt')
	if approved in val_hash:
		if mode != 1:
			print "QR Code Accepted"
			mode=1
			os.system('echo 1 > /sys/class/gpio/gpio45/value')
			os.system('echo 1 > /sys/class/gpio/gpio44/value')
			os.system('echo 0 > /sys/class/gpio/gpio60/value')
			time.sleep(10)
			os.system('echo 0 > /sys/class/gpio/gpio45/value')
			os.system('echo 0 > /sys/class/gpio/gpio44/value')
			os.system('echo 1 > /sys/class/gpio/gpio60/value')
	else:
		if mode != 0:
			print "No Valid Code Presented"
			mode=0
			os.system('echo 1 > /sys/class/gpio/gpio60/value')
			os.system('echo 0 > /sys/class/gpio/gpio44/value')
			os.system('echo 0 > /sys/class/gpio/gpio45/value')
	old_size = curr_size
