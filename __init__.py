import importlib.metadata as metadata

__version__ = metadata.version(__name__)
__author__ = metadata.metadata(__name__)['Author']
__license__ = metadata.metadata(__name__)['License']
__all__ = [__name__]

from kanjivg import *
from kvg_lookup import *
from kvg import *