#!/usr/bin/env python3

"""
This module defines logging format.

Author:
    Adrien LECHARNY - April 2025
"""

# Standard library imports
import logging

FORMAT = "%(asctime)-15s [%(levelname)s] [%(filename)s:%(lineno)s %(threadName)s %(funcName)s()] %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger("project_logger")
