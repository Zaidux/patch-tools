#!/usr/bin/env python3
"""
Migration Scripts for Professional Patch Tool
Code migration and upgrade scripts
"""

MIGRATION_PATCHES = {
    "python_2_to_3_print": {
        "name": "Python 2 to 3 Print Migration",
        "description": "Convert Python 2 print statements to Python 3 print functions",
        "category": "migration",
        "severity": "high",
        "risk_level": "medium",
        "files": ["**/*.py"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r'print\s+([^(\s].*)$',
                "replacement": "print(\\1)",
                "parameters": {
                    "add_parentheses": {
                        "description": "Add parentheses around print arguments",
                        "type": "boolean",
                        "default": True
                    }
                },
                "validation": "python3_print"
            }
        ],
        "dependencies": [],
        "author": "Migration Team",
        "version": "1.0",
        "created": "2024-01-08",
        "test_cases": [
            {
                "input": "print \"Hello, World!\"",
                "expected": "print(\"Hello, World!\")"
            }
        ]
    },
    
    "django_1_to_2_urls": {
        "name": "Django 1.x to 2.x URL Migration",
        "description": "Update Django URL patterns from 1.x syntax to 2.x path() and re_path()",
        "category": "migration",
        "severity": "high",
        "risk_level": "high",
        "files": ["**/urls.py"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r'url\(\s*r\'(.*?)\',\s*(.*?),\s*name=\'(.*?)\'\)',
                "replacement": "path('\\1', \\2, name='\\3')",
                "pre_requisite": ["from django.urls import path, re_path"],
                "parameters": {
                    "pattern_type": {
                        "description": "Type of URL pattern (path or re_path)",
                        "type": "string",
                        "default": "path",
                        "options": ["path", "re_path"]
                    }
                },
                "validation": "django2_urls"
            }
        ],
        "dependencies": [],
        "author": "Migration Team",
        "version": "1.0",
        "created": "2024-01-12"
    },
    
    "react_class_to_hooks": {
        "name": "React Class to Hooks Migration",
        "description": "Convert React class components to functional components with hooks",
        "category": "migration",
        "severity": "medium",
        "risk_level": "medium",
        "files": ["**/*.js", "**/*.jsx", "**/*.tsx"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r'class\s+(\w+)\s+extends\s+React\.Component\s*{',
                "replacement": "const \\1 = () => {",
                "pre_requisite": ["import React, { useState, useEffect } from 'react';"],
                "parameters": {
                    "component_name": {
                        "description": "Name of the React component",
                        "type": "string",
                        "required": True
                    }
                },
                "validation": "react_hooks"
            }
        ],
        "dependencies": [],
        "author": "Migration Team",
        "version": "1.0",
        "created": "2024-01-18"
    },
    
    "add_async_await": {
        "name": "Add Async/Await",
        "description": "Convert promise-based code to async/await syntax for better readability",
        "category": "migration",
        "severity": "medium",
        "risk_level": "low",
        "files": ["**/*.js", "**/*.ts"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r'function\s+(\w+)\s*\(\s*\)\s*{\s*\n\s*return\s+(\w+)\.then\(',
                "replacement": "async function \\1() {\n    return await \\2.",
                "parameters": {
                    "function_name": {
                        "description": "Name of the async function",
                        "type": "string",
                        "required": True
                    }
                },
                "validation": "async_await"
            }
        ],
        "dependencies": [],
        "author": "Migration Team",
        "version": "1.0",
        "created": "2024-01-22"
    },
    
    "update_deprecated_methods": {
        "name": "Update Deprecated Methods",
        "description": "Replace deprecated methods and functions with their modern equivalents",
        "category": "migration",
        "severity": "medium",
        "risk_level": "medium",
        "files": ["**/*.py", "**/*.js", "**/*.java"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r'\.appendChild\(',
                "replacement": ".append(",
                "parameters": {
                    "method_name": {
                        "description": "Name of the deprecated method",
                        "type": "string",
                        "required": True
                    }
                },
                "validation": "no_deprecated_methods"
            }
        ],
        "dependencies": [],
        "author": "Migration Team",
        "version": "1.0",
        "created": "2024-01-28"
    },
    
    "config_format_migration": {
        "name": "Config Format Migration",
        "description": "Migrate configuration files from older formats to newer standards (INI to YAML, etc.)",
        "category": "migration",
        "severity": "medium",
        "risk_level": "medium",
        "files": ["**/*.ini", "**/*.cfg"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r'\[(\w+)\]',
                "replacement": "\\1:",
                "parameters": {
                    "target_format": {
                        "description": "Target configuration format",
                        "type": "string",
                        "default": "yaml",
                        "options": ["yaml", "json", "toml"]
                    }
                },
                "validation": "config_format"
            }
        ],
        "dependencies": [],
        "author": "Migration Team",
        "version": "1.0",
        "created": "2024-02-05"
    },
    
    "package_import_updates": {
        "name": "Package Import Updates",
        "description": "Update import statements for packages that have been renamed or reorganized",
        "category": "migration",
        "severity": "medium",
        "risk_level": "low",
        "files": ["**/*.py"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r'from\s+urllib2\s+import',
                "replacement": "from urllib.request import",
                "parameters": {
                    "old_package": {
                        "description": "Old package name",
                        "type": "string",
                        "required": True
                    },
                    "new_package": {
                        "description": "New package name",
                        "type": "string",
                        "required": True
                    }
                },
                "validation": "updated_imports"
            }
        ],
        "dependencies": [],
        "author": "Migration Team",
        "version": "1.0",
        "created": "2024-02-08"
    }
}
