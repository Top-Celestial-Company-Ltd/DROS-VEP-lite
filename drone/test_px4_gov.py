import subprocess
import time
import os

px4_bin = "/home/ai_user/px4_build/PX4-Autopilot/build/px4_sitl_default/bin/px4"
px4_dir = "/home/ai_user/px4_build/PX4-Autopilot/build/px4_sitl_default"
px4_etc = "/home/ai_user/px4_governed_etc"

print("Starting PX4 with governed etc...")
p = subprocess.Popen([px4_bin, "-d", px4_etc], cwd=px4_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)

print("Checking UDP listening ports:")
res = subprocess.run(["ss", "-ulpn"], capture_output=True, text=True)
for line in res.stdout.splitlines():
    if any(k in line for k in ["1857", "1428", "1303", "1458", "1454"]):
        print(line)

p.kill()
p.wait()
print("PX4 terminated.")
