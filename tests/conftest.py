import pytest
import sys

# Patch numpy 2.0 backwards compatibility for older classy_blocks/nptyping versions 
# so unit tests run seamlessly on local python 3.12+ (numpy 2.x) without needing Blender 4.0's bundled numpy 1.x
try:
    import numpy as np
    if not hasattr(np, 'bool8'): np.bool8 = np.bool_
    if not hasattr(np, 'float_'): np.float_ = np.float64
    if not hasattr(np, 'int_'): np.int_ = np.int64
    if not hasattr(np, 'complex_'): np.complex_ = np.complex128
    if not hasattr(np, 'object_'): np.object_ = object
    if not hasattr(np, 'object0'): np.object0 = object
    if not hasattr(np, 'int0'): np.int0 = np.intp
    if not hasattr(np, 'uint0'): np.uint0 = np.uintp
    if not hasattr(np, 'void0'): np.void0 = np.void
    if not hasattr(np, 'str0'): np.str0 = str
    if not hasattr(np, 'bytes0'): np.bytes0 = bytes
    if not hasattr(np, 'str_'): np.str_ = str
except Exception:
    pass

# Mock bpy so pure-logic imports that accidentally touch bpy don't crash unit tests
from unittest.mock import MagicMock
sys.modules['bpy'] = MagicMock()
sys.modules['mathutils'] = MagicMock()
