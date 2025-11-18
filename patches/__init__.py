#!/usr/bin/env python3
"""
Patches module for Professional Patch Tool
User-defined patch library and automated fixes
"""

from .security_fixes import SECURITY_PATCHES
from .code_style import CODE_STYLE_PATCHES
from .migration_scripts import MIGRATION_PATCHES

# Combined patches dictionary
PATCHES = {}
PATCHES.update(SECURITY_PATCHES)
PATCHES.update(CODE_STYLE_PATCHES)
PATCHES.update(MIGRATION_PATCHES)

__all__ = [
    'SECURITY_PATCHES',
    'CODE_STYLE_PATCHES', 
    'MIGRATION_PATCHES',
    'PATCHES'
]
