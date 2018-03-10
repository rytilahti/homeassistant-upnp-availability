# PoC UPnP binary sensor for Home Assistant

* Get instant notifications when turning UPnP-enabled devices on and off.
* Works by listening for SSDP "ssdp:alive" and "ssdp:goodbye" notifications, for this the device has to be in the same network.
* May or may not work for you, different devices seem to behave differently regarding to their notifications.

# Installation

1. This sensor requires upnpclient to be installed.
```
pip install upnpclient
```

2. Copy custom_components/binary_sensor/upnp.py to its correct place.

3. Find out the UUIDs of the devices you want to track somehow, there is a small script in this repository to do that.
```
python list_devices.py
```

4. Configure home assistant.

```binary_sensor:
  - platform: upnp
    uuid:
      - uuid: uuid:78a0716b-3f00-XXXXXXXXXXXXXXXXXXXXXX
        name: xbox
      - uuid: uuid:00000000-0000-XXXXXXXXXXXXXXXXXXXXXX
        name: xxxx
```