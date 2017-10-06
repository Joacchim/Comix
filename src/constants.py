"""constants.py - Miscellaneous constants."""
from __future__ import absolute_import

from src import portability

VERSION = '4.0.12'
HOME_DIR = portability.get_home_directory()
CONFIG_DIR = portability.get_config_directory()
DATA_DIR = portability.get_data_directory()
