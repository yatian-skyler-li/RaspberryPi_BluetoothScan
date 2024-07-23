import subprocess

# Scan devices that met the minimum RSSI threshold
def scan_for_devices(min_rssi):
    devices = []
    process = subprocess.Popen(['sudo', 'hcitool', 'lescan'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        output = process.stdout.readline().decode('utf-8').strip()
        if output == '':
            break
        parts = output.split()
        if len(parts) == 2 and parts[1] != '(unknown)':
            rssi = int(parts[1], 16) - 256
            if rssi >= min_rssi:
                devices.append((parts[0], rssi))
    process.terminate()
    return devices

# Set the minimum RSSI threshold
min_rssi_threshold = -70

# Scan for devices and filter by RSSI
devices = scan_for_devices(min_rssi_threshold)

# Print the filtered devices
for device in devices:
    print(f"Device: {device[0]}, RSSI: {device[1]} dBm")

# The output of the print result in terminal could be store in a txt file for further analysis