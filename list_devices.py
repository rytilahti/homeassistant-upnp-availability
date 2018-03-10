import upnpclient

for dev in upnpclient.discover():
    print("Device: %s, UUID: %s" % (dev, dev.udn))
