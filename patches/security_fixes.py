#!/usr/bin/env python3
"""
Security Fixes for Professional Patch Tool
Security-related patches and vulnerability fixes
"""

SECURITY_PATCHES = {
    "fix_sql_injection": {
        "name": "SQL Injection Protection",
        "description": "Replace string formatting with parameterized queries in SQL statements to prevent SQL injection attacks",
        "category": "security",
        "severity": "high",
        "risk_level": "critical",
        "files": ["**/*.py", "**/*.java", "**/*.php"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r"cursor\.execute\(\s*[\"'](.*?\%s.*?)[\"']\s*%\s*(.*?)\s*\)",
                "replacement": "cursor.execute(\"\\1\", \\2)",
                "validation": "sql_safe",
                "parameters": {
                    "pattern": {
                        "description": "SQL query pattern with %s formatting",
                        "type": "regex"
                    },
                    "replacement": {
                        "description": "Parameterized query template", 
                        "type": "string"
                    }
                }
            },
            {
                "type": "replace_pattern", 
                "pattern": r"cursor\.execute\(\s*f[\"'](.*?)\[\"']\s*\)",
                "replacement": "cursor.execute(\"\\1\")",
                "validation": "sql_safe"
            }
        ],
        "dependencies": [],
        "prerequisites": ["import sqlite3", "import mysql.connector"],
        "author": "Security Team",
        "version": "1.0",
        "created": "2024-01-15",
        "test_cases": [
            {
                "input": "cursor.execute(\"SELECT * FROM users WHERE id = %s\" % user_id)",
                "expected": "cursor.execute(\"SELECT * FROM users WHERE id = ?\", user_id)"
            }
        ]
    },
    
    "fix_hardcoded_secrets": {
        "name": "Remove Hardcoded Secrets", 
        "description": "Replace hardcoded passwords, API keys, and secrets with environment variables",
        "category": "security",
        "severity": "critical",
        "risk_level": "high",
        "files": ["**/*.py", "**/*.js", "**/*.java", "**/*.php"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r'(password|api[_-]?key|secret|token)\s*=\s*[\"\'][^\"\']+[\"\']',
                "replacement": "\\1 = os.getenv('\\1'.upper(), '')",
                "pre_requisite": ["import os"],
                "parameters": {
                    "secret_types": {
                        "description": "Types of secrets to detect (password, api_key, etc.)",
                        "type": "list",
                        "default": ["password", "api_key", "secret", "token"]
                    }
                }
            },
            {
                "type": "replace_pattern",
                "pattern": r'config\[[\"\'][^\"\']+[\"\']\]\s*=\s*[\"\'][^\"\']+[\"\']',
                "replacement": "# SECURITY: Remove hardcoded values\n# config['key'] = 'value'  # Replace with environment variable",
                "validation": "no_hardcoded_values"
            }
        ],
        "dependencies": [],
        "author": "Security Team",
        "version": "1.1", 
        "created": "2024-01-20",
        "test_cases": [
            {
                "input": "api_key = \"sk_1234567890abcdef\"",
                "expected": "api_key = os.getenv('API_KEY', '')"
            }
        ]
    },
    
    "fix_ssl_verification": {
        "name": "Enable SSL Certificate Verification",
        "description": "Replace insecure SSL verification disablement with proper certificate verification",
        "category": "security", 
        "severity": "high",
        "risk_level": "medium",
        "files": ["**/*.py"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r'verify\s*=\s*False',
                "replacement": "verify=True",
                "parameters": {
                    "context": {
                        "description": "Only apply in requests context",
                        "type": "context",
                        "required": True
                    }
                }
            },
            {
                "type": "replace_pattern",
                "pattern": r'urllib3\.disable_warnings\(\)',
                "replacement": "# SECURITY: Enable SSL warnings\n# urllib3.disable_warnings()  # Remove this line to enable SSL verification",
                "validation": "ssl_warnings_enabled"
            }
        ],
        "dependencies": [],
        "author": "Security Team",
        "version": "1.0",
        "created": "2024-01-25"
    },
    
    "fix_xss_vulnerability": {
        "name": "Prevent XSS Vulnerabilities",
        "description": "Add HTML escaping to prevent cross-site scripting attacks in web applications",
        "category": "security",
        "severity": "high", 
        "risk_level": "high",
        "files": ["**/*.py", "**/*.js", "**/*.html"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r'response\.write\(([^)]+)\)',
                "replacement": "response.write(html.escape(\\1))",
                "pre_requisite": ["import html"],
                "parameters": {
                    "context": {
                        "description": "Apply to response.write calls",
                        "type": "context", 
                        "required": True
                    }
                }
            },
            {
                "type": "replace_pattern",
                "pattern": r'document\.innerHTML\s*=\s*([^;]+);',
                "replacement": "document.textContent = \\1; // SECURITY: Use textContent instead of innerHTML",
                "validation": "no_inner_html"
            }
        ],
        "dependencies": [],
        "author": "Security Team",
        "version": "1.0",
        "created": "2024-02-01"
    },
    
    "add_input_validation": {
        "name": "Add Input Validation",
        "description": "Add basic input validation to function parameters to prevent injection attacks",
        "category": "security",
        "severity": "medium",
        "risk_level": "medium", 
        "files": ["**/*.py"],
        "patches": [
            {
                "type": "insert_before",
                "before": r'def\s+(\w+)\s*\((.*?)\)\s*:',
                "replacement": "def \\1(\\2):\n    # Input validation\n    if not all(isinstance(arg, str) for arg in [\\2]):\n        raise ValueError(\"Invalid input types\")\n    ",
                "parameters": {
                    "function_name": {
                        "description": "Name of the function to protect",
                        "type": "string",
                        "required": True
                    }
                }
            }
        ],
        "dependencies": [],
        "author": "Security Team", 
        "version": "1.0",
        "created": "2024-02-05"
    }
}
