#!/usr/bin/env python3
"""
Code Style Fixes for Professional Patch Tool
Code quality and style improvements
"""

CODE_STYLE_PATCHES = {
    "add_type_hints": {
        "name": "Add Python Type Hints",
        "description": "Add basic type hints to function definitions for better code documentation and IDE support",
        "category": "code_quality",
        "severity": "low",
        "risk_level": "low",
        "files": ["**/*.py"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r'def\s+(\w+)\s*\((.*?)\)\s*:',
                "replacement": "def \\1(\\2) -> None:",
                "context_aware": True,
                "parameters": {
                    "return_type": {
                        "description": "Return type for the function",
                        "type": "string", 
                        "default": "None"
                    }
                },
                "validation": "type_hints_added"
            }
        ],
        "dependencies": [],
        "author": "Code Quality Team",
        "version": "1.0",
        "created": "2024-01-10",
        "test_cases": [
            {
                "input": "def process_data(data):",
                "expected": "def process_data(data) -> None:"
            }
        ]
    },
    
    "fix_import_order": {
        "name": "Fix Import Order",
        "description": "Reorder imports according to PEP8 standards (standard library, third-party, local imports)",
        "category": "code_quality",
        "severity": "low", 
        "risk_level": "low",
        "files": ["**/*.py"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r'^import\s+(\w+)',
                "replacement": "import \\1",
                "multi_file": True,
                "parameters": {
                    "group_imports": {
                        "description": "Group imports by type",
                        "type": "boolean",
                        "default": True
                    }
                }
            }
        ],
        "dependencies": [],
        "author": "Code Quality Team",
        "version": "1.0",
        "created": "2024-01-12"
    },
    
    "convert_print_to_logging": {
        "name": "Convert Print to Logging",
        "description": "Replace print statements with proper logging for better application monitoring",
        "category": "code_quality",
        "severity": "medium",
        "risk_level": "low",
        "files": ["**/*.py"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r'print\s*\((.*?)\)',
                "replacement": "logging.info(\\1)",
                "pre_requisite": ["import logging"],
                "parameters": {
                    "log_level": {
                        "description": "Logging level to use",
                        "type": "string",
                        "default": "info",
                        "options": ["debug", "info", "warning", "error"]
                    }
                },
                "validation": "no_print_statements"
            }
        ],
        "dependencies": [],
        "author": "Code Quality Team",
        "version": "1.0",
        "created": "2024-01-18",
        "test_cases": [
            {
                "input": "print(\"Processing data...\")",
                "expected": "logging.info(\"Processing data...\")"
            }
        ]
    },
    
    "add_docstrings": {
        "name": "Add Missing Docstrings",
        "description": "Add basic docstrings to functions and classes that are missing documentation",
        "category": "code_quality",
        "severity": "low",
        "risk_level": "low",
        "files": ["**/*.py"],
        "patches": [
            {
                "type": "insert_after",
                "after": r'def\s+(\w+)\s*\((.*?)\)\s*:',
                "replacement": "    \"\"\"\\1 function.\n    \n    Args:\n        \\2: Function arguments\n        \n    Returns:\n        None\n    \"\"\"",
                "parameters": {
                    "function_name": {
                        "description": "Name of the function to document",
                        "type": "string",
                        "required": True
                    }
                },
                "validation": "docstring_added"
            },
            {
                "type": "insert_after", 
                "after": r'class\s+(\w+)\s*:',
                "replacement": "    \"\"\"\\1 class.\n    \n    Attributes:\n        None\n    \"\"\"",
                "parameters": {
                    "class_name": {
                        "description": "Name of the class to document", 
                        "type": "string",
                        "required": True
                    }
                }
            }
        ],
        "dependencies": [],
        "author": "Code Quality Team",
        "version": "1.0",
        "created": "2024-01-22"
    },
    
    "remove_unused_imports": {
        "name": "Remove Unused Imports",
        "description": "Remove imported modules that are not used in the code",
        "category": "code_quality",
        "severity": "low",
        "risk_level": "low",
        "files": ["**/*.py"],
        "patches": [
            {
                "type": "replace_pattern", 
                "pattern": r'^import\s+(\w+)$',
                "replacement": "# import \\1  # UNUSED",
                "parameters": {
                    "detect_unused": {
                        "description": "Detect if import is actually used",
                        "type": "boolean", 
                        "default": True
                    }
                },
                "validation": "no_unused_imports"
            }
        ],
        "dependencies": [],
        "author": "Code Quality Team",
        "version": "1.0",
        "created": "2024-01-25"
    },
    
    "optimize_string_building": {
        "name": "Optimize String Building",
        "description": "Replace string concatenation in loops with join() for better performance",
        "category": "performance",
        "severity": "medium",
        "risk_level": "low",
        "files": ["**/*.py"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r'result\s*=\s*\"\"\s*\n\s*for\s+(\w+)\s+in\s+(\w+)\s*:\s*\n\s*result\s*\+=\s*(\w+)',
                "replacement": "result = ''.join(\\3 for \\1 in \\2)",
                "validation": "same_output",
                "parameters": {
                    "variable_names": {
                        "description": "Variable names used in the loop",
                        "type": "list",
                        "required": True
                    }
                }
            }
        ],
        "dependencies": [],
        "author": "Performance Team",
        "version": "1.0",
        "created": "2024-01-30",
        "test_cases": [
            {
                "input": "result = \"\"\nfor char in text:\n    result += char",
                "expected": "result = ''.join(char for char in text)"
            }
        ]
    },
    
    "convert_list_comprehensions": {
        "name": "Convert to List Comprehensions",
        "description": "Replace simple for loops with list comprehensions for better readability and performance",
        "category": "code_quality",
        "severity": "low",
        "risk_level": "low",
        "files": ["**/*.py"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r'result\s*=\s*\[\]\s*\n\s*for\s+(\w+)\s+in\s+(\w+)\s*:\s*\n\s*result\.append\(([^)]+)\)',
                "replacement": "result = [\\3 for \\1 in \\2]",
                "validation": "same_output",
                "parameters": {
                    "loop_variable": {
                        "description": "Variable used in the loop",
                        "type": "string",
                        "required": True
                    }
                }
            }
        ],
        "dependencies": [],
        "author": "Code Quality Team",
        "version": "1.0",
        "created": "2024-02-02"
    }
}
