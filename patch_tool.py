#!/usr/bin/env python3
"""
Professional Patch Tool for Ziver Chain
Interactive file patching with UNIX-style navigation
"""

import os
import sys
import re
import datetime
from typing import List, Dict, Any, Optional
from utils import RegexUtils, FuzzyMatcher, LineUtils, Validation, PatchValidator
from patches import PATCHES

# Import core modules
from core import ConfigManager, FileManager, NavigationSystem, PatchEngine

# Import features modules
from features import PatchLibrary, PredefinedFixes, BatchOperations, DiffEngine, PatchHistory

# Import UI modules
from ui import MainMenu, SyntaxHighlighter, PreviewRenderer


class ProfessionalPatchTool:
    def __init__(self):
        # Start from current working directory where tool was run
        self.base_path = os.path.expanduser('~')
        
        # Initialize core modules
        self.config_manager = ConfigManager(self.base_path)
        self.file_manager = FileManager(self.base_path, self.config_manager)
        self.navigation = NavigationSystem(self.file_manager, self.config_manager)
        self.patch_engine = PatchEngine(self.file_manager, self.config_manager)
        
        # Initialize UI modules
        self.syntax_highlighter = SyntaxHighlighter(self.config_manager)
        self.preview_renderer = PreviewRenderer(self.syntax_highlighter, self.config_manager)
        self.main_menu = MainMenu(self)
        
        # Initialize features modules
        self.patch_library = PatchLibrary()
        self.predefined_fixes = PredefinedFixes(self.patch_engine, self.file_manager, self.patch_library)
        self.batch_operations = BatchOperations(self.patch_engine, self.file_manager)
        self.diff_engine = DiffEngine(self.file_manager)
        self.patch_history = PatchHistory(self.file_manager)
        
        # Maintain compatibility with existing code
        self.current_directory = self.navigation.current_directory
        self.applied_patches = self.patch_engine.applied_patches
        self.backup_dir = self.file_manager.backup_dir
        self.config_file = self.config_manager.config_file
        self.config = self.config_manager.config
        self.file_history = self.file_manager.file_history
        
        # Initialize utility modules
        self.regex_utils = RegexUtils()
        self.fuzzy_matcher = FuzzyMatcher()
        self.line_utils = LineUtils() 
        self.validation = Validation()
        self.patch_validator = PatchValidator(self.regex_utils)
    
        # Load patches library
        self.patches_library = PATCHES

    # Delegate methods to core modules for backward compatibility
    def _load_config(self) -> Dict[str, Any]:
        return self.config_manager.config

    def _save_config(self):
        return self.config_manager.save_config()

    def _resolve_path(self, path: str) -> str:
        return self.file_manager.resolve_path(path)

    def _list_directory(self, path: str = None):
        self.navigation.display_directory_listing(path)

    def navigate_to_file(self) -> Optional[str]:
        return self.navigation.navigate_to_file()

    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        return self.file_manager.get_file_info(file_path)

    def _detect_language(self, file_path: str) -> str:
        return self.file_manager._detect_language(file_path)

    def display_file_preview(self, file_info: Dict[str, Any], start_line: int = 1, num_lines: int = 20):
        """Display a preview of the file with syntax hints"""
        preview = self.preview_renderer.render_file_preview(file_info, start_line, num_lines)
        print(preview)

    def _highlight_syntax(self, line: str, language: str) -> str:
        """Basic syntax highlighting (ANSI colors) - kept for compatibility"""
        return self.syntax_highlighter.highlight_line(line, language)

    def create_backup(self, file_path: str) -> str:
        success, backup_path = self.file_manager.create_backup(file_path)
        return backup_path if success else ""

    def show_line_range(self, file_info: Dict[str, Any], start_line: int, end_line: int):
        """Show specific line range with context"""
        preview = self.preview_renderer.render_line_range(file_info, start_line, end_line)
        print(preview)

    def find_code_block(self, file_info: Dict[str, Any], search_pattern: str, context_lines: int = 3) -> List[Dict[str, Any]]:
        return self.patch_engine.find_code_blocks(file_info, search_pattern, context_lines)

    def patch_file_interactive(self, file_path: str) -> bool:
        """Interactive file patching with full user control - kept for compatibility"""
        from ui import PatchMenu
        patch_menu = PatchMenu(self)
        return patch_menu.show_patch_menu(file_path)

    def _apply_patches(self, file_path: str, file_info: Dict[str, Any]) -> bool:
        """Apply all queued patches using the patch engine - kept for compatibility"""
        patches = self.patch_engine.applied_patches
        
        if not patches:
            print("❌ No patches to apply")
            return False

        print(f"\n📋 Patches to apply ({len(patches)}):")
        for i, patch in enumerate(patches, 1):
            print(f"  {i}. {patch['description']}")

        if self.config_manager.get("confirm_applications", True):
            confirm = input("\n✅ Apply these patches? (y/n): ").lower()
            if confirm != 'y':
                print("❌ Patch application cancelled")
                return False

        # Use the patch engine to apply patches
        success, result = self.patch_engine.apply_patches(file_path, patches)
        
        if success:
            print(f"\n🎉 Successfully applied {result['successful_patches']}/{len(patches)} patches")
            print(f"📊 File changed: {result['original_lines']} → {result['new_lines']} lines")
            
            # Record in history
            original_content = self.file_manager.read_file_lines(file_path)
            if original_content:
                self.patch_history.record_operation(file_path, patches, original_content, result)
            
            # Show summary of changes
            self._show_patch_summary(file_path)
            return True
        else:
            print(f"❌ Patch application failed: {result.get('error', 'Unknown error')}")
            if 'failed_patches' in result:
                for failed in result['failed_patches']:
                    print(f"   - {failed['patch']['description']}: {failed['error']}")
            return False

    def _show_patch_summary(self, file_path: str):
        """Show summary of applied patches"""
        file_info = self.file_manager.get_file_info(file_path)
        if file_info:
            print(f"\n📄 Final file state: {file_info['lines']} lines")

            if file_info['lines'] > 0:
                print("\nFirst 5 lines:")
                self.show_line_range(file_info, 1, min(5, file_info['lines']))

                if file_info['lines'] > 5:
                    print("\nLast 5 lines:")
                    self.show_line_range(file_info, max(1, file_info['lines']-4), file_info['lines'])

    def _settings_menu(self):
        """Configuration settings menu - kept for compatibility"""
        from ui import SettingsMenu
        settings_menu = SettingsMenu(self)
        settings_menu.show_settings_menu()

    def restore_backup(self, file_path: str) -> bool:
        return self.file_manager.restore_backup(file_path)

    def cleanup_old_backups(self, days: int = 30):
        self.file_manager.cleanup_old_backups(days)

    def run(self):
        """Main application entry point"""
        print("🚀 PROFESSIONAL PATCH TOOL")
        print("="*60)
        print(f"📁 Started in: {self.current_directory}")
        print(f"🔧 Features: Predefined fixes, Batch operations, Diff engine, Patch history")
        print("="*60)
        
        # Main application loop
        try:
            while True:
                choice = self.main_menu.show_main_menu()
                if not self.main_menu.handle_main_choice(choice):
                    break
                    
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main interactive interface"""
    tool = ProfessionalPatchTool()
    tool.run()


# Predefined fixes functions (kept for compatibility)
def apply_predefined_fixes(tool: ProfessionalPatchTool):
    """Apply predefined fixes for common issues"""
    fixes = {
        '1': ('Fix Import Statements', 'src/zexus/evaluator.py', fix_import_statements),
        '2': ('Add Missing Function', 'src/zexus/parser.py', add_missing_function),
        '3': ('Fix Syntax Error', 'src/zexus/evaluator.py', fix_syntax_error),
        '4': ('Update Configuration', 'config.json', update_configuration),
    }

    print("\n🛠️ PREDEFINED FIXES")
    for key, (name, file, _) in fixes.items():
        print(f"{key}. {name} ({file})")
    print("0. Back")

    choice = input("\nSelect fix: ").strip()
    if choice in fixes:
        name, file, fix_func = fixes[choice]
        print(f"\nApplying: {name}")
        if fix_func(tool, file):
            print(f"✅ {name} applied successfully")
        else:
            print(f"❌ Failed to apply {name}")
    elif choice != '0':
        print("❌ Invalid choice")

def fix_import_statements(tool: ProfessionalPatchTool, file_path: str) -> bool:
    """Example fix: Add missing import statements"""
    patches = [
        {
            'type': 'insert_at_line',
            'line_number': 1,
            'code': ['import sys', 'import os', 'from typing import Dict, List'],
            'description': 'Add standard imports at top of file'
        }
    ]

    # Apply patches directly
    file_info = tool.get_file_info(file_path)
    if not file_info:
        return False

    tool.applied_patches = patches
    return tool._apply_patches(file_path, file_info)

def add_missing_function(tool: ProfessionalPatchTool, file_path: str) -> bool:
    """Example fix: Add a missing function"""
    patches = [
        {
            'type': 'append',
            'code': [
                '',
                'def missing_function(arg1, arg2):',
                '    """A function that was missing"""',
                '    result = arg1 + arg2',
                '    return result'
            ],
            'description': 'Add missing_function to end of file'
        }
    ]

    file_info = tool.get_file_info(file_path)
    if not file_info:
        return False

    tool.applied_patches = patches
    return tool._apply_patches(file_path, file_info)

def fix_syntax_error(tool: ProfessionalPatchTool, file_path: str) -> bool:
    """Example fix: Fix common syntax errors"""
    patches = [
        {
            'type': 'replace_pattern',
            'pattern': r'print\s*\(.*[^)]$',
            'code': ['print("Fixed syntax error")'],
            'description': 'Fix incomplete print statement'
        }
    ]

    file_info = tool.get_file_info(file_path)
    if not file_info:
        return False

    tool.applied_patches = patches
    return tool._apply_patches(file_path, file_info)

def update_configuration(tool: ProfessionalPatchTool, file_path: str) -> bool:
    """Example fix: Update configuration values"""
    patches = [
        {
            'type': 'replace_pattern',
            'pattern': r'"timeout":\s*\d+',
            'code': ['    "timeout": 30'],
            'description': 'Update timeout value to 30 seconds'
        }
    ]

    file_info = tool.get_file_info(file_path)
    if not file_info:
        return False

    tool.applied_patches = patches
    return tool._apply_patches(file_path, file_info)

if __name__ == "__main__":
    main()
