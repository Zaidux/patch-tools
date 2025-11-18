#!/usr/bin/env python3
"""
Predefined Fixes System for Professional Patch Tool
Advanced patch library and automated fixes
"""

import os
import json
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import importlib.util
import inspect


class PatchLibrary:
    """Manages a library of predefined patches with dynamic loading"""
    
    def __init__(self, patches_dir: str = "patches/"):
        self.patches_dir = patches_dir
        self.regex_utils = regex_utils or RegexUtils()
        self.line_utils = line_utils or LineUtils()
        self.patches = {}
        self.categories = {}
        self._load_patch_library()

    def _load_patch_library(self):
        """Load all patch definitions from patches directory"""
        # Create patches directory if it doesn't exist
        os.makedirs(self.patches_dir, exist_ok=True)
        
        # Load from built-in patches first
        self._load_builtin_patches()
        
        # Load from external patch files
        self._load_external_patches()

    def _load_builtin_patches(self):
        """Load built-in patch definitions"""
        builtin_patches = {
            "security": {
                "fix_sql_injection": {
                    "name": "SQL Injection Protection",
                    "description": "Replace string formatting with parameterized queries in SQL statements",
                    "category": "security",
                    "severity": "high",
                    "files": ["**/*.py"],
                    "patches": [
                        {
                            "type": "replace_pattern",
                            "pattern": r"cursor\.execute\(\s*[\"'](.*?)[\"']\s*%\s*(.*?)\s*\)",
                            "replacement": "cursor.execute(\"\\1\", \\2)",
                            "validation": "sql_safe"
                        }
                    ],
                    "dependencies": [],
                    "author": "Security Team",
                    "version": "1.0"
                },
                "fix_hardcoded_secrets": {
                    "name": "Remove Hardcoded Secrets",
                    "description": "Replace hardcoded passwords and API keys with environment variables",
                    "category": "security",
                    "severity": "critical",
                    "files": ["**/*.py", "**/*.js", "**/*.java"],
                    "patches": [
                        {
                            "type": "replace_pattern",
                            "pattern": r'(password|api[_-]?key|secret)\s*=\s*[\"\'][^\"\']+[\"\']',
                            "replacement": "\\1 = os.getenv('\\1'.upper(), '')",
                            "pre_requisite": ["import os"]
                        }
                    ],
                    "dependencies": [],
                    "author": "Security Team", 
                    "version": "1.0"
                }
            },
            "code_quality": {
                "add_type_hints": {
                    "name": "Add Python Type Hints",
                    "description": "Add basic type hints to function definitions",
                    "category": "code_quality", 
                    "severity": "low",
                    "files": ["**/*.py"],
                    "patches": [
                        {
                            "type": "replace_pattern",
                            "pattern": r'def\s+(\w+)\s*\((.*?)\)\s*:',
                            "replacement": "def \\1(\\2) -> None:",
                            "context_aware": True
                        }
                    ],
                    "dependencies": [],
                    "author": "Code Quality Team",
                    "version": "1.0"
                },
                "fix_import_order": {
                    "name": "Fix Import Order",
                    "description": "Reorder imports according to PEP8 standards",
                    "category": "code_quality",
                    "severity": "low", 
                    "files": ["**/*.py"],
                    "patches": [
                        {
                            "type": "replace_pattern",
                            "pattern": r'(import\s+[\w\s,]+)',
                            "replacement": "\\1",  # This would be more complex in reality
                            "multi_file": True
                        }
                    ],
                    "dependencies": [],
                    "author": "Code Quality Team",
                    "version": "1.0"
                }
            },
            "performance": {
                "optimize_string_building": {
                    "name": "Optimize String Building",
                    "description": "Replace string concatenation in loops with join()",
                    "category": "performance",
                    "severity": "medium",
                    "files": ["**/*.py"],
                    "patches": [
                        {
                            "type": "replace_pattern", 
                            "pattern": r'result\s*=\s*\"\"\s*\n\s*for\s+(\w+)\s+in\s+(\w+)\s*:\s*\n\s*result\s*\+=\s*(\w+)',
                            "replacement": "result = ''.join(\\3 for \\1 in \\2)",
                            "validation": "same_output"
                        }
                    ],
                    "dependencies": [],
                    "author": "Performance Team",
                    "version": "1.0"
                }
            }
        }
        
        for category, patches in builtin_patches.items():
            self.categories[category] = category.replace('_', ' ').title()
            for patch_id, patch_def in patches.items():
                self.patches[patch_id] = patch_def

    def _load_external_patches(self):
        """Load patch definitions from external Python files"""
        patch_files = glob.glob(os.path.join(self.patches_dir, "*.py"))
        
        for patch_file in patch_files:
            try:
                spec = importlib.util.spec_from_file_location(
                    f"patch_{Path(patch_file).stem}", patch_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Look for PATCHES variable or class
                if hasattr(module, 'PATCHES'):
                    for patch_id, patch_def in module.PATCHES.items():
                        self.patches[patch_id] = patch_def
                
                # Also look for patch classes
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        hasattr(obj, 'patch_id') and 
                        hasattr(obj, 'apply')):
                        self.patches[obj.patch_id] = obj
                        
            except Exception as e:
                print(f"⚠️  Error loading patch file {patch_file}: {e}")

    def get_categories(self) -> Dict[str, str]:
        """Get available patch categories"""
        return self.categories.copy()

    def get_patches_by_category(self, category: str) -> Dict[str, Dict]:
        """Get all patches in a category"""
        return {pid: patch for pid, patch in self.patches.items() 
                if patch.get('category') == category}

    def get_patch(self, patch_id: str) -> Optional[Dict]:
        """Get a specific patch definition"""
        return self.patches.get(patch_id)

    def search_patches(self, query: str) -> Dict[str, Dict]:
        """Search patches by name, description, or category"""
        query = query.lower()
        results = {}
        
        for patch_id, patch_def in self.patches.items():
            if (query in patch_def.get('name', '').lower() or
                query in patch_def.get('description', '').lower() or
                query in patch_def.get('category', '').lower()):
                results[patch_id] = patch_def
                
        return results

    def create_custom_patch(self, name: str, description: str, patches: List[Dict], 
                          category: str = "custom", **kwargs):
        """Create a new custom patch definition"""
        patch_id = name.lower().replace(' ', '_')
        
        self.patches[patch_id] = {
            "name": name,
            "description": description,
            "category": category,
            "patches": patches,
            "author": kwargs.get('author', 'User'),
            "version": kwargs.get('version', '1.0'),
            "severity": kwargs.get('severity', 'medium'),
            "files": kwargs.get('files', ['**/*']),
            "dependencies": kwargs.get('dependencies', [])
        }
        
        return patch_id

    def save_custom_patch(self, patch_id: str, filename: str = None):
        """Save a custom patch to file"""
        if patch_id not in self.patches:
            return False
            
        if not filename:
            filename = f"{patch_id}.py"
            
        filepath = os.path.join(self.patches_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                f.write(f'# Custom Patch: {self.patches[patch_id]["name"]}\n')
                f.write(f'# Generated by Professional Patch Tool\n\n')
                f.write('PATCHES = {\n')
                f.write(f'    "{patch_id}": {json.dumps(self.patches[patch_id], indent=4)}\n')
                f.write('}\n')
            return True
        except Exception as e:
            print(f"❌ Error saving patch: {e}")
            return False


class PredefinedFixes:
    """Applies predefined fixes with advanced features"""
    
    def __init__(self, patch_engine, file_manager, patch_library: PatchLibrary = None):
        self.patch_engine = patch_engine
        self.file_manager = file_manager
        self.patch_library = patch_library or PatchLibrary()
        self.applied_fixes = []

    def interactive_fixes_menu(self):
        """Interactive menu for applying predefined fixes"""
        while True:
            print(f"\n🛠️ PREDEFINED FIXES")
            print("=" * 60)
            
            categories = self.patch_library.get_categories()
            for i, (cat_id, cat_name) in enumerate(categories.items(), 1):
                patch_count = len(self.patch_library.get_patches_by_category(cat_id))
                print(f"{i}. {cat_name} ({patch_count} fixes)")
            
            print(f"{len(categories) + 1}. 🔍 Search fixes")
            print(f"{len(categories) + 2}. 💾 Custom patches")
            print(f"{len(categories) + 3}. 📊 Fix history")
            print("0. ↩️  Back to main menu")
            print("=" * 60)
            
            try:
                choice = input("\nSelect category: ").strip()
                
                if choice == '0':
                    break
                elif choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(categories):
                        cat_id = list(categories.keys())[choice_num - 1]
                        self._show_category_fixes(cat_id)
                    elif choice_num == len(categories) + 1:
                        self._search_fixes()
                    elif choice_num == len(categories) + 2:
                        self._custom_patches_menu()
                    elif choice_num == len(categories) + 3:
                        self._show_fix_history()
                    else:
                        print("❌ Invalid choice")
                else:
                    print("❌ Invalid input")
                    
            except KeyboardInterrupt:
                print("\n⏹️  Operation cancelled.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def _show_category_fixes(self, category: str):
        """Show fixes for a specific category"""
        patches = self.patch_library.get_patches_by_category(category)
        
        if not patches:
            print(f"❌ No fixes found in category: {category}")
            return
            
        while True:
            print(f"\n📁 {category.replace('_', ' ').title()} FIXES")
            print("=" * 50)
            
            patch_list = list(patches.items())
            for i, (patch_id, patch_def) in enumerate(patch_list, 1):
                severity_icon = self._get_severity_icon(patch_def.get('severity', 'medium'))
                print(f"{i}. {severity_icon} {patch_def['name']}")
                print(f"   📝 {patch_def['description']}")
            
            print("0. ↩️  Back")
            print("=" * 50)
            
            try:
                choice = input("\nSelect fix to view details: ").strip()
                
                if choice == '0':
                    break
                elif choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(patch_list):
                        patch_id, patch_def = patch_list[choice_num - 1]
                        self._show_fix_details(patch_id, patch_def)
                    else:
                        print("❌ Invalid choice")
                else:
                    print("❌ Invalid input")
                    
            except KeyboardInterrupt:
                break

    def _show_fix_details(self, patch_id: str, patch_def: Dict):
        """Show detailed information about a fix"""
        print(f"\n🔍 {patch_def['name']}")
        print("=" * 60)
        print(f"📝 Description: {patch_def['description']}")
        print(f"📁 Category: {patch_def.get('category', 'uncategorized')}")
        print(f"⚠️  Severity: {patch_def.get('severity', 'medium')}")
        print(f"👤 Author: {patch_def.get('author', 'Unknown')}")
        print(f"🔄 Version: {patch_def.get('version', '1.0')}")
        print(f"📄 Files: {', '.join(patch_def.get('files', ['**/*']))}")
        
        if patch_def.get('dependencies'):
            print(f"📦 Dependencies: {', '.join(patch_def['dependencies'])}")
        
        print(f"\n🔧 Patches to apply:")
        for i, patch in enumerate(patch_def.get('patches', []), 1):
            print(f"  {i}. {patch.get('type', 'unknown')}: {patch.get('pattern', 'N/A')}")
        
        print("\n1. ✅ Apply this fix")
        print("2. 🔍 Preview changes")
        print("3. 💾 Save as custom patch")
        print("0. ↩️  Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            self._apply_predefined_fix(patch_id, patch_def)
        elif choice == '2':
            self._preview_fix(patch_id, patch_def)
        elif choice == '3':
            self.patch_library.save_custom_patch(patch_id)
            print("✅ Fix saved as custom patch")

    def _apply_predefined_fix(self, patch_id: str, patch_def: Dict):
        """Apply a predefined fix"""
        print(f"\n🎯 Applying: {patch_def['name']}")
        
        # Find files matching the pattern
        target_files = self._find_target_files(patch_def.get('files', ['**/*']))
        
        if not target_files:
            print("❌ No files found matching the pattern")
            return False
            
        print(f"📄 Found {len(target_files)} files to patch")
        
        # Show files and get confirmation
        for i, file_path in enumerate(target_files[:10], 1):  # Show first 10 files
            print(f"  {i}. {file_path}")
        if len(target_files) > 10:
            print(f"  ... and {len(target_files) - 10} more files")
            
        confirm = input("\n✅ Apply fix to these files? (y/n): ").lower()
        if confirm != 'y':
            print("❌ Fix application cancelled")
            return False
            
        # Apply patches to each file
        success_count = 0
        for file_path in target_files:
            if self._apply_fix_to_file(file_path, patch_def):
                success_count += 1
                
        print(f"\n🎉 Successfully applied fix to {success_count}/{len(target_files)} files")
        
        # Record the application
        self.applied_fixes.append({
            'patch_id': patch_id,
            'name': patch_def['name'],
            'timestamp': self._get_timestamp(),
            'files_affected': success_count,
            'total_files': len(target_files)
        })
        
        return success_count > 0

    def _apply_fix_to_file(self, file_path: str, patch_def: Dict) -> bool:
        """Apply a fix to a specific file"""
        file_info = self.file_manager.get_file_info(file_path)
        if not file_info:
            return False
            
        patches = []
        for patch_config in patch_def.get('patches', []):
            patches.append({
                'type': patch_config['type'],
                'pattern': patch_config.get('pattern', ''),
                'code': patch_config.get('replacement', '').split('\n') if isinstance(patch_config.get('replacement'), str) else patch_config.get('code', []),
                'line_number': patch_config.get('line_number'),
                'start_line': patch_config.get('start_line'),
                'end_line': patch_config.get('end_line'),
                'description': f"Predefined fix: {patch_def['name']}"
            })
            
        success, result = self.patch_engine.apply_patches(file_path, patches)
        return success

    def _find_target_files(self, file_patterns: List[str]) -> List[str]:
        """Find files matching the given patterns"""
        import fnmatch
        
        target_files = []
        base_path = self.file_manager.base_path
        
        for pattern in file_patterns:
            # Simple glob pattern matching
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, base_path)
                    
                    if any(fnmatch.fnmatch(rel_path, pattern) for pattern in file_patterns):
                        target_files.append(rel_path)
                        
        return list(set(target_files))  # Remove duplicates

    def _preview_fix(self, patch_id: str, patch_def: Dict):
        """Preview changes without applying"""
        print(f"\n🔍 Previewing: {patch_def['name']}")
        print("⚠️  Preview mode - no changes will be applied")
        
        target_files = self._find_target_files(patch_def.get('files', ['**/*']))[:5]  # Limit preview
        
        for file_path in target_files:
            print(f"\n📄 {file_path}:")
            file_info = self.file_manager.get_file_info(file_path)
            if file_info:
                # Simulate patches to show what would change
                for patch_config in patch_def.get('patches', []):
                    matches = self.patch_engine.find_code_blocks(
                        file_info, 
                        patch_config.get('pattern', ''),
                        context_lines=2
                    )
                    if matches:
                        for match in matches:
                            print(f"  📍 Line {match['line_number']}: {match['full_match'][:50]}...")
                    else:
                        print("  ✅ No changes needed")

    def _search_fixes(self):
        """Search for fixes by keyword"""
        query = input("\n🔍 Search fixes: ").strip()
        if not query:
            return
            
        results = self.patch_library.search_patches(query)
        
        if not results:
            print("❌ No fixes found matching your search")
            return
            
        print(f"\n🔍 SEARCH RESULTS for '{query}':")
        for patch_id, patch_def in results.items():
            print(f"  • {patch_def['name']} ({patch_def.get('category', 'uncategorized')})")
            print(f"    {patch_def['description']}")

    def _custom_patches_menu(self):
        """Menu for managing custom patches"""
        print("\n💾 CUSTOM PATCHES")
        print("1. 🆕 Create new custom patch")
        print("2. 📋 List custom patches") 
        print("0. ↩️  Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            self._create_custom_patch()
        elif choice == '2':
            self._list_custom_patches()

    def _create_custom_patch(self):
        """Interactive custom patch creation"""
        print("\n🆕 CREATE CUSTOM PATCH")
        
        name = input("Patch name: ").strip()
        if not name:
            print("❌ Patch name is required")
            return
            
        description = input("Description: ").strip()
        category = input("Category [custom]: ").strip() or "custom"
        
        print("\n📝 Now define the patches (empty line to finish):")
        patches = []
        
        while True:
            print(f"\nPatch #{len(patches) + 1}:")
            patch_type = input("Type (insert_at_line/replace_range/replace_pattern/append) [replace_pattern]: ").strip() or "replace_pattern"
            
            patch_config = {'type': patch_type}
            
            if patch_type == 'insert_at_line':
                patch_config['line_number'] = int(input("Line number: "))
            elif patch_type == 'replace_range':
                patch_config['start_line'] = int(input("Start line: "))
                patch_config['end_line'] = int(input("End line: "))
            elif patch_type in ['replace_pattern', 'insert_after', 'insert_before']:
                patch_config['pattern'] = input("Pattern (regex): ").strip()
                
            patch_config['code'] = self._get_multiline_input("Replacement code (empty line to finish): ")
            
            patches.append(patch_config)
            
            more = input("\nAdd another patch? (y/n) [n]: ").strip().lower()
            if more != 'y':
                break
                
        # Create the patch
        patch_id = self.patch_library.create_custom_patch(
            name, description, patches, category
        )
        
        print(f"✅ Custom patch '{name}' created with ID: {patch_id}")
        
        save = input("Save to file? (y/n) [y]: ").strip().lower()
        if save != 'n':
            self.patch_library.save_custom_patch(patch_id)

    def _list_custom_patches(self):
        """List all custom patches"""
        custom_patches = {pid: patch for pid, patch in self.patch_library.patches.items() 
                         if patch.get('category') == 'custom'}
        
        if not custom_patches:
            print("❌ No custom patches found")
            return
            
        print("\n💾 CUSTOM PATCHES:")
        for patch_id, patch_def in custom_patches.items():
            print(f"  • {patch_def['name']} ({patch_id})")
            print(f"    {patch_def['description']}")

    def _show_fix_history(self):
        """Show history of applied fixes"""
        if not self.applied_fixes:
            print("❌ No fix history found")
            return
            
        print("\n📊 FIX HISTORY:")
        for fix in self.applied_fixes[-10:]:  # Show last 10
            print(f"  • {fix['timestamp']}: {fix['name']}")
            print(f"    Files: {fix['files_affected']}/{fix['total_files']}")

    def _get_severity_icon(self, severity: str) -> str:
        """Get icon for severity level"""
        icons = {
            'critical': '🔴',
            'high': '🟠', 
            'medium': '🟡',
            'low': '🟢'
        }
        return icons.get(severity, '⚪')

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _get_multiline_input(self, prompt: str) -> List[str]:
        """Get multiline input from user"""
        print(prompt)
        lines = []
        while True:
            line = input().strip()
            if not line:
                break
            lines.append(line)
        return lines
