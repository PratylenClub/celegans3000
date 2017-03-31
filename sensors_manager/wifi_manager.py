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
