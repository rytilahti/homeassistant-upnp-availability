# UPnP Availability sensor for Home Assistant

[![hacs_badge](https://img.shields.io/badge/hacs-default-orange.svg)](https://github.com/custom-components/hacs)

This custom integration allows you to track the state (on/off) of your UPnP-compatible devices, even when Home Assistant does not have support for controlling them.

The functionality is very straightforward: a new `binary_sensor` entity is created for every UPnP-compatible device in your network.
The state changes as instantaneous as they are based on the notifications sent by the devices.

## So why do you want to have this?
* Some devices have no direct support by homeassistant, but you want to do automations based on when that device gets turned on or off.
* Your device is supported by homeassistant, but is uses polling and the state changes are not updated as fast as you would like.
  * Idea: automate immediate update of the device, no more waiting for the next poll for the lights to go on!


## HACS installation

1. Search for upnp in the HACS and download it.
2. Go to Settings -> Devices & Services (or click [![Open your Home Assistant instance and show your devices.](https://my.home-assistant.io/badges/integrations.svg)](https://my.home-assistant.io/redirect/integrations/)) and select "Add integration".
3. Search for "UPnP Availability Sensor" and configure it.
4. That's it! Entities will be immediately created for the already available devices. As soon as you add (or turn on) new UPnP-supporting devices, new entities are generated to track their state.

## Manual Installation

1. Copy the `upnp_availability` directory to your `custom_components` directory.
2. Restart Home Assistant.
3. Follow the instructions above for configuration (step 2.)

### How does it work?

* This integration listens for multicast communication mandated by UPnP specifications ("ssdp:alive" and "ssdp:goodbye" notifications).
  * Limitation: the device has to be in the same network as your homeassistant instance.
* After the device-given timeout (or 1800 seconds) has lapsed without an update from the device, it will be considered to be turned off.


## Testing the discovery without homeassistant

You can try the tracker without homeassistant by executing:
```shell
python cli.py
```
On multihomed systems, you can define `--addr` for each source IP address to use for tracking:
```shell
python cli.py --addr 192.168.1.123 --addr 192.168.100.123
```
