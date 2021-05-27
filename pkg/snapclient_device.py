"""Snapclient adapter for WebThings Gateway."""

from gateway_addon import Device
import threading
import time

from .snapclient_property import SnapClientProperty
from .util import hsv_to_rgb


_POLL_INTERVAL = 5


class SnapClientPlayer(Device):
    """SnapClient player type."""

    def __init__(self, adapter, _id, dev, index=-1):
        """
        Initialize the object.

        adapter -- the Adapter managing this device
        _id -- ID of this device
        hs100_dev -- the pyHS100 device object to initialize from
        index -- index inside parent device
        """
        Device.__init__(self, adapter, _id)
        self.dev = dev
        self.index = index
        self._type.extend(['SnapClient Player'])
        self.mac = dev["host"]["mac"] if "host" in dev and "mac" in dev["host"] else False
        self.description = dev["host"]["ip"] if "host" in dev and "ip" in dev["host"] else "unknown"
        self.name = dev["host"]["name"] if "host" in dev and "name" in dev["host"] else self.description
        # connected = dev["connected"] if "connected" in dev else False
        # muted = dev["config"]["volume"]["muted"] if "config" in dev and "volume" in dev["config"] and "muted" in dev["config"]["volume"] else False
        # volume = dev["config"]["volume"]["percent"] if "config" in dev and "volume" in dev["config"] and "percent" in dev["config"]["volume"] else 0
        # sysinfo = dev["host"] if "host" in dev else {}

        self.properties['level'] = SnapClientProperty(
            self,
            'level',
            {
                '@type': 'VolumeProperty',
                'title': 'Volume',
                'type': 'integer',
                'unit': 'percent',
                'minimum': 0,
                'maximum': 100,
            },
            self.volume(dev)
        )

        self.properties['muted'] = SnapClientProperty(
            self,
            'muted',
            {
                '@type': 'OnOffProperty',
                'title': 'Mute',
                'type': 'boolean',
            },
            self.is_muted(dev)
        )

        self.properties['active'] = SnapClientProperty(
            self,
            'active',
            {
                '@type': 'BooleanProperty',
                'title': 'Active',
                'type': 'boolean',
                'readOnly': True
            },
            self.is_active(dev)
        )

        # t = threading.Thread(target=self.poll)
        # t.daemon = True
        # t.start()

    def poll(self):
        """Poll the device for changes."""
        print("starting device property polling thread for {} with internal {}".format(self.id, _POLL_INTERVAL))
        while True:
            time.sleep(_POLL_INTERVAL)
            try:
                print("$$$$$$$$$$ POLLING $$$$$$$$$$$$$$$$")
                status = self.adapter.get_client_status(self.id)
                print("$$$$$$$$$$ POLLING RESULT $$$$$$$$$$$$$$$$", status)

                for prop in self.properties.values():
                    prop.update(status)
            except SmartDeviceException as ee:
                print(ee)

    @staticmethod
    def is_active(dev):
        """
        Determine whether or not the player is on.

        player_state -- current state of the snapclient player
        """
        return dev["connected"] if "connected" in dev else False

    @staticmethod
    def is_muted(dev):
        """
        Determine whether or not the player is on.

        player_state -- current state of the snapclient player
        """
        return dev["config"]["volume"]["muted"] if "config" in dev and "volume" in dev["config"] and "muted" in dev["config"]["volume"] else False

    @staticmethod
    def volume(dev):
        """
        Determine the current volume of the player.

        volume_state -- current level of the player volume
        """
        return int(dev["config"]["volume"]["percent"]) if "config" in dev and "volume" in dev["config"] and "percent" in dev["config"]["volume"] else 0
