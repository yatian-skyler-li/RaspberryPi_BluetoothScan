# RaspberryPi_BluetoothScan
This project aims to monitor the volume of visitors and classify their initial activities in urban green space by leveraging Raspberry Pi devices equipped with cameras and Bluetooth technology. 

# Devices required
- A Raspberry Pi 4 with bluetooth on and a SD card are required for the script to run. Keyboard, mouse and monitor are necessary if there is no device to remote control the Raspberry Pi by SSH.
- A laptop is preferred to use for SSH connection with the Rasberry Pi. There is no restriction on the system of the laptop.
  
# Basic setup
- Raspberry pi setting -> Preferences -> raspberry pi configuration -> interfaces -> SSH, VNC, I2C, SPI, remote GPIO (on)/All on
- Get Raspberry Pi IP address in the terminal: hostname -I

# Camera scan
- Video scanning can be done if Raspberry Pi camera is available
- Example code in the termial: sudo libcamera-vid -t 5000 -o test.h264
- More complex features could be added by writing the commands in the script, like start time, duration, output directory.

# Scripts Available
The scripts are used to collect bluetooth device data near the Rasspberry Pi for geospatial models.
- "DeviceScan_RSSI" can scan the bluetooth devices nearby with Received Signal Strength Indicator (RSSI) threshold, which is a basic scan script used to test the Bluetooth low energy (LE) scan.
- "DeviceScan_BREDR" will scan the classic Bluetooth devices (Bluetooth basic rate/enhanced data rate - BR/EDR ) near the Raspberry Pi.
The latest script in this project could set up the scanning duration and start time, with the options to choose scanning mode (LE/BREDR). Since Mr.Mingze Chen also contributed to this script, it won't be included in this repository until the end of the this research project. 
