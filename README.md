# UPnP Availability sensor for Home Assistant

This custom integration allows you to track the state (on/off) of your UPnP-compatible devices, even when Home Assistant does not have support for controlling them.

The functionality is very straightforward: a new `binary_sensor` entity is created for every UPnP-compatible device in your network.
The state changes as instantaneous as they are based on the notifications sent by the devices.

## So why do you want to have this?
* Some devices have no direct support by homeassistant, but you want to do automations based on when that device gets turned on or off.
* Your device is supported by homeassistant, but is uses polling and the state changes are not updated as fast as you would like.
  * Idea: automate immediate update of the device, no more waiting for the next poll for the lights to go on!


## Installation

1. Copy the `upnp_availability` directory to your `custom_components` directory. Restart Home Assistant.
2. Go to Configuration -> Integrations -> Set up a new integration and search for "UPnP Availability".
3. That's it! Entities will be immediately created for the already available devices. As soon as you add (or turn on) new UPnP-supporting devices, new entities are generated to track their state. 

### How does it work?

* This integration listens for multicast communication mandated by UPnP specifications ("ssdp:alive" and "ssdp:goodbye" notifications).
  * Limitation: the device has to be in the same network as your homeassistant instance.
* After the device-given timeout (or 1800 seconds) has lapsed without an update from the device, it will be considered to be turned off.
