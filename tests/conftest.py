import pytest
import sys
import os

# Add repo root and parent to sys.path so tests can import modules smoothly
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

parent_dir = os.path.dirname(repo_root)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

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
