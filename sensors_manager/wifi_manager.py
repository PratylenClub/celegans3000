import subprocess
import time

def get_wifi_quality(interface = "wlan0", feature_name = "Link Quality", sep = "="):
    cmd = subprocess.Popen('iwconfig '+interface+' | grep \"'+ feature_name+'\"', shell=True, stdout=subprocess.PIPE)
    line = cmd.stdout.read()
    feature_value = line.split(feature_name)[1].split()[0].split(sep)[1].split("/")[0]
    return eval(feature_value)
"""
for i in range(100):
	print get_wifi_quality()
	time.sleep(0.5)

"""

def time2distance(interface = "en0"):    # I just use en0 to test the function on mac
	cmd = subprocess.Popen('tcpdump -c 4 -tttt -i en0 -n tcp | grep '\[\.\]' | sed -e 's/.*ack \(.*\)/\1/' | sed -e 's/,/ /' | awk  '{print $1}'') # Use Python to parse the data, it is neccesary to extract the timestamp the host IP and the Receptor IP, the seq and the tcp. Then is just resting the time.
 
