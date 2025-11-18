#!/usr/bin/env python3
"""
Template for creating custom patches
Copy this file and modify to create your own patch definitions
"""

# Example custom patch template
CUSTOM_PATCHES = {
    "your_patch_id": {
        "name": "Your Patch Name",
        "description": "Description of what this patch does",
        "category": "custom",  # or "security", "performance", "migration", etc.
        "severity": "low",     # low, medium, high, critical
        "risk_level": "low",   # low, medium, high
        "files": ["**/*.py"],  # File patterns to apply to
        "patches": [
            {
                "type": "replace_pattern",  # or insert_at_line, replace_range, etc.
                "pattern": r"your_regex_pattern",
                "replacement": "your_replacement",
                # Optional parameters:
                "pre_requisite": ["import statements", "other requirements"],
                "validation": "your_validation_function",
                "parameters": {
                    "param1": {
                        "description": "Description of parameter",
                        "type": "string",  # or integer, boolean, list
                        "default": "default_value",
                        "required": False
                    }
                }
            }
        ],
        "dependencies": [],  # Other patches this depends on
        "author": "Your Name",
        "version": "1.0",
        "created": "2024-01-01",
        "test_cases": [
            {
                "input": "example input code",
                "expected": "expected output after patch"
            }
        ]
    }
}

"""
Patch Types Available:
- insert_at_line: Insert code at specific line number
- replace_range: Replace lines between start and end
- replace_pattern: Replace regex pattern match
- replace_pattern_all: Replace all regex pattern matches  
- insert_after: Insert after regex pattern
- insert_before: Insert before regex pattern
- append: Add to end of file
- delete_range: Delete lines between start and end

Validation Options:
- sql_safe: Check for SQL injection safety
- no_hardcoded_values: Ensure no secrets in code
- type_hints_added: Verify type hints were added
- same_output: Ensure functionality unchanged
- python3_print: Verify Python 3 print syntax
- etc.
"""
