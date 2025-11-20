## Professional Patch Tool

A powerful, interactive file patching tool with advanced modular architecture, batch operations, and comprehensive patch library.

## 🚀 New Features & Architecture

### Modular Architecture
The tool has been completely refactored into a modular architecture for better maintainability and extensibility:

```

patch-tool/
├──📁 core/                    # Core engine components
│├── config_manager.py       # Configuration with validation
│├── file_manager.py         # File operations & backup rotation
│├── navigation.py           # UNIX-style navigation
│└── patch_engine.py         # Core patching logic
├──📁 features/                # Advanced features
│├── predefined_fixes.py     # Patch library system
│├── batch_operations.py     # Multi-file processing
│├── diff_engine.py          # Diff generation & preview
│└── patch_history.py        # Undo/Redo system
├──📁 ui/                      # User interface
│├── interactive_menus.py    # All menu systems
│├── syntax_highlighter.py   # Enhanced syntax highlighting
│└── preview_renderer.py     # File preview & diff display
├──📁 utils/                   # Utility functions
│├── regex_utils.py          # Advanced pattern matching
│├── line_utils.py           # Line manipulation helpers
│└── validation.py           # Input validation
├──📁 patches/                 # User-defined patch library
│├── security_fixes.py       # Security vulnerability fixes
│├── code_style.py           # Code quality improvements
│└── migration_scripts.py    # Framework migration helpers
├──patch_tool.py              # Main entry point
└──README.md

```

### Advanced Features
- **🔀 Batch Operations**: Multi-file search/replace and analysis
- **🛠️ Predefined Fixes Library**: 15+ ready-to-use patches
- **🔍 Advanced Diff Engine**: Side-by-side diff previews
- **📋 Patch History**: Full undo/redo capability
- **🎯 Fuzzy Matching**: Find similar code with Levenshtein distance
- **📊 Multi-line Pattern Matching**: Match complex code blocks
- **💾 Patch File Generation**: Create standard .patch files

## 🏃 Quick Start

```bash
# Run the tool
python3 patch_tool.py

# Or make it executable and run directly
chmod +x patch_tool.py
./patch_tool.py

# Or simply run
patch-tool
```

📚 Comprehensive Usage Guide

Main Menu Options

1. 📝 Navigate & patch file (UNIX-style) - Interactive file browser with UNIX commands
2. 📝 Enter file path directly - Quick file access by path
3. 🛠️ Predefined fixes - Apply automated fixes from patch library
4. 🔀 Batch operations - Multi-file processing and analysis
5. 📂 File history - Select from recently edited files
6. 🔧 Advanced tools - Diff preview, patch history, backup management
7. ⚙️ Settings - Configure tool behavior
8. ❌ Exit - Quit the application

Advanced Tools Menu

· 🔍 Diff preview - See changes before applying
· 📋 Patch history - Undo/redo operations
· 💾 Backup management - Restore and manage backups
· 📊 File analysis - Code pattern analysis

🗂️ File Navigation (UNIX-style)

When you select "Navigate & patch file", you get a UNIX-style interface:

```
📁 Current: /your/project/path
============================================================
💡 TIPS:
  • Enter path: 'api/main.py' or 'src/'
  • Commands: 'ls', 'cd <dir>', 'pwd', '~' for home
  • Navigation: '../' to go up, '/' for root, '-' for previous
  • Type filename to select, 'q' to quit, 'h' for history
============================================================

📁 /your/project/path $ 
```

Navigation Commands:

· ls - List directory contents
· cd <dir> - Change directory
· pwd - Show current directory
· ~ - Go to home directory
· - - Go to previous directory
· ../ - Go up one level
· / - Go to root directory
· q - Quit navigation
· h - Show file history

🔧 Enhanced Patching Operations

Patch Menu Options

1. 📋 Show file preview - Navigate with next/previous/goto line
2. 🔍 Search for code pattern - Enhanced with fuzzy matching
3. 📍 Insert code at specific line - With indentation preservation
4. 🔄 Replace code block - By range, pattern, or all matches
5. ➕ Insert after pattern - Context-aware insertion
6. ➖ Insert before pattern - Context-aware insertion
7. 📤 Append to end of file - Auto-indentation
8. 🗑️ Delete code block - With safety confirmation
9. 📋 Show patch queue - Enhanced preview with details
10. 🔍 Preview changes - See diff before applying
11. 💾 Apply patches - With backup and history tracking
12. ⚙️ Settings - Patch-specific configuration

Advanced Code Input

· Multi-line patterns - Match complex code blocks
· Fuzzy matching - Find similar code (80%+ similarity)
· Indentation preservation - Auto-detect and maintain code style
· Context-aware insertion - Smart indentation based on surrounding code

🛠️ Predefined Fixes Library

Security Fixes

· SQL Injection Protection - Parameterized queries
· Remove Hardcoded Secrets - Environment variables
· Enable SSL Verification - Secure HTTP requests
· XSS Prevention - HTML escaping
· Input Validation - Function parameter validation

Code Quality

· Add Type Hints - Python type annotations
· Convert Print to Logging - Better application monitoring
· Add Missing Docstrings - Function/class documentation
· Remove Unused Imports - Code cleanup
· Optimize String Building - Performance improvements
· List Comprehensions - Convert loops to comprehensions

Migration Scripts

· Python 2 to 3 - Print function migration
· Django 1.x to 2.x - URL pattern updates
· React Class to Hooks - Functional components
· Async/Await - Modern JavaScript syntax
· Deprecated Methods - Update outdated APIs
· Config Format Migration - INI to YAML/JSON

🔀 Batch Operations

Multi-file Processing

· Batch Find & Replace - Across multiple files
· Pattern Search - Search across directory trees
· Batch Patch Application - Apply same patch to multiple files
· File Analysis - Code statistics and pattern detection

Example: Batch Security Fix

```bash
# Apply SQL injection protection to all Python files
1. Select "Batch operations"
2. Choose "Apply patch to multiple files"
3. Select "SQL Injection Protection" from predefined fixes
4. Specify file pattern: **/*.py
5. Preview and apply to all matching files
```

🔍 Diff & Preview System

Advanced Diff Views

· Unified Diff - Standard patch format
· Side-by-Side - Visual comparison
· Inline Changes - Within file context
· Change Statistics - Added/removed/modified lines

Patch File Generation

Generate standard .patch files for version control:

```bash
# Creates patch files that can be applied with `git apply` or `patch`
```

💾 Enhanced Safety Features

Backup System

· Automatic Backups - Before every patch operation
· Backup Rotation - Configurable retention (default: 30 days)
· Backup Restoration - One-click restore from any backup
· Safe File Operations - Validation and conflict detection

Validation System

· Patch Validation - Pre-application checks
· Conflict Detection - Identify overlapping changes
· File Safety Checks - Read/write permissions
· Input Sanitization - Safe filename and path handling

🎯 Advanced Pattern Matching

Fuzzy Matching

Find similar code with configurable similarity thresholds:

```python
# Finds "hello world", "hello there", "hell world" when searching for "hello world"
Similarity threshold: 0.8 (80% match)
```

Multi-line Patterns

Match complex code structures:

```python
# Match entire function blocks
pattern = r"def\s+\w+\(.*?\):\n.*?return.*?\n"
```

Regex Utilities

· Pattern Validation - Syntax checking
· Pattern Testing - Test against sample strings
· Regex Building - Complex pattern construction
· Caching - Performance optimization

📁 Adding Custom Features Safely

Creating Custom Patches

1. Create a new patch file in patches/ directory:

```python
# patches/custom_fixes.py
CUSTOM_PATCHES = {
    "my_custom_fix": {
        "name": "My Custom Fix",
        "description": "Description of what this fix does",
        "category": "custom",
        "severity": "medium",
        "files": ["**/*.py"],
        "patches": [
            {
                "type": "replace_pattern",
                "pattern": r"old_pattern",
                "replacement": "new_code",
                "validation": "custom_validation"
            }
        ],
        "author": "Your Name",
        "version": "1.0"
    }
}
```

1. Update patches/__init__.py to include your new patches:

```python
from .custom_fixes import CUSTOM_PATCHES
PATCHES.update(CUSTOM_PATCHES)
```

Adding New Utility Functions

1. Create new utility module in utils/:

```python
# utils/custom_utils.py
class CustomUtils:
    def new_feature(self, data):
        # Implementation
        pass

__all__ = ['CustomUtils']
```

1. Update utils/__init__.py:

```python
from .custom_utils import CustomUtils
```

1. Integrate into main tool in patch_tool.py:

```python
from utils import CustomUtils

class ProfessionalPatchTool:
    def __init__(self):
        # ...
        self.custom_utils = CustomUtils()
```

Safe Development Practices

1. Use Validation: Always validate inputs using utils.validation
2. Create Backups: Use file_manager.create_backup() before changes
3. Test Patches: Use the built-in patch validation system
4. Handle Errors: Use try-catch with proper error messages
5. Follow Patterns: Use existing modules as templates

🎨 Enhanced Syntax Highlighting

Supported Languages

· Python (.py) - Full keyword and string highlighting
· Zexus (.zx) - Custom language support
· JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
· Java (.java)
· C/C++ (.c, .cpp, .h, .hpp)
· HTML (.html, .htm)
· CSS (.css, .scss, .less)
· Markdown (.md, .markdown)
· JSON (.json)
· XML (.xml)
· YAML (.yaml, .yml)
· SQL (.sql)
· Bash (.sh, .bash)
· PHP (.php)
· Ruby (.rb)
· Go (.go)
· Rust (.rs)

Advanced Highlighting Features

· Pygments Integration - Professional syntax coloring (if available)
· Theme Support - Configurable color schemes
· Language Detection - Automatic from file extension and content

🔧 Configuration

Settings Menu

· Auto Backup: Enable/disable automatic backups
· Confirm Applications: Safety confirmation prompts
· Syntax Hints: Enable syntax highlighting
· Max Preview Lines: Lines to show in file preview (10-200)
· Show Hidden Files: Include hidden files in navigation
· Backup Keep Days: Backup retention period (1-365 days)
· Advanced Highlighting: Use Pygments if available

Configuration File

~/.patch_config.json - Automatically created and managed

```json
{
  "auto_backup": true,
  "confirm_applications": true,
  "enable_syntax_hints": true,
  "max_preview_lines": 50,
  "show_hidden_files": false,
  "backup_keep_days": 30,
  "use_advanced_highlighting": false
}
```

📊 Examples & Use Cases

Example 1: Security Audit & Fix

```bash
# 1. Run security analysis
Batch Operations → File Analysis → Search for security patterns

# 2. Apply security fixes
Predefined Fixes → Security → Apply multiple fixes

# 3. Verify changes
Diff Preview → Review all modifications
```

Example 2: Code Quality Improvement

```bash
# 1. Add type hints to all functions
Predefined Fixes → Code Quality → Add Type Hints

# 2. Convert print to logging
Predefined Fixes → Code Quality → Convert Print to Logging

# 3. Add missing documentation
Predefined Fixes → Code Quality → Add Missing Docstrings
```

Example 3: Framework Migration

```bash
# 1. Update Django URLs
Predefined Fixes → Migration → Django 1.x to 2.x URLs

# 2. Update package imports
Predefined Fixes → Migration → Package Import Updates

# 3. Generate migration report
Batch Operations → File Analysis → Migration patterns
```

🐛 Troubleshooting

Common Issues

File not found

· Check current directory with pwd command
· Verify file exists with ls command
· Use absolute paths if needed

Permission denied

· Check file/directory permissions
· Run tool with appropriate privileges
· Verify backup directory is writable

Invalid regex pattern

· Use pattern validation in regex utilities
· Test patterns with built-in testing feature
· Check regex syntax documentation

Backup failed

· Verify disk space availability
· Check write permissions in backup directory
· Review backup rotation settings

Debug Mode

Enable verbose logging for troubleshooting:

```python
# Add to patch_tool.py for debugging
import logging
logging.basicConfig(level=logging.DEBUG)
```

🤝 Contributing

Adding New Features

1. Follow the modular architecture patterns
2. Use existing utilities for validation and safety
3. Add comprehensive documentation
4. Include integration tests

Creating Patch Libraries

1. Use the template in patches/template.py
2. Include test cases and validation
3. Add proper metadata (author, version, dependencies)
4. Categorize appropriately (security, performance, migration, etc.)

Reporting Issues

Include:

· Tool version and configuration
· Steps to reproduce
· Expected vs actual behavior
· Relevant file examples

📄 License & Attribution

This tool is designed for professional development use. Always:

· Test patches in a safe environment first
· Maintain proper version control
· Follow your organization's security policies
· Keep backups of important files

---

Professional Patch Tool - Your comprehensive solution for safe, efficient code modification and migration.
