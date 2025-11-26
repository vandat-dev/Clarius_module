"""
Clarius Module

A modular package for Clarius ultrasound probe integration.

Usage:
    from clarius import ClariusCasterClient, CMD_FREEZE
    
    client = ClariusCasterClient()
    client.connect("10.3.5.96", 5828)
    image = client.get_pil_image()
"""

from initial.client import ClariusCasterClient
from initial.constants import (
    CMD_FREEZE,
    CMD_CAPTURE_IMAGE,
    CMD_CAPTURE_CINE,
    CMD_DEPTH_DEC,
    CMD_DEPTH_INC,
    CMD_GAIN_DEC,
    CMD_GAIN_INC,
    CMD_B_MODE,
    CMD_CFI_MODE,
)
from initial.data_store import CasterData, global_caster_data

# Optional: Import streaming client (requires grpcio)
try:
    from clarius.streaming_client import ClariusStreamingClient
    _HAS_STREAMING = True
except ImportError:
    ClariusStreamingClient = None
    _HAS_STREAMING = False

__all__ = [
    'ClariusCasterClient',
    'CasterData',
    'global_caster_data',
    'CMD_FREEZE',
    'CMD_CAPTURE_IMAGE',
    'CMD_CAPTURE_CINE',
    'CMD_DEPTH_DEC',
    'CMD_DEPTH_INC',
    'CMD_GAIN_DEC',
    'CMD_GAIN_INC',
    'CMD_B_MODE',
    'CMD_CFI_MODE',
]

if _HAS_STREAMING:
    __all__.append('ClariusStreamingClient')
