# Script used to scan BR/EDR bluetooth devices near the Raspberry Pi
# Start time and duration of the scanning can be defined using --start and --duration in the terminal
# Import necessary libraries
from optparse import OptionParser
import dbus
import dbus.mainloop.glib
from gi.repository import GLib
from datetime import datetime, timedelta
import time

# Dictionary to store discovered devices
devices = {}
# List of devices to be ignored
devs_tobe_ignored = None
# D-Bus service and interface names for BlueZ
SERVICE_NAME = 'org.bluez'
ADAPTER_INTERFACE = 'org.bluez.Adapter1'
DEVICE_INTERFACE = 'org.bluez.Device1'

def interfaces_added(path, interfaces):
    """
    Callback function for when a new device interface is added.
    """
    properties = interfaces['org.bluez.Device1']
    if not properties:
        return

    dev_info = {}
    # Get device address
    if "Address" in properties:
        if properties['Address'] in devs_tobe_ignored:
            return
        dev_info['Address'] = properties['Address']
    else:
        dev_info['Address'] = 'unknown'

    # Get device name
    if "Name" in properties:
        dev_info['Name'] = properties['Name'].replace('&', '_').replace('?', '_')
    else:
        dev_info['Name'] = 'unknown'

    # Get device RSSI
    if 'RSSI' in properties:
        dev_info['RSSI'] = properties['RSSI']
    else:
        dev_info['RSSI'] = 0

    # Check if the device is already in the list
    if path in devices:
        print(f"\nDevice discovered, but the device {dev_info['Address']} is already in the current list.\n")
    else:
        devices[path] = dev_info

    msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}]: Device discovered - Address: {dev_info['Address']}, Name: {dev_info['Name']}, RSSI: {dev_info['RSSI']}"
    print(msg)

def interfaces_removed(path, unknowns):
    """
    Callback function for when a device interface is removed.
    """
    if path in devices:
        msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}]: Device (Address: {devices[path]['Address']}) signal lost, no longer tracking it."
        devices.pop(path)
        print(msg)
    else:
        print(f"\nDevice lost, but the information for this device {path} is not in the current list.\n")

def properties_changed(interface, changed, invalidated, path):
    """
    Callback function for when properties of a device change.
    """
    if interface != "org.bluez.Device1":
        return

    if path in devices and "RSSI" in changed:
        msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}]: Device (Address: {devices[path]['Address']}) RSSI changed to {changed['RSSI']}"
        devices[path]['RSSI'] = changed['RSSI']
        print(msg)

def find_adapter():
    """
    Find the Bluetooth adapter to use for device discovery.
    """
    remote_om = dbus.Interface(bus.get_object(SERVICE_NAME, "/"), "org.freedesktop.DBus.ObjectManager")
    objects = remote_om.GetManagedObjects()
    for path, interfaces in objects.items():
        if ADAPTER_INTERFACE in interfaces:
            return dbus.Interface(bus.get_object(SERVICE_NAME, path), "org.freedesktop.DBus.Properties")
    return None

def start_discovery(adapter, scan_filter):
    """
    Start the Bluetooth device discovery.
    """
    adapter.SetDiscoveryFilter(scan_filter)
    adapter.StartDiscovery()
    print("Started Bluetooth device discovery")

def stop_discovery(adapter):
    """
    Stop the Bluetooth device discovery.
    """
    adapter.StopDiscovery()
    print("Stopped Bluetooth device discovery")
    mainloop.quit()

if __name__ == '__main__':
    # Initialize D-Bus main loop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    # Set up command-line options
    parser = OptionParser(
        usage='%prog [options]',
        description='Observe nearby Bluetooth devices (support BR/EDR)',
        version='0.0.1'
    )

    parser.add_option('-u', "--uuids", action="store", type="string", dest="uuids", help="Filtered service UUIDs [uuid1,uuid2,...]")
    parser.add_option("-r", "--rssi", action="store", type="int", dest="rssi", help="RSSI threshold value")
    parser.add_option("-p", "--pathloss", action="store", type="int", dest="pathloss", help="Pathloss threshold value")
    parser.add_option("-t", "--transport", action="store", type="string", dest="transport", help="Type of scan to run (le/bredr/auto)")
    parser.add_option('-d', "--devs", action="store", type="string", dest="devs", help="Devices to be ignored [dev_addr1,dev_addr2,...]")
    parser.add_option('-s', "--start", action="store", type="string", dest="start_time", help="Start time for scanning (format: HH:MM)")
    parser.add_option('-n', "--duration", action="store", type="int", dest="duration", help="Duration of the scanning in seconds")

    (options, args) = parser.parse_args()

    # Find the Bluetooth adapter
    adapter = find_adapter()

    # Set up signal receivers
    bus.add_signal_receiver(interfaces_added, bus_name=SERVICE_NAME, dbus_interface="org.freedesktop.DBus.ObjectManager", signal_name="InterfacesAdded")
    bus.add_signal_receiver(interfaces_removed, bus_name=SERVICE_NAME, dbus_interface="org.freedesktop.DBus.ObjectManager", signal_name="InterfacesRemoved")
    bus.add_signal_receiver(properties_changed, bus_name=SERVICE_NAME, dbus_interface="org.freedesktop.DBus.Properties", signal_name="PropertiesChanged", arg0="org.bluez.Device1", path_keyword="path")

    # Configure scan filter
    scan_filter = dict()

    if options.uuids:
        scan_filter.update({'UUIDs': options.uuids.split(',')})

    if options.rssi:
        scan_filter.update({'RSSI': dbus.Int16(options.rssi)})

    if options.pathloss:
        scan_filter.update({'Pathloss': dbus.UInt16(options.pathloss)})

    # Update the transport type for BR/EDR scan
    scan_filter.update({'Transport': 'bredr'})

    if options.devs:
        devs_tobe_ignored = options.devs.replace(' ', '').split(',')
    else:
        devs_tobe_ignored = []

    # Get current time and calculate the start time and duration for the scan
    if options.start_time:
        start_time = datetime.strptime(options.start_time, "%H:%M").time()
        current_time = datetime.now().time()

        # Calculate the delay until the start time
        delay = (datetime.combine(datetime.today(), start_time) - datetime.combine(datetime.today(), current_time)).total_seconds()
        if delay < 0:
            delay += 86400  # Add a day if the start time is for the next day

        print(f"Scheduled to start scanning at {options.start_time}, in {delay} seconds.")
        time.sleep(delay)

    if options.duration:
        end_time = datetime.now() + timedelta(seconds=options.duration)
        GLib.timeout_add_seconds(options.duration, stop_discovery, adapter)
        print(f"Scanning will run for {options.duration} seconds, until {end_time.strftime('%H:%M:%S')}")

    # Start device discovery with the specified filter
    start_discovery(adapter, scan_filter)

    # Run the main loop
    mainloop = GLib.MainLoop()
    mainloop.run()
