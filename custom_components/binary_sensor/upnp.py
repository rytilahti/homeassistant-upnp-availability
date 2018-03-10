"""
This platform provides a binary sensor to track the availability
 of UPNP devices, based on ssdp:alive and ssdp:byebye notifications.

For more details about this component, please refer to the documentation at
X
"""
import logging
import asyncio
import socket
import inspect
import struct
from collections import defaultdict
from pprint import pformat as pf

from homeassistant.const import CONF_NAME
from homeassistant.components.binary_sensor import BinarySensorDevice, PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

CONF_UUID = "uuid"

_LOGGER = logging.getLogger(__name__)


class SSDPDiscovery(asyncio.Protocol):
    """This needs to be moved into a new lib or replaced with something existing."""
    SSDP_HELLO = "ssdp:alive"
    SSDP_BYE = "ssdp:byebye"

    def __init__(self, callbacks):
        super().__init__()
        self._callbacks = callbacks

    def connection_made(self, transport):
        self.transport = transport
        _LOGGER.info("connected! %s" % self.transport)
        self.send_discover()

    def send_discover(self):
        payload = "M-SEARCH * HTTP/1.1\r\n" \
                  "HOST: 239.255.255.250:1900\r\n" \
                  "MAN: ssdp:discover\r\n" \
                  "MX: 2\r\n" \
                  "ST: ssdp:all\r\n"
        _LOGGER.debug("Sending %s" % payload)
        _LOGGER.info("Sending a discovery packet")
        self.transport.sendto(payload.encode(), ("239.255.255.250", 1900))

    def datagram_received(self, data, addr):
        data = data.decode()
        host, _ = addr

        payload = defaultdict(lambda:"empty")
        for idx, line in enumerate(data.rstrip('\r\n').split('\r\n')):
            if idx == 0:
                cmd, _, _ = line.split(" ")
                if cmd != "NOTIFY":
                    # print("got non-notify: %s" % data)
                    return  # break on non-notifys
                continue
            name, content = line.split(':', maxsplit=1)
            content = content.strip()
            payload[name] = content

        # _LOGGER.debug("Got a notify: %s", pf(payload))
        if payload["NTS"] == SSDPDiscovery.SSDP_HELLO:
            _LOGGER.debug("Got alive from (%s) %s!" % (host, payload["USN"]))
            for cb in self._callbacks:
                asyncio.ensure_future(cb("on", host, payload["USN"]))
        elif payload["NTS"] == SSDPDiscovery.SSDP_BYE:
            for cb in self._callbacks:
                asyncio.ensure_future(cb("off", host, payload["USN"]))
            _LOGGER.debug("Got bye from (%s) %s!" % (host, payload["USN"]))
        else:
            _LOGGER.warning("got unknown payload: %s" % payload)

    def error_received(self, exc):
        _LOGGER.error('Error received:', exc)

    def connection_lost(self, exc):
        _LOGGER.error("Socket closed, stop the event loop")


DEVICE_INFO = vol.Schema({
    vol.Required(CONF_UUID): cv.string,
    vol.Required(CONF_NAME): cv.string,
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_UUID): vol.All(cv.ensure_list, [DEVICE_INFO])
})


async def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Set up the UPNP device class for the hass platform."""
    if 'upnp' not in hass.data:
        hass.data['upnp'] = defaultdict(lambda: False)
    upnp_data = hass.data['upnp']

    device_list = {}

    for entry in config["uuid"]:
        uuid = entry["uuid"]
        name = entry["name"]
        device_list[uuid] = UPNPBinarySensor(hass, name, uuid)

    _LOGGER.info("tracking: %s" % device_list)

    async def change_cb(new_state, host, uuid):
        upnp_data[uuid] = True if new_state == "on" else False
        if uuid in device_list.keys():
            name = device_list[uuid].name
            _LOGGER.debug("Got update for %s: %s", name, new_state)
            await device_list[uuid].async_update_ha_state()
        else:
            _LOGGER.error("Got a change callback for non-existing uuid: %s" % uuid)


    # Initialize all tracked devices to be off.
    for device in device_list.values():
        _LOGGER.error("dev: %s" % device)
        upnp_data[device.uuid] = False

    def create_socket():
        """Create multicast listener socket for SSDP."""
        BROADCAST_PORT = 1900
        BROADCAST_IP = "239.255.255.250"

        addrinfo = socket.getaddrinfo(BROADCAST_IP, None)[0]

        sock = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])

        if addrinfo[0] == socket.AF_INET:  # IPv4
            sock.bind(('', BROADCAST_PORT))
            mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        else:
            _LOGGER.warning("ipv6 is not supported.")
        return sock

    ssdp = lambda: SSDPDiscovery([change_cb])
    listen = hass.loop.create_datagram_endpoint(ssdp, sock=create_socket())
    asyncio.ensure_future(listen)

    async_add_devices(device_list.values())


class UPNPBinarySensor(BinarySensorDevice):
    """A Class for an UPNP sensor."""

    def __init__(self, hass, name, uuid):
        """Initialize the binarysensor."""
        self._upnp_data = hass.data['upnp']
        self._name = name
        self._uuid = uuid

    @property
    def uuid(self):
        return self._uuid

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def name(self):
        """Return the name of the node."""
        return self._name

    @property
    def is_on(self):
        """Return boolean for device state."""
        return self._upnp_data[self._uuid]

    @property
    def device_state_attributes(self):
        """Provide attributes for display on device card."""
        return {'name': self._name,
                'uuid': self._uuid}
