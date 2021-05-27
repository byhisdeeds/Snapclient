"""TP-Link adapter for WebThings Gateway."""

from gateway_addon import Adapter, Database, IpcClient
from pyHS100 import Discover, SmartBulb, SmartPlug, SmartStrip

from .snapclient_device import SnapClientPlayer, TPLinkBulb, TPLinkPlug
from .snapserver import Clients, SnapServer


_TIMEOUT = 5


class SnapclientAdapter(Adapter):
    """Adapter for Snapclient smart home music players."""

    def __init__(self, verbose=True):
        """
        Initialize the object.

        verbose -- whether or not to enable verbose logging
        """

        self.name = self.__class__.__name__
        Adapter.__init__(self,
                         'snapclient',
                         'snapclient',
                         verbose=verbose)

        # self.manager_proxy = SnapclientAddonManagerProxy(self.package_name, verbose=verbose)
        # self.manager_proxy.add_property_change_listener(self.on_property_change_listener)

        self.server = None
        self.pairing = False
        self.start_pairing(_TIMEOUT)

    def _add_from_config(self):
        """Attempt to add all configured devices."""
        database = Database('snapclient')
        if not database.open():
            return

        config = database.load_config()
        database.close()

        if not config or 'addresses' not in config:
            return

        for address in config['addresses']:
            print("===ADDRESSES===", address)
            try:
                self.server = SnapServer(host=address, timeout=_TIMEOUT) if self.server is None else self.server
                # servers = Clients.discover(host=address, timeout=_TIMEOUT)
                servers = self.server.get_status(server=address)
                if "result" in servers:
                    if "server" in servers["result"] and "groups" in servers["result"]["server"]:
                        for group in servers["result"]["server"]["groups"]:
                            for client in group["clients"]:
                                print("@@@@@@@@ CLIENT: ", client)
                                if self.pairing:
                                    self._add_device(client)
            except (OSError, UnboundLocalError) as e:
                print('Failed to connect to {}: {}'.format(address, e))
                continue

    def start_pairing(self, timeout):
        """
        Start the pairing process.

        timeout -- Timeout in seconds at which to quit pairing
        """
        if self.pairing:
            return

        self.pairing = True

        self._add_from_config()

        # self.server = SnapServer(host=address, timeout=_TIMEOUT) if self.server is None else self.server
        # # servers = Clients.discover(timeout=min(timeout, _TIMEOUT))
        # servers = Clients.discover(timeout=min(timeout, _TIMEOUT))
        # if self.pairing and "result" in servers:
        #     if "server" in servers["result"] and "groups" in servers["result"]["server"]:
        #         for group in servers["result"]["server"]["groups"]:
        #             for client in group["clients"]:
        #                 print("@@@@@@@@ CLIENT: ", client)
        #                 if self.pairing:
        #                     self._add_device(client)

        self.pairing = False

    def _add_device(self, dev):
        _id = 'snapclient-' + dev["id"]
        if _id not in self.devices:
            device = SnapClientPlayer(self, _id, dev)
            self.handle_device_added(device)

    def cancel_pairing(self):
        """Cancel the pairing process."""
        self.pairing = False

    def get_client_status(self, id):
        result = {}
        print("!!!!!!!!!!!!!!!!!!! STATUS - ID", id)
        if self.server:
            try:
                result = self.server.get_status(client=id)
                print(">>>>>>>>>", result)
            except (OSError, UnboundLocalError) as e:
                print('Failed to connect to {}: {}'.format(address, e))
            return result

    def on_property_change_listener(self, msg):
        """Read a message from the IPC socket."""
        # if self.verbose:
        #     print('AddonManagerProxy: recv:', msg)

        # msg_type = msg['messageType']
        print("++++++++DEVICE_PROPERTY_CHANGED_NOTIFICATION++++++++", msg["data"])
