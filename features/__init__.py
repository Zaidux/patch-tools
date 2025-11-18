#!/usr/bin/env python3
"""
Features module for Professional Patch Tool
Advanced features and extended functionality
"""

from .predefined_fixes import PatchLibrary, PredefinedFixes
from .batch_operations import BatchOperations
from .diff_engine import DiffEngine
from .patch_history import PatchHistory

__all__ = [
    'PatchLibrary',
    'PredefinedFixes', 
    'BatchOperations',
    'DiffEngine',
    'PatchHistory'
]
