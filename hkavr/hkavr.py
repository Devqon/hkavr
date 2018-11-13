#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module implements the interface to Harman Kardon AVR receivers.

:copyright: (c) 2018 by Sander Geerts.
:license: MIT, see LICENSE for more details.
"""

import logging
import socket
import requests

_LOGGER = logging.getLogger("HkAVR")

DEFAULT_SOURCES = ["Disc", "STB", "Cable Sat", "Media Server", "DVR", "Radio", "TV", "USB", "Game",
            "Home Network", "AUX"]

COMMAND_MAPPING = {
    "POWER_OFF": "power-off",
    "POWER_ON": "power-on",
    "SLEEP": "sleep",
    "VOLUME_UP": "volume-up",
    "VOLUME_DOWN": "volume-down",
    "MUTE_TOGGLE": "mute-toggle",
    "PLAY": "play",
    "PAUSE": "pause",
    "NEXT": "next",
    "PREVIOUS": "previous",
    "SOURCE": "source-selection",
    "HEARTBEAT": "heart-alive"
}

POWER_ON = "ON"
POWER_OFF = "OFF"
POWER_STANDBY = "STANDBY"
STATE_ON = "on"
STATE_OFF = "off"

class HkAVR:
    """Representing a Harman Kardon AVR Device."""

    def __init__(self, host, port=10025, name=None):
        """
        Initialize MainZone of HkAVR.

        :param host: IP or HOSTNAME.
        :type host: str

        :param port: port.
        :type host: number

        :param name: Device name, if None FriendlyName of device is used.
        :type name: str or None
        """
        self._name = name
        self._host = host
        self._port = port
        # For now only support for main zone
        self._zone = "Main Zone"
        self._mute = STATE_OFF

        self._state = None
        self._power = None
        self._socket = self._get_new_socket()

        self.update()

    def _get_new_socket(self):
        try:
            _new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _new_socket.connect((self._host, self._port))
            return _new_socket
        except ConnectionError as connection_error:
            _LOGGER.warning("Connection error: %s", connection_error)
            return None
        except socket.gaierror as socket_gaierror:
            _LOGGER.warning("Address-related error: %s", socket_gaierror)
            return None
        except socket.error as socket_error:
            _LOGGER.warning("Connection error: %s", socket_error)
            return None

    def _exec_appcommand_post(self, command, param):
        """
        Prepare xml command for AVR
        """
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <harman>
            <avr>
                <common>
                    <control>
                        <name>""" + command + """</name>
                        <zone>""" + self._zone + """</zone>
                        <para>""" + param + """</para>
                    </control>
                </common>
            </avr>
        </harman>"""
        command = """POST AVR HTTP/1.1\r\nHost: :""" + str(self._port) \
                  + """\r\nUser-Agent: Harman Kardon AVR Remote """\
                  + """Controller /2.0""" \
                  + """\r\nContent-Length: """ + str(xml.__len__()) \
                  + """\r\n\r\n""" + xml

        if self._socket is None:
            self._socket = self._get_new_socket()
        if self._socket is None:
            _LOGGER.warning("Cannot connect to AVR")
            return
        try:
            resp = self._socket.sendto(command.encode(),
                                       (self._host, self._port))
            if resp == 0:
                self._socket.close()
                self._socket = None
                _LOGGER.warning("Send fail, disconnecting from AVR")
                return False
            return True
        except (BrokenPipeError, ConnectionError) as connect_error:
            _LOGGER.warning("Connection error, retrying. %s", connect_error)
            self._socket = None
            self._socket = self._get_new_socket()
            if self._socket is not None:
                # retrying after broken pipe error
                resp = self._socket.sendto(command.encode(), (self._host, self._port))

                return resp != 0

    def send_command(self, command, param=''):
        comm = COMMAND_MAPPING[command]
        return self._exec_appcommand_post(comm, param)

    def update(self):
        """
        Get the latest status information from device.
        """
        if (self.send_command("HEARTBEAT")):
            self._power = POWER_ON
            self._state = STATE_ON
        else:
            self._power = POWER_OFF
            self._state = STATE_OFF

        return True

    def _get_receiver_sources(self):
        """
        Get sources list.
        """
        return DEFAULT_SOURCES

    @property
    def zone(self):
        """Return Zone of this instance."""
        return self._zone

    @property
    def name(self):
        """Return the name of the device as string."""
        return self._name

    @property
    def host(self):
        """Return the host of the device as string."""
        return self._host

    @property
    def power(self):
        """
        Return the power state of the device.
        Possible values are: "ON", "STANDBY" and "OFF"
        """
        return self._power

    @property
    def state(self):
        """
        Return the state of the device.

        Possible values are: "on", "off"
        """
        return self._state

    @property
    def muted(self):
        """
        Boolean if volume is currently muted.
        Return "True" if muted and "False" if not muted.
        """
        return bool(self._mute == STATE_ON)

    @property
    def port(self):
        """Return the receiver's port."""
        return self._port

    def power_on(self):
        """Turn off receiver via command."""
        try:
            if self.send_command("POWER_ON"):
                self._power = POWER_ON
                self._state = STATE_ON
                return True
            else:
                return False
        except requests.exceptions.RequestException:
            _LOGGER.error("Connection error: power on command not sent.")
            return False

    def power_off(self):
        """Turn off receiver"""
        try:
            if self.send_command("POWER_OFF"):
                self._power = POWER_OFF
                self._state = STATE_OFF
                return True
            else:
                return False
        except requests.exceptions.RequestException:
            _LOGGER.error("Connection error: power off command not sent.")
            return False

    def sleep(self):
        """Sleep"""
        try:
            if self.send_command("SLEEP"):
                return True
            else:
                return False
        except requests.exceptions.RequestException:
            _LOGGER.error("Connection error: sleep command not sent.")
            return False

    def volume_up(self):
        """Volume up receiver"""
        try:
            return bool(self.send_command("VOLUME_UP"))
        except requests.exceptions.RequestException:
            _LOGGER.error("Connection error: volume up command not sent.")
            return False

    def volume_down(self):
        """Volume down receiver"""
        try:
            return bool(self.send_command("VOLUME_DOWN"))
        except requests.exceptions.RequestException:
            _LOGGER.error("Connection error: volume down command not sent.")
            return False

    def set_volume(self, volume):
        # not supported
        return False

    def select_source(self, source):
        try:
            return bool(self.send_command("SOURCE", source))
        except requests.exceptions.RequestException:
            _LOGGER.error("Connection error: select source command not sent.")
            return False

    def mute(self, mute):
        """Mute receiver"""
        try:
            if (mute and self._mute == STATE_OFF):
                if self.send_command("MUTE"):
                    self._mute = STATE_ON
                    return True
                else:
                    return False
            elif not mute and self._mute == STATE_ON:
                if self.send_command("MUTE"):
                    self._mute = STATE_OFF
                    return True
                else:
                    return False
        except requests.exceptions.RequestException:
            _LOGGER.error("Connection error: mute command not sent.")
            return False