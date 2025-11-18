#!/usr/bin/env python3
"""
Interactive Menus for Professional Patch Tool
All menu systems and user interaction handlers
"""

import os
import sys
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path


class MenuSystem:
    """Base menu system with common functionality"""
    
    def __init__(self, tool_instance):
        self.tool = tool_instance
        self.menu_history = []
        self.current_context = {}

    def display_menu(self, title: str, options: List[Dict], prompt: str = "Select option") -> str:
        """Display a menu and get user selection"""
        print(f"\n{title}")
        print("=" * 60)
        
        for option in options:
            if option.get('separator'):
                print("-" * 60)
            else:
                print(f"{option['key']}. {option['label']}")
                if option.get('description'):
                    print(f"   {option['description']}")
        
        print("=" * 60)
        
        while True:
            try:
                choice = input(f"\n{prompt}: ").strip()
                
                # Check if choice matches any option key
                valid_choices = [opt['key'] for opt in options if not opt.get('separator')]
                if choice in valid_choices:
                    self.menu_history.append({
                        'menu': title,
                        'choice': choice,
                        'context': self.current_context.copy()
                    })
                    return choice
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n⏹️  Operation cancelled.")
                return '0'
            except EOFError:
                print("\n👋 Goodbye!")
                sys.exit(0)

    def get_confirmation(self, message: str, default: bool = False) -> bool:
        """Get user confirmation"""
        default_text = "Y/n" if default else "y/N"
        response = input(f"{message} [{default_text}]: ").strip().lower()
        
        if not response:
            return default
        return response in ['y', 'yes', '1', 'true']

    def get_input(self, prompt: str, default: str = "", required: bool = False) -> str:
        """Get user input with validation"""
        while True:
            if default:
                full_prompt = f"{prompt} [{default}]: "
            else:
                full_prompt = f"{prompt}: "
                
            try:
                value = input(full_prompt).strip()
                
                if not value:
                    if default:
                        return default
                    elif required:
                        print("❌ This field is required.")
                        continue
                    else:
                        return ""
                else:
                    return value
                    
            except KeyboardInterrupt:
                print("\n⏹️  Input cancelled.")
                return ""

    def get_multiline_input(self, prompt: str, end_marker: str = "") -> List[str]:
        """Get multiline input from user"""
        print(prompt)
        print(">" * 40)
        
        lines = []
        while True:
            try:
                line = input()
                if end_marker and line.strip() == end_marker:
                    break
                if not end_marker and line == "":
                    break
                lines.append(line)
            except KeyboardInterrupt:
                print("\n⏹️  Input cancelled.")
                break
            except EOFError:
                break
                
        print("<" * 40)
        return lines

    def show_breadcrumbs(self):
        """Show navigation breadcrumbs"""
        if self.menu_history:
            crumbs = " > ".join([f"{item['menu']}" for item in self.menu_history[-3:]])
            print(f"\n📍 {crumbs}")

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')


class MainMenu(MenuSystem):
    """Main application menu system"""
    
    def __init__(self, tool_instance):
        super().__init__(tool_instance)
        self.features_enabled = {
            'batch_operations': True,
            'predefined_fixes': True,
            'diff_preview': True,
            'patch_history': True
        }

    def show_main_menu(self):
        """Display the main application menu"""
        options = [
            {'key': '1', 'label': '📝 Navigate & patch file (UNIX-style)', 'description': 'Interactive file patching'},
            {'key': '2', 'label': '📝 Enter file path directly', 'description': 'Quick file access'},
            {'key': '3', 'label': '🛠️ Predefined fixes', 'description': 'Apply automated fixes'},
            {'key': '4', 'label': '🔀 Batch operations', 'description': 'Multi-file processing'},
            {'key': '5', 'label': '📂 File history', 'description': 'Recent files'},
            {'key': '6', 'label': '🔧 Advanced tools', 'description': 'Additional features'},
            {'key': '7', 'label': '⚙️ Settings', 'description': 'Configure tool behavior'},
            {'key': '8', 'label': '❌ Exit', 'description': 'Exit the application'}
        ]
        
        return self.display_menu("🚀 PROFESSIONAL PATCH TOOL", options, "Select option (1-8)")

    def show_advanced_tools_menu(self):
        """Display advanced tools menu"""
        options = [
            {'key': '1', 'label': '🔍 Diff preview', 'description': 'Preview changes before applying'},
            {'key': '2', 'label': '📋 Patch history', 'description': 'Undo/redo operations'},
            {'key': '3', 'label': '💾 Backup management', 'description': 'Manage file backups'},
            {'key': '4', 'label': '📊 File analysis', 'description': 'Analyze code patterns'},
            {'key': '0', 'label': '↩️ Back to main menu', 'description': 'Return to main menu'}
        ]
        
        return self.display_menu("🔧 ADVANCED TOOLS", options)

    def handle_main_choice(self, choice: str) -> bool:
        """Handle main menu choice"""
        if choice == '1':
            return self._handle_navigation()
        elif choice == '2':
            return self._handle_direct_path()
        elif choice == '3':
            return self._handle_predefined_fixes()
        elif choice == '4':
            return self._handle_batch_operations()
        elif choice == '5':
            return self._handle_file_history()
        elif choice == '6':
            return self._handle_advanced_tools()
        elif choice == '7':
            return self._handle_settings()
        elif choice == '8':
            print("👋 Goodbye!")
            return False
        return True

    def _handle_navigation(self) -> bool:
        """Handle UNIX-style navigation"""
        file_path = self.tool.navigation.navigate_to_file()
        if file_path:
            patch_menu = PatchMenu(self.tool)
            patch_menu.show_patch_menu(file_path)
            self.tool.patch_engine.applied_patches = []  # Reset for next operation
        return True

    def _handle_direct_path(self) -> bool:
        """Handle direct file path entry"""
        file_path = self.get_input("Enter file path (absolute or relative)")
        if file_path:
            abs_path = self.tool.file_manager.resolve_path(file_path)
            if self.tool.file_manager.file_exists(abs_path):
                rel_path = self.tool.file_manager._get_relative_path(abs_path)
                print(f"✅ Selected file: {rel_path}")
                patch_menu = PatchMenu(self.tool)
                patch_menu.show_patch_menu(rel_path)
                self.tool.patch_engine.applied_patches = []
            else:
                print(f"❌ File not found: {abs_path}")
        return True

    def _handle_predefined_fixes(self) -> bool:
        """Handle predefined fixes"""
        if hasattr(self.tool, 'predefined_fixes'):
            self.tool.predefined_fixes.interactive_fixes_menu()
        else:
            print("❌ Predefined fixes feature not available")
        return True

    def _handle_batch_operations(self) -> bool:
        """Handle batch operations"""
        if hasattr(self.tool, 'batch_operations'):
            self.tool.batch_operations.interactive_batch_menu()
        else:
            print("❌ Batch operations feature not available")
        return True

    def _handle_file_history(self) -> bool:
        """Handle file history"""
        history = self.tool.file_manager.get_history()
        if not history:
            print("❌ No recent files")
            return True
            
        options = [{'key': str(i+1), 'label': f"📄 {file_path}"} 
                  for i, file_path in enumerate(history)]
        options.append({'key': '0', 'label': '↩️ Back'})
        
        choice = self.display_menu("📂 RECENT FILES", options, "Select file")
        
        if choice != '0' and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(history):
                patch_menu = PatchMenu(self.tool)
                patch_menu.show_patch_menu(history[idx])
                
        return True

    def _handle_advanced_tools(self) -> bool:
        """Handle advanced tools menu"""
        while True:
            choice = self.show_advanced_tools_menu()
            
            if choice == '1':
                self._handle_diff_preview()
            elif choice == '2':
                self._handle_patch_history()
            elif choice == '3':
                self._handle_backup_management()
            elif choice == '4':
                self._handle_file_analysis()
            elif choice == '0':
                break
                
        return True

    def _handle_diff_preview(self) -> bool:
        """Handle diff preview"""
        print("🔍 Diff preview - select a file to see changes")
        file_path = self.tool.navigation.navigate_to_file()
        if file_path and hasattr(self.tool, 'diff_engine'):
            # This would show diff for current patches
            if self.tool.patch_engine.applied_patches:
                self.tool.diff_engine.interactive_diff_menu(
                    file_path, self.tool.patch_engine.applied_patches
                )
            else:
                print("❌ No patches to preview")
        return True

    def _handle_patch_history(self) -> bool:
        """Handle patch history"""
        if hasattr(self.tool, 'patch_history'):
            self.tool.patch_history.interactive_history_menu()
        else:
            print("❌ Patch history feature not available")
        return True

    def _handle_backup_management(self) -> bool:
        """Handle backup management"""
        options = [
            {'key': '1', 'label': '🔙 Restore from backup', 'description': 'Restore previous version'},
            {'key': '2', 'label': '🧹 Cleanup old backups', 'description': 'Remove old backup files'},
            {'key': '3', 'label': '📊 Backup statistics', 'description': 'Show backup information'},
            {'key': '0', 'label': '↩️ Back', 'description': 'Return to previous menu'}
        ]
        
        choice = self.display_menu("💾 BACKUP MANAGEMENT", options)
        
        if choice == '1':
            file_path = self.get_input("Enter file path to restore")
            if file_path:
                self.tool.file_manager.restore_backup(file_path)
        elif choice == '2':
            try:
                days = int(self.get_input("Delete backups older than (days)", "30"))
                self.tool.file_manager.cleanup_old_backups(days)
            except ValueError:
                print("❌ Invalid number")
        elif choice == '3':
            self._show_backup_statistics()
            
        return True

    def _handle_file_analysis(self) -> bool:
        """Handle file analysis"""
        print("📊 File analysis - this feature is coming soon!")
        return True

    def _handle_settings(self) -> bool:
        """Handle settings menu"""
        settings_menu = SettingsMenu(self.tool)
        settings_menu.show_settings_menu()
        return True

    def _show_backup_statistics(self):
        """Show backup statistics"""
        backup_dir = self.tool.file_manager.backup_dir
        if os.path.exists(backup_dir):
            backups = list(Path(backup_dir).glob('*.bak'))
            print(f"\n📊 BACKUP STATISTICS")
            print(f"📁 Backup directory: {backup_dir}")
            print(f"📄 Total backups: {len(backups)}")
            
            if backups:
                # Group by file type
                by_extension = {}
                total_size = 0
                
                for backup in backups:
                    ext = backup.suffixes[-2] if len(backup.suffixes) > 1 else 'unknown'
                    by_extension[ext] = by_extension.get(ext, 0) + 1
                    total_size += backup.stat().st_size
                    
                print(f"💾 Total size: {self._format_size(total_size)}")
                print(f"\n📁 Backups by type:")
                for ext, count in by_extension.items():
                    print(f"  {ext}: {count} files")
        else:
            print("❌ Backup directory not found")

    def _format_size(self, size_bytes: int) -> str:
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


class PatchMenu(MenuSystem):
    """Patch-specific menu system"""
    
    def __init__(self, tool_instance):
        super().__init__(tool_instance)
        self.current_file_info = None

    def show_patch_menu(self, file_path: str):
        """Show the patch menu for a specific file"""
        self.current_file_info = self.tool.file_manager.get_file_info(file_path)
        
        if not self.current_file_info:
            print(f"❌ File not found: {file_path}")
            return False

        # Add to history
        self.tool.file_manager.add_to_history(file_path)

        print(f"\n🎯 Patching: {file_path}")
        print(f"📊 File Info: {self.current_file_info['lines']} lines, "
              f"{self.current_file_info['size']} bytes, {self.current_file_info['language']}")

        while True:
            options = [
                {'key': '1', 'label': '📋 Show file preview', 'description': 'View file content'},
                {'key': '2', 'label': '🔍 Search for code pattern', 'description': 'Find code patterns'},
                {'key': '3', 'label': '📍 Insert code at line', 'description': 'Insert at specific line'},
                {'key': '4', 'label': '🔄 Replace code block', 'description': 'Replace code sections'},
                {'key': '5', 'label': '➕ Insert after pattern', 'description': 'Insert after matching code'},
                {'key': '6', 'label': '➖ Insert before pattern', 'description': 'Insert before matching code'},
                {'key': '7', 'label': '📤 Append to end', 'description': 'Add to file end'},
                {'key': '8', 'label': '🗑️ Delete code block', 'description': 'Remove code sections'},
                {'key': '9', 'label': '📋 Show patch queue', 'description': 'View pending patches'},
                {'key': '10', 'label': '🔍 Preview changes', 'description': 'See changes before applying'},
                {'key': '11', 'label': '💾 Apply patches', 'description': 'Save all changes'},
                {'key': '12', 'label': '⚙️ Settings', 'description': 'Configure patching'},
                {'key': '0', 'label': '❌ Cancel and exit', 'description': 'Discard changes and exit'}
            ]
            
            choice = self.display_menu("🔧 PATCH MENU", options, "Select option (0-12)")
            
            if not self._handle_patch_choice(choice, file_path):
                break

        return True

    def _handle_patch_choice(self, choice: str, file_path: str) -> bool:
        """Handle patch menu choice"""
        handlers = {
            '1': self._show_preview_menu,
            '2': self._search_pattern_menu,
            '3': self._insert_at_line_menu,
            '4': self._replace_block_menu,
            '5': self._insert_after_menu,
            '6': self._insert_before_menu,
            '7': self._append_menu,
            '8': self._delete_block_menu,
            '9': self._show_patch_queue,
            '10': self._preview_changes,
            '11': lambda: self._apply_patches(file_path),
            '12': self._show_patch_settings,
            '0': lambda: False
        }
        
        handler = handlers.get(choice)
        if handler:
            if callable(handler):
                return handler()
            else:
                return handler(file_path) if 'file_path' in handler.__code__.co_varnames else handler()
        return True

    def _show_preview_menu(self) -> bool:
        """Show file preview with navigation"""
        if not self.current_file_info:
            return True
            
        start_line = 1
        while True:
            self.tool.display_file_preview(self.current_file_info, start_line)
            
            options = [
                {'key': 'n', 'label': 'Next page'},
                {'key': 'p', 'label': 'Previous page'},
                {'key': 'g', 'label': 'Go to line'},
                {'key': 's', 'label': 'Show specific range'},
                {'key': 'b', 'label': 'Back to patch menu'}
            ]
            
            choice = self.display_menu("📋 FILE PREVIEW", options, "Choose navigation")
            
            if choice == 'n':
                start_line = min(start_line + 20, self.current_file_info['lines'] - 19)
            elif choice == 'p':
                start_line = max(1, start_line - 20)
            elif choice == 'g':
                try:
                    line_num = int(self.get_input("Go to line"))
                    start_line = max(1, min(line_num, self.current_file_info['lines'] - 19))
                except ValueError:
                    print("❌ Invalid line number")
            elif choice == 's':
                try:
                    start = int(self.get_input("Start line"))
                    end = int(self.get_input("End line"))
                    self.tool.show_line_range(self.current_file_info, start, end)
                except ValueError:
                    print("❌ Invalid line numbers")
            elif choice == 'b':
                break
                
        return True

    def _search_pattern_menu(self) -> bool:
        """Search for code patterns"""
        pattern = self.get_input("Enter search pattern (regex)")
        if not pattern:
            return True
            
        matches = self.tool.patch_engine.find_code_blocks(self.current_file_info, pattern)
        
        if not matches:
            print("❌ No matches found.")
            return True
            
        print(f"\n🔍 Found {len(matches)} matches:")
        for i, match in enumerate(matches):
            print(f"\n[{i+1}] Line {match['line_number']}:")
            print(f"    Match: {match['full_match'][:100]}{'...' if len(match['full_match']) > 100 else ''}")

            if self.get_confirmation("Show context?"):
                self.tool.show_line_range(
                    self.current_file_info, 
                    match['context_start'], 
                    match['context_end']
                )
                
        return True

    def _insert_at_line_menu(self) -> bool:
        """Insert code at specific line"""
        try:
            line_num = int(self.get_input("Enter line number to insert at"))
            if line_num < 1 or line_num > self.current_file_info['lines'] + 1:
                print("❌ Invalid line number")
                return True

            print(f"\nCurrent content at line {line_num}:")
            if line_num <= self.current_file_info['lines']:
                current_line = self.current_file_info['line_list'][line_num-1]
                if self.tool.config_manager.get("enable_syntax_hints", True):
                    current_line = self.tool._highlight_syntax(current_line, self.current_file_info['language'])
                print(f"{line_num:4d} │ {current_line}")
            else:
                print("(end of file)")

            print("\nEnter code to insert:")
            new_code = self.get_multiline_input("")

            if new_code:
                self.tool.patch_engine.applied_patches.append({
                    'type': 'insert_at_line',
                    'line_number': line_num,
                    'code': new_code,
                    'description': f'Insert {len(new_code)} lines at line {line_num}'
                })
                print("✅ Patch queued for application")
        except ValueError:
            print("❌ Invalid line number")
            
        return True

    def _replace_block_menu(self) -> bool:
        """Replace code block menu"""
        options = [
            {'key': '1', 'label': 'Replace by line range'},
            {'key': '2', 'label': 'Replace by pattern match'},
            {'key': '3', 'label': 'Replace all pattern matches'}
        ]
        
        choice = self.display_menu("🔄 REPLACE CODE BLOCK", options)
        
        if choice == '1':
            self._replace_by_line_range()
        elif choice == '2':
            self._replace_by_pattern(single_match=True)
        elif choice == '3':
            self._replace_by_pattern(single_match=False)
            
        return True

    def _replace_by_line_range(self):
        """Replace by line range"""
        try:
            start_line = int(self.get_input("Start line"))
            end_line = int(self.get_input("End line"))

            if (start_line < 1 or end_line > self.current_file_info['lines'] or 
                start_line > end_line):
                print("❌ Invalid line range")
                return

            print(f"\nCurrent content (lines {start_line}-{end_line}):")
            self.tool.show_line_range(self.current_file_info, start_line, end_line)

            print("\nEnter replacement code:")
            new_code = self.get_multiline_input("")

            if new_code:
                self.tool.patch_engine.applied_patches.append({
                    'type': 'replace_range',
                    'start_line': start_line,
                    'end_line': end_line,
                    'code': new_code,
                    'description': f'Replace lines {start_line}-{end_line} with {len(new_code)} lines'
                })
                print("✅ Patch queued for application")

        except ValueError:
            print("❌ Invalid line numbers")

    def _replace_by_pattern(self, single_match: bool = True):
        """Replace by pattern matching"""
        pattern = self.get_input("Enter pattern to replace (regex)")
        if not pattern:
            return

        matches = self.tool.patch_engine.find_code_blocks(self.current_file_info, pattern, context_lines=2)
        if not matches:
            print("❌ No matches found")
            return

        if single_match:
            match = matches[0]
            print(f"\nFound match at line {match['line_number']}:")
            self.tool.show_line_range(self.current_file_info, match['context_start'], match['context_end'])

            print("\nEnter replacement code:")
            new_code = self.get_multiline_input("")

            if new_code:
                self.tool.patch_engine.applied_patches.append({
                    'type': 'replace_pattern',
                    'pattern': pattern,
                    'code': new_code,
                    'description': f'Replace pattern at line {match["line_number"]}',
                    'match_line': match['line_number']
                })
                print("✅ Patch queued for application")
        else:
            print(f"\nFound {len(matches)} matches. Replace all?")
            if self.get_confirmation("Confirm replacement for all matches"):
                print("\nEnter replacement code (will be applied to all matches):")
                new_code = self.get_multiline_input("")

                if new_code:
                    for match in matches:
                        self.tool.patch_engine.applied_patches.append({
                            'type': 'replace_pattern_all',
                            'pattern': pattern,
                            'code': new_code,
                            'description': f'Replace pattern at line {match["line_number"]}',
                            'match_line': match['line_number']
                        })
                    print(f"✅ Queued replacement for {len(matches)} matches")

    def _insert_after_menu(self) -> bool:
        """Insert code after pattern"""
        return self._insert_relative_to_pattern('after')

    def _insert_before_menu(self) -> bool:
        """Insert code before pattern"""
        return self._insert_relative_to_pattern('before')

    def _insert_relative_to_pattern(self, position: str) -> bool:
        """Insert code relative to pattern (before/after)"""
        pattern = self.get_input(f"Enter pattern to insert {position} (regex)")
        if not pattern:
            return True

        matches = self.tool.patch_engine.find_code_blocks(self.current_file_info, pattern)
        if not matches:
            print("❌ Pattern not found")
            return True

        print(f"\nFound {len(matches)} matches. Will insert {position} first match at line {matches[0]['line_number']}")
        self.tool.show_line_range(
            self.current_file_info, 
            matches[0]['line_number']-1, 
            matches[0]['line_number']+1
        )

        print(f"\nEnter code to insert {position} pattern:")
        new_code = self.get_multiline_input("")

        if new_code:
            patch_type = f'insert_{position}'
            self.tool.patch_engine.applied_patches.append({
                'type': patch_type,
                position: pattern,
                'code': new_code,
                'description': f'Insert {len(new_code)} lines {position} pattern at line {matches[0]["line_number"]}'
            })
            print("✅ Patch queued for application")
            
        return True

    def _append_menu(self) -> bool:
        """Append code to end of file"""
        print(f"\nAppending to end of file (currently {self.current_file_info['lines']} lines)")
        print("Last 5 lines:")
        self.tool.show_line_range(
            self.current_file_info, 
            max(1, self.current_file_info['lines']-4), 
            self.current_file_info['lines']
        )

        print("\nEnter code to append:")
        new_code = self.get_multiline_input("")

        if new_code:
            self.tool.patch_engine.applied_patches.append({
                'type': 'append',
                'code': new_code,
                'description': f'Append {len(new_code)} lines to end of file'
            })
            print("✅ Patch queued for application")
            
        return True

    def _delete_block_menu(self) -> bool:
        """Delete code block"""
        try:
            start_line = int(self.get_input("Start line to delete"))
            end_line = int(self.get_input("End line to delete"))

            if (start_line < 1 or end_line > self.current_file_info['lines'] or 
                start_line > end_line):
                print("❌ Invalid line range")
                return True

            print(f"\nContent to delete (lines {start_line}-{end_line}):")
            self.tool.show_line_range(self.current_file_info, start_line, end_line)

            if self.get_input("Confirm deletion? (type 'DELETE' to confirm)") == 'DELETE':
                self.tool.patch_engine.applied_patches.append({
                    'type': 'delete_range',
                    'start_line': start_line,
                    'end_line': end_line,
                    'description': f'Delete lines {start_line}-{end_line}'
                })
                print("✅ Delete operation queued")
            else:
                print("❌ Deletion cancelled")
                
        except ValueError:
            print("❌ Invalid line numbers")
            
        return True

    def _show_patch_queue(self) -> bool:
        """Show current patch queue"""
        patches = self.tool.patch_engine.applied_patches
        
        if not patches:
            print("❌ No patches in queue")
            return True

        print(f"\n📋 PATCH QUEUE ({len(patches)} patches):")
        for i, patch in enumerate(patches, 1):
            print(f"  {i}. {patch['description']}")

            if 'code' in patch and patch['code']:
                code_preview = ' | '.join(patch['code'][:2])
                if len(patch['code']) > 2:
                    code_preview += f" ... (+{len(patch['code'])-2} lines)"
                print(f"      Code: {code_preview}")
                
        return True

    def _preview_changes(self) -> bool:
        """Preview changes before applying"""
        if not self.tool.patch_engine.applied_patches:
            print("❌ No patches to preview")
            return True
            
        if hasattr(self.tool, 'diff_engine'):
            # Get current file path from context
            file_path = self.current_file_info['relative_path']
            self.tool.diff_engine.interactive_diff_menu(
                file_path, self.tool.patch_engine.applied_patches
            )
        else:
            print("❌ Diff preview not available")
            
        return True

    def _apply_patches(self, file_path: str) -> bool:
        """Apply all queued patches"""
        patches = self.tool.patch_engine.applied_patches
        
        if not patches:
            print("❌ No patches to apply")
            return True

        print(f"\n📋 Patches to apply ({len(patches)}):")
        for i, patch in enumerate(patches, 1):
            print(f"  {i}. {patch['description']}")

        if self.tool.config_manager.get("confirm_applications", True):
            if not self.get_confirmation("Apply these patches?"):
                print("❌ Patch application cancelled")
                return True

        # Use the patch engine to apply patches
        success, result = self.tool.patch_engine.apply_patches(file_path, patches)
        
        if success:
            print(f"\n🎉 Successfully applied {result['successful_patches']}/{len(patches)} patches")
            print(f"📊 File changed: {result['original_lines']} → {result['new_lines']} lines")
            
            # Record in history if available
            if hasattr(self.tool, 'patch_history'):
                original_content = self.tool.file_manager.read_file_lines(file_path)
                if original_content:
                    self.tool.patch_history.record_operation(
                        file_path, patches, original_content, result
                    )
            
            # Show summary
            self._show_patch_summary(file_path)
            
            # Clear applied patches
            self.tool.patch_engine.applied_patches = []
            
            return False  # Exit patch menu after successful application
        else:
            print(f"❌ Patch application failed: {result.get('error', 'Unknown error')}")
            if 'failed_patches' in result:
                for failed in result['failed_patches']:
                    print(f"   - {failed['patch']['description']}: {failed['error']}")
                    
        return True

    def _show_patch_summary(self, file_path: str):
        """Show summary of applied patches"""
        file_info = self.tool.file_manager.get_file_info(file_path)
        if file_info:
            print(f"\n📄 Final file state: {file_info['lines']} lines")

            if file_info['lines'] > 0:
                print("\nFirst 5 lines:")
                self.tool.show_line_range(file_info, 1, min(5, file_info['lines']))

                if file_info['lines'] > 5:
                    print("\nLast 5 lines:")
                    self.tool.show_line_range(
                        file_info, 
                        max(1, file_info['lines']-4), 
                        file_info['lines']
                    )

    def _show_patch_settings(self) -> bool:
        """Show patch-specific settings"""
        settings_menu = SettingsMenu(self.tool)
        settings_menu.show_settings_menu()
        return True


class SettingsMenu(MenuSystem):
    """Settings menu system"""
    
    def show_settings_menu(self):
        """Display settings menu"""
        while True:
            options = [
                {'key': '1', 'label': f"Auto backup: {'ON' if self.tool.config_manager.get('auto_backup') else 'OFF'}"},
                {'key': '2', 'label': f"Confirm applications: {'ON' if self.tool.config_manager.get('confirm_applications') else 'OFF'}"},
                {'key': '3', 'label': f"Syntax hints: {'ON' if self.tool.config_manager.get('enable_syntax_hints') else 'OFF'}"},
                {'key': '4', 'label': f"Max preview lines: {self.tool.config_manager.get('max_preview_lines')}"},
                {'key': '5', 'label': f"Show hidden files: {'ON' if self.tool.config_manager.get('show_hidden_files') else 'OFF'}"},
                {'key': '6', 'label': f"Backup keep days: {self.tool.config_manager.get('backup_keep_days')}"},
                {'key': '7', 'label': "Reset to defaults"},
                {'key': '8', 'label': "Save and back"}
            ]
            
            choice = self.display_menu("⚙️ SETTINGS", options)
            
            if choice == '1':
                self._toggle_setting('auto_backup')
            elif choice == '2':
                self._toggle_setting('confirm_applications')
            elif choice == '3':
                self._toggle_setting('enable_syntax_hints')
            elif choice == '4':
                self._change_max_preview_lines()
            elif choice == '5':
                self._toggle_setting('show_hidden_files')
            elif choice == '6':
                self._change_backup_days()
            elif choice == '7':
                self._reset_to_defaults()
            elif choice == '8':
                self.tool.config_manager.save_config()
                break

    def _toggle_setting(self, setting_name: str):
        """Toggle a boolean setting"""
        current = self.tool.config_manager.get(setting_name)
        self.tool.config_manager.set(setting_name, not current)
        print(f"✅ {setting_name.replace('_', ' ').title()} set to {not current}")

    def _change_max_preview_lines(self):
        """Change max preview lines setting"""
        try:
            new_max = int(self.get_input("New max preview lines", 
                                       str(self.tool.config_manager.get('max_preview_lines'))))
            if 10 <= new_max <= 200:
                self.tool.config_manager.set('max_preview_lines', new_max)
                print(f"✅ Max preview lines set to {new_max}")
            else:
                print("❌ Must be between 10 and 200")
        except ValueError:
            print("❌ Invalid number")

    def _change_backup_days(self):
        """Change backup keep days setting"""
        try:
            new_days = int(self.get_input("Backup keep days", 
                                        str(self.tool.config_manager.get('backup_keep_days'))))
            if 1 <= new_days <= 365:
                self.tool.config_manager.set('backup_keep_days', new_days)
                print(f"✅ Backup keep days set to {new_days}")
            else:
                print("❌ Must be between 1 and 365")
        except ValueError:
            print("❌ Invalid number")

    def _reset_to_defaults(self):
        """Reset all settings to defaults"""
        if self.get_confirmation("Reset ALL settings to defaults?"):
            self.tool.config_manager.reset_to_defaults()
            print("✅ All settings reset to defaults")
