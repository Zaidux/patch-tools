#!/usr/bin/env python3
"""
Integration test for the complete Professional Patch Tool
"""

import os
import tempfile
from patch_tool import ProfessionalPatchTool
from utils import RegexUtils, Validation, PatchValidator
from patches import PATCHES

def test_integration():
    """Test that all modules work together"""
    print("🧪 Running integration tests...")
    
    # Test utility modules
    regex_utils = RegexUtils()
    validation = Validation()
    patch_validator = PatchValidator(regex_utils)
    
    # Test patches loading
    assert len(PATCHES) > 0, "No patches loaded"
    print(f"✅ Loaded {len(PATCHES)} predefined patches")
    
    # Test patch validation
    test_patch = {
        'type': 'insert_at_line',
        'line_number': 1,
        'code': ['import os'],
        'description': 'Test patch'
    }
    
    is_valid, message = patch_validator.validate_patch(test_patch)
    assert is_valid, f"Patch validation failed: {message}"
    print("✅ Patch validation working")
    
    # Test tool initialization
    with tempfile.TemporaryDirectory() as temp_dir:
        tool = ProfessionalPatchTool()
        tool.base_path = temp_dir
        
        # Test that all modules are initialized
        assert hasattr(tool, 'regex_utils'), "RegexUtils not initialized"
        assert hasattr(tool, 'patch_validator'), "PatchValidator not initialized"
        assert hasattr(tool, 'patches_library'), "Patches library not loaded"
        
        print("✅ All modules integrated successfully")
        print("🎉 Integration tests passed!")

if __name__ == "__main__":
    test_integration()
