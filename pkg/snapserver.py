import socket
import telnetlib
import logging
import json
from typing import Dict, Type

_LOGGER = logging.getLogger(__name__)


class SnapServer:
    def __init__(self,
                 host: str = '192.168.100.79',
                 port: int = 1705,
                 timeout: int = 5) -> Dict:
        """
        Initialize the object.

        host -- the Adapter managing this device
        """
        self.host = host
        self.post = port
        self.timeout = timeout

        self.tn = telnetlib.Telnet(host, port, timeout)

    def get_status(self, server=None, client=None) -> Dict:
        status = {}
        if client:
            print('{"id":1,"jsonrpc":"2.0","method":"Client.GetStatus","params":{"id":"' +
                  client.replace('snapclient-', '') + '"}}' + '\n')
            self.tn.write(('{"id":1,"jsonrpc":"2.0","method":"Client.GetStatus","params":{"id":"' +
                           client.replace('snapclient-', '') + '"}}' + '\n').encode('ascii'))
        elif server:
            self.tn.write(('{"id":1,"jsonrpc":"2.0","method":"Server.GetStatus"}' + '\n').encode('ascii'))
        else:
            return status

        try:
            print("++++")
            status = json.loads(self.tn.read_until('\n'.encode('ascii'), timeout=self.timeout))
            print("----")
        except socket.timeout:
            print("Got socket timeout, which is okay.")
        except Exception as ex:
            print("Got exception %s", ex, exc_info=True)
        return status

    @staticmethod
    def set_client_property(host, client, name, value):
        tn = telnetlib.Telnet(host, 1705, 5)
        if name == 'level':
            rq = {
                "jsonrpc": "2.0",
                "method": "Client.SetVolume",
                "params": {
                    "id": client.replace("snapclient-", ""),
                    "volume": {
                        "percent": value
                    }
                },
                "id": 2
            }
        elif name == 'muted':
            rq = {
                "jsonrpc": "2.0",
                "method": "Client.SetVolume",
                "params": {
                    "id": client.replace("snapclient-", ""),
                    "volume": {
                        "muted": value
                    }
                },
                "id": 2
            }
        else:
            return

        tn.write((json.dumps(rq)+'\n').encode('ascii'))
        # try:
        #     print("++++")
        #     print(json.loads(self.tn.read_until('\n'.encode('ascii'), timeout=5)))
        #     print("----")
        # except socket.timeout:
        #     print("Got socket timeout, which is okay.")
        # except Exception as ex:
        #     print("Got exception %s", ex, exc_info=True)

        tn.close()


class Clients:

    @staticmethod
    def discover(host: str = '192.168.100.79',
                 port: int = 1705,
                 timeout: int = 5) -> Dict:
        """
        Sends discovery message to 255.255.255.255:1780 in order
        to detect available supported devices in the local network,
        and waits for given timeout for answers from devices.

        :param host: How long to wait for responses, defaults to 3
        :param timeout: How long to wait for responses, defaults to 3
        :param port: port to send broadcast messages, defaults to 9999.
        :rtype: dict
        :return: Array of json objects {"ip", "port", "sys_info"}
        """

        tn = telnetlib.Telnet(host, port, timeout)

        tn.write(('{"id":1,"jsonrpc":"2.0","method":"Server.GetStatus"}'+'\n').encode('ascii'))

        devices = {}

        try:
            devices = json.loads(tn.read_until('\n'.encode('ascii')))
        except socket.timeout:
            print("Got socket timeout, which is okay.")
        except Exception as ex:
            print("Got exception %s", ex, exc_info=True)
        return devices
