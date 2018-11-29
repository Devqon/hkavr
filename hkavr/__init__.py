#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automation Library for Harman Kardon AVR receivers.
:copyright: (c) 2018 by Sander Geerts.
:license: MIT, see LICENSE for more details.
"""

# Set default logging handler to avoid "No handler found" warnings.
import logging

# Import hkavr module
from .hkavr import HkAVR

logging.getLogger(__name__).addHandler(logging.NullHandler())

__title__ = "hkavr"
__version__ = "0.0.4"