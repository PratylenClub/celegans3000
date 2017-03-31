import subprocess
import time

def get_wifi_quality(interface = "wlan0"):
    cmd = subprocess.Popen('iwconfig %s' % interface, shell=True, stdout=subprocess.PIPE)
    for line in cmd.stdout:
        if 'Link Quality' in line:
            return float(line.split(" ")[-2].split("=")[-1])
        elif 'Not-Associated' in line:
            return None
    return None

for i in range(100):
	print get_wifi_quality()
	time.sleep(0.5)