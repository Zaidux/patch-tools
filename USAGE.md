# Professional Patch Tool - Usage Guide

## 🚀 Overview

The Professional Patch Tool is an interactive file patching system with UNIX-style navigation, predefined fixes, batch operations, and advanced code manipulation capabilities.

## 📋 Quick Start

### Basic Usage
```bash
# Run the tool
patch-tool

# Or directly with Python
python3 patch_tool.py
```

Navigation Patterns

· File paths: src/main.py, api/routes/
· Commands: ls, cd <dir>, pwd, ~ (home), .. (parent)
· Navigation: ../ (up), / (root), - (previous directory)
· Selection: Type filename to select, q to quit, h for history

🎯 Core Features

1. Interactive File Patching

Main Menu → Option 1 (Navigate & patch file)

Navigate through directories and select files to patch:

```
📁 Current: /home/user/project/
📄 FILES:
  main.py (2.1 KB)
  utils.py (1.5 KB)
  config.json (0.8 KB)
```

2. Direct File Access

Main Menu → Option 2 (Enter file path directly)
Quickly access files without navigation:

```
Enter file path: src/utils/helpers.py
```

3. Predefined Fixes

Main Menu → Option 3 (Predefined fixes)
Apply automated fixes for common issues:

Categories:

· 🔒 Security: SQL injection protection, hardcoded secrets removal
· 🎨 Code Quality: Type hints, import order fixes
· ⚡ Performance: String building optimization

Example: Fix SQL Injection

```python
# Before: cursor.execute("SELECT * FROM users WHERE id = %s" % user_id)
# After: cursor.execute("SELECT * FROM users WHERE id = %s", user_id)
```

4. Batch Operations

Main Menu → Option 4 (Batch operations)
Apply patches to multiple files simultaneously:

· Process entire directories
· Apply patterns across multiple files
· Preview changes before applying

5. File History

Main Menu → Option 5 (File history)
Access recently patched files for quick editing.

🔧 Patch Operations

Available Patch Types

1. Insert at Line

```bash
Insert 2 lines at line 25:
# New feature added
print("Feature implemented")
```

2. Replace Code Block

By Line Range:

```bash
Replace lines 10-15 with:
def new_function():
    return "Updated implementation"
```

By Pattern:

```bash
Pattern: old_function\(.*\)
Replacement: new_function()
```

3. Insert Relative to Pattern

After Pattern:

```bash
Pattern: import os
Insert after:
import sys
import json
```

Before Pattern:

```bash
Pattern: def main():
Insert before:
# Main entry point
```

4. Append to End

```bash
Add to file end:
if __name__ == "__main__":
    main()
```

5. Delete Code Block

```bash
Delete lines 30-35:
# Removes deprecated code
```

Patch Queue Management

· View queue: Option 9 (Show patch queue)
· Preview changes: Option 10 (Preview changes)
· Apply patches: Option 11 (Apply patches)

🛠️ Advanced Features

Diff Preview

Main Menu → Option 6 → Option 1
See exactly what will change before applying patches:

```diff
- print("Old message")
+ print("New improved message")
```

Patch History

Main Menu → Option 6 → Option 2

· View applied patches
· Undo operations
· Track changes over time

Backup Management

Main Menu → Option 6 → Option 3

· Restore from backups
· Cleanup old backups
· View backup statistics

⚙️ Configuration

Settings Menu

Main Menu → Option 7 (Settings)

Available Settings:

· ✅ Auto backup: Automatically create backups before patching
· ✅ Confirm applications: Ask for confirmation before applying patches
· ✅ Syntax hints: Enable syntax highlighting in previews
· 📏 Max preview lines: Control how many lines to show in previews
· 👻 Show hidden files: Include hidden files in navigation
· 📅 Backup keep days: How long to keep backup files

Default Configuration

```json
{
  "auto_backup": true,
  "confirm_applications": true,
  "enable_syntax_hints": true,
  "max_preview_lines": 20,
  "show_hidden_files": false,
  "backup_keep_days": 30
}
```

🔍 Search & Navigation Tips

Pattern Matching

Use regex patterns for powerful searches:

```bash
# Find function definitions
def\s+\w+\(.*\):

# Find class definitions
class\s+\w+:

# Find TODO comments
# TODO:.*
```

Fuzzy Search

Enable fuzzy matching for approximate pattern matching:

```
Use fuzzy matching? [y/N]: y
```

Context Lines

View surrounding code for better understanding:

```
Show context? [y/N]: y
```

💾 Backup System

Automatic Backups

· Created before every patch application
· Stored in backups/ directory
· Named with timestamp: filename_20251201_143022.bak

Manual Backup Management

```bash
# Restore from backup
patch-tool
→ Option 6 (Advanced tools)
→ Option 3 (Backup management)
→ Option 1 (Restore from backup)

# Cleanup old backups
→ Option 3 (Backup management)
→ Option 2 (Cleanup old backups)
```

🎨 Custom Patches

Creating Custom Patches

Predefined Fixes → Custom Patches → Create New

1. Define patch metadata:
   · Name: "Fix Import Statements"
   · Description: "Add missing import statements"
   · Category: "code_quality"
2. Add patch operations:
   ```yaml
   - type: insert_at_line
     line_number: 1
     code: |
       import os
       import sys
   ```
3. Save for reuse:
   · Save as custom patch file
   · Available in predefined fixes menu

Patch Validation

All patches are validated before application:

· ✅ Line number bounds checking
· ✅ Regex pattern validation
· ✅ File compatibility checks

🔄 Workflow Examples

Example 1: Add Missing Import

```bash
1. Navigate to file: src/main.py
2. Option 3 (Insert at line)
3. Line: 1
4. Code:
   import json
   import requests
5. Option 11 (Apply patches)
```

Example 2: Fix Function Signature

```bash
1. Navigate to file: utils/helpers.py
2. Option 4 (Replace code block)
3. Option 2 (Replace by pattern)
4. Pattern: def process_data\(data\):
5. Replacement:
   def process_data(data: Dict) -> List:
6. Option 11 (Apply patches)
```

Example 3: Batch Security Fix

```bash
1. Option 3 (Predefined fixes)
2. Select "Security" category
3. Choose "Remove Hardcoded Secrets"
4. Review affected files
5. Confirm application
```

🚨 Troubleshooting

Common Issues

Patch not applied:

· Ensure you select Option 11 (Apply patches) after queuing
· Check patch queue with Option 9

File not found:

· Use absolute paths: /home/user/project/file.py
· Or relative paths from current directory

Permission errors:

· Ensure write permissions on target files
· Run with appropriate user privileges

Backup failures:

· Check disk space
· Verify backup directory permissions

Debug Mode

Enable verbose output for troubleshooting:

```bash
python3 -c "
from patch_tool import ProfessionalPatchTool
tool = ProfessionalPatchTool()
# Debug specific operations
"
```

📚 Best Practices

1. Always Preview Changes

Use Option 10 before applying patches to avoid unintended changes.

2. Use Predefined Fixes

Leverage built-in patches for common patterns before creating custom ones.

3. Regular Backups

Keep backup retention appropriate for your workflow (default: 30 days).

4. Test in Safe Environment

Test patches on non-critical files first.

5. Use Version Control

The patch tool complements but doesn't replace proper version control systems.

🎊 Success Stories

Real-world Use Cases

· Code Migration: Update function signatures across large codebases
· Security Hardening: Apply security fixes to multiple projects
· Code Standardization: Enforce coding standards automatically
· Dependency Updates: Update import statements and API calls

---

Need Help?

· Run integration test: python3 test_integration.py
· Check file structure: tree patch-tool/
· Review logs in backup directory

Happy Patching! 🚀
