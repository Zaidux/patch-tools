#!/usr/bin/env python3
"""
Professional Patch Tool for Ziver Chain
Interactive file patching with UNIX-style navigation
"""

import os
import sys
import re
import shutil
import json
from pathlib import Path
import datetime
from typing import List, Dict, Any, Optional

class ProfessionalPatchTool:
    def __init__(self):
        # Start from current working directory where tool was run
        self.current_directory = os.path.expanduser('~')
        self.base_path = self.current_directory
        self.applied_patches = []
        self.backup_dir = os.path.join(self.base_path, '.patch_backups')
        self.config_file = os.path.join(self.base_path, '.patch_config.json')

        # Load configuration
        self.config = self._load_config()

        # Create backup directory
        os.makedirs(self.backup_dir, exist_ok=True)

        # File history for quick access
        self.file_history = []
        self.max_history = 10
        
        # Compiled regex cache for performance
        self._regex_cache = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        default_config = {
            "auto_backup": True,
            "confirm_applications": True,
            "max_preview_lines": 50,
            "enable_syntax_hints": True,
            "backup_keep_days": 30,
            "show_hidden_files": False
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    # Validate config structure
                    for key in user_config:
                        if key in default_config:
                            default_config[key] = user_config[key]
            except Exception as e:
                print(f"⚠️  Config load error: {e}, using defaults")

        return default_config

    def _save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"⚠️  Config save error: {e}")

    def _resolve_path(self, path: str) -> str:
        """Resolve a path relative to current directory"""
        if path.startswith('/'):
            return path  # Absolute path
        elif path.startswith('~'):
            return os.path.expanduser(path)  # Home directory
        else:
            return os.path.join(self.current_directory, path)

    def _list_directory(self, path: str = None):
        """List directory contents like ls command"""
        target_dir = path if path else self.current_directory
        target_dir = self._resolve_path(target_dir)

        if not os.path.exists(target_dir):
            print(f"❌ Directory not found: {target_dir}")
            return

        try:
            items = os.listdir(target_dir)
        except PermissionError:
            print(f"❌ Permission denied: {target_dir}")
            return

        # Filter out hidden files if not enabled
        if not self.config["show_hidden_files"]:
            items = [item for item in items if not item.startswith('.')]

        # Separate directories and files
        directories = []
        files = []

        for item in sorted(items):
            item_path = os.path.join(target_dir, item)
            if os.path.isdir(item_path):
                directories.append(item)
            else:
                files.append(item)

        print(f"\n📁 {target_dir}/")
        print("=" * 60)

        if directories:
            print("\n📂 DIRECTORIES:")
            for dir_name in directories:
                print(f"  {dir_name}/")

        if files:
            print("\n📄 FILES:")
            for file_name in files:
                print(f"  {file_name}")

    def navigate_to_file(self) -> Optional[str]:
        """UNIX-style file navigation"""
        print(f"\n🚀 PROFESSIONAL PATCH TOOL - FILE NAVIGATION")
        print(f"📁 Current: {self.current_directory}")
        print("\n💡 TIPS:")
        print("  • Enter path: 'api/main.py' or 'src/'")
        print("  • Commands: 'ls', 'cd <dir>', 'pwd', '~' for home")
        print("  • Navigation: '../' to go up, '/' for root")
        print("  • Type filename to select, 'q' to quit")
        print("  • Press Enter to list current directory")
        print("=" * 60)

        while True:
            try:
                user_input = input(f"\n📁 {self.current_directory} $ ").strip()

                if not user_input:
                    self._list_directory()
                    continue

                if user_input.lower() == 'q':
                    return None

                # Handle commands
                if user_input.lower() == 'ls':
                    self._list_directory()
                    continue
                elif user_input.lower() == 'pwd':
                    print(f"📁 {self.current_directory}")
                    continue
                elif user_input.lower() == '~':
                    self.current_directory = os.path.expanduser('~')
                    print(f"📁 Moved to: {self.current_directory}")
                    continue
                elif user_input.lower().startswith('cd '):
                    new_dir = user_input[3:].strip()
                    if not new_dir:
                        self.current_directory = os.path.expanduser('~')
                    else:
                        new_dir = self._resolve_path(new_dir)
                        if os.path.isdir(new_dir):
                            self.current_directory = new_dir
                        else:
                            print(f"❌ Directory not found: {new_dir}")
                    print(f"📁 Moved to: {self.current_directory}")
                    continue

                # Handle path navigation
                target_path = self._resolve_path(user_input)

                if os.path.isdir(target_path):
                    # It's a directory - move there
                    self.current_directory = target_path
                    print(f"📁 Moved to: {self.current_directory}")
                    self._list_directory()
                elif os.path.isfile(target_path):
                    # It's a file - select it
                    # Calculate relative path from base for display
                    try:
                        relative_path = os.path.relpath(target_path, self.base_path)
                    except ValueError:
                        relative_path = target_path  # Use absolute if relative fails

                    print(f"✅ Selected file: {relative_path}")
                    return relative_path
                else:
                    # Check if it's a relative path to a file that exists
                    if '/' in user_input or user_input.endswith('.py') or user_input.endswith('.zx'):
                        # Assume it's a file path, check if it exists
                        if os.path.exists(target_path):
                            try:
                                relative_path = os.path.relpath(target_path, self.base_path)
                            except ValueError:
                                relative_path = target_path
                            print(f"✅ Selected file: {relative_path}")
                            return relative_path
                        else:
                            print(f"❌ File not found: {target_path}")
                    else:
                        # Check if it's a file in current directory
                        current_file = os.path.join(self.current_directory, user_input)
                        if os.path.isfile(current_file):
                            try:
                                relative_path = os.path.relpath(current_file, self.base_path)
                            except ValueError:
                                relative_path = current_file
                            print(f"✅ Selected file: {relative_path}")
                            return relative_path
                        else:
                            print(f"❌ Not found: {user_input}")

            except KeyboardInterrupt:
                print("\n❌ Navigation cancelled.")
                return None
            except Exception as e:
                print(f"❌ Error: {e}")

    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a file"""
        file_abs_path = os.path.join(self.base_path, file_path)

        if not os.path.exists(file_abs_path):
            return None

        try:
            with open(file_abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            stat = os.stat(file_abs_path)
            return {
                'exists': True,
                'path': file_abs_path,
                'relative_path': file_path,
                'size': stat.st_size,
                'lines': len(lines),
                'extension': os.path.splitext(file_abs_path)[1].lower(),
                'content': content,
                'line_list': lines,
                'modified': datetime.datetime.fromtimestamp(stat.st_mtime),
                'language': self._detect_language(file_abs_path)
            }
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext_map = {
            '.py': 'python',
            '.zx': 'zexus',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
            '.c': 'c',
            '.h': 'c', '.hpp': 'cpp',
            '.html': 'html',
            '.css': 'css',
            '.md': 'markdown',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml', '.yml': 'yaml'
        }
        return ext_map.get(os.path.splitext(file_path)[1].lower(), 'text')

    def display_file_preview(self, file_info: Dict[str, Any], start_line: int = 1, num_lines: int = 20):
        """Display a preview of the file with syntax hints"""
        print(f"\n📄 File: {file_info['relative_path']}")
        print(f"📊 Size: {file_info['size']} bytes, Lines: {file_info['lines']}, Language: {file_info['language']}")
        print(f"🕒 Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        print("─" * 80)

        end_line = min(start_line + num_lines - 1, file_info['lines'])

        for i in range(start_line - 1, end_line):
            if i < len(file_info['line_list']):
                line_num = i + 1
                line_content = file_info['line_list'][i]

                # Basic syntax highlighting
                if self.config["enable_syntax_hints"]:
                    line_content = self._highlight_syntax(line_content, file_info['language'])

                print(f"{line_num:4d} │ {line_content}")

        print("─" * 80)
        if end_line < file_info['lines']:
            print(f"... and {file_info['lines'] - end_line} more lines")

    def _highlight_syntax(self, line: str, language: str) -> str:
        """Basic syntax highlighting (ANSI colors)"""
        if language == 'python':
            # Python keywords
            keywords = ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'return', 'import', 'from', 'as']
            for kw in keywords:
                if re.match(rf'^\s*{kw}\b', line):
                    return f"\033[95m{line}\033[0m"  # Magenta
            # Strings
            if '"' in line or "'" in line:
                return f"\033[92m{line}\033[0m"  # Green
        elif language == 'zexus':
            # Zexus keywords
            keywords = ['action', 'entity', 'contract', 'export', 'use', 'let', 'if', 'else', 'for', 'while']
            for kw in keywords:
                if re.match(rf'^\s*{kw}\b', line):
                    return f"\033[95m{line}\033[0m"
        return line

    def create_backup(self, file_path: str) -> str:
        """Create a backup of the file"""
        file_abs_path = os.path.join(self.base_path, file_path)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Safe backup name encoding
        safe_path = file_path.replace('/', '__').replace('\\', '__')
        backup_name = f"{safe_path}.{timestamp}.bak"
        backup_path = os.path.join(self.backup_dir, backup_name)

        try:
            shutil.copy2(file_abs_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return ""

    def show_line_range(self, file_info: Dict[str, Any], start_line: int, end_line: int):
        """Show specific line range with context"""
        print(f"\n🔍 Lines {start_line}-{end_line}:")
        print("─" * 80)

        for i in range(start_line - 1, min(end_line, len(file_info['line_list']))):
            line_num = i + 1
            line_content = file_info['line_list'][i]

            if self.config["enable_syntax_hints"]:
                line_content = self._highlight_syntax(line_content, file_info['language'])

            print(f"{line_num:4d} │ {line_content}")
        print("─" * 80)

    def _get_compiled_regex(self, pattern: str) -> Optional[re.Pattern]:
        """Get compiled regex from cache or compile new one"""
        if pattern in self._regex_cache:
            return self._regex_cache[pattern]
        
        try:
            compiled = re.compile(pattern)
            self._regex_cache[pattern] = compiled
            return compiled
        except re.error as e:
            print(f"❌ Invalid regex pattern: {e}")
            return None

    def find_code_block(self, file_info: Dict[str, Any], search_pattern: str, context_lines: int = 3) -> List[Dict[str, Any]]:
        """Find code blocks matching pattern with context"""
        matches = []
        regex = self._get_compiled_regex(search_pattern)
        if not regex:
            return []

        for i, line in enumerate(file_info['line_list']):
            if regex.search(line):
                start = max(0, i - context_lines)
                end = min(len(file_info['line_list']), i + context_lines + 1)
                matches.append({
                    'line_number': i + 1,
                    'context_start': start + 1,
                    'context_end': end,
                    'context': file_info['line_list'][start:end],
                    'match_index': len(matches) + 1,
                    'full_match': line
                })
        return matches

    def patch_file_interactive(self, file_path: str) -> bool:
        """Interactive file patching with full user control"""
        file_info = self.get_file_info(file_path)

        if not file_info:
            print(f"❌ File not found: {file_path}")
            return False

        # Add to history
        if file_path not in self.file_history:
            self.file_history.insert(0, file_path)
            self.file_history = self.file_history[:self.max_history]

        print(f"\n🎯 Patching: {file_path}")
        print(f"📊 File Info: {file_info['lines']} lines, {file_info['size']} bytes, {file_info['language']}")

        while True:
            print("\n" + "="*60)
            print("🔧 PATCH MENU")
            print("="*60)
            print("1. 📋 Show file preview")
            print("2. 🔍 Search for code pattern")
            print("3. 📍 Insert code at specific line")
            print("4. 🔄 Replace code block")
            print("5. ➕ Insert after pattern")
            print("6. ➖ Insert before pattern")
            print("7. 📤 Append to end of file")
            print("8. 🗑️  Delete code block")
            print("9. 📋 Show patch queue")
            print("10. 💾 Apply patches and save")
            print("11. ⚙️  Settings")
            print("0. ❌ Cancel and exit")
            print("="*60)

            try:
                choice = input("\nSelect option (0-11): ").strip()

                if choice == '1':
                    self._show_preview_menu(file_info)
                elif choice == '2':
                    self._search_pattern_menu(file_info)
                elif choice == '3':
                    self._insert_at_line_menu(file_info)
                elif choice == '4':
                    self._replace_block_menu(file_info)
                elif choice == '5':
                    self._insert_after_menu(file_info)
                elif choice == '6':
                    self._insert_before_menu(file_info)
                elif choice == '7':
                    self._append_menu(file_info)
                elif choice == '8':
                    self._delete_block_menu(file_info)
                elif choice == '9':
                    self._show_patch_queue()
                elif choice == '10':
                    return self._apply_patches(file_path, file_info)
                elif choice == '11':
                    self._settings_menu()
                elif choice == '0':
                    print("❌ Operation cancelled.")
                    return False
                else:
                    print("❌ Invalid choice. Please try again.")
            except KeyboardInterrupt:
                print("\n⏹️  Operation cancelled.")
                continue
            except Exception as e:
                print(f"❌ Error in menu: {e}")

    def _show_preview_menu(self, file_info: Dict[str, Any]):
        """Show file preview with navigation"""
        start_line = 1
        while True:
            self.display_file_preview(file_info, start_line)
            print("\nNavigation: [n]ext, [p]revious, [g]oto line, [s]pecific range, [b]ack")
            try:
                nav = input("Choose: ").strip().lower()

                if nav == 'n':
                    start_line = min(start_line + 20, file_info['lines'] - 19)
                elif nav == 'p':
                    start_line = max(1, start_line - 20)
                elif nav == 'g':
                    try:
                        line_num = int(input("Go to line: "))
                        start_line = max(1, min(line_num, file_info['lines'] - 19))
                    except ValueError:
                        print("❌ Invalid line number")
                elif nav == 's':
                    try:
                        start = int(input("Start line: "))
                        end = int(input("End line: "))
                        self.show_line_range(file_info, start, end)
                    except ValueError:
                        print("❌ Invalid line numbers")
                elif nav == 'b':
                    break
                else:
                    print("❌ Invalid option")
            except KeyboardInterrupt:
                print("\n⏹️  Navigation cancelled.")
                break

    def _search_pattern_menu(self, file_info: Dict[str, Any]):
        """Search for code patterns with enhanced options"""
        pattern = input("\nEnter search pattern (regex): ").strip()
        if not pattern:
            return

        print("Search options: [1] Normal, [2] Case-sensitive, [3] Whole word")
        option = input("Choose option [1]: ").strip() or "1"

        if option == "2":
            pattern = f"(?i){pattern}"  # Case insensitive
        elif option == "3":
            pattern = r"\b" + pattern + r"\b"  # Whole word

        matches = self.find_code_block(file_info, pattern)

        if not matches:
            print("❌ No matches found.")
            return

        print(f"\n🔍 Found {len(matches)} matches:")
        for i, match in enumerate(matches):
            print(f"\n[{i+1}] Line {match['line_number']}:")
            print(f"    Match: {match['full_match'][:100]}{'...' if len(match['full_match']) > 100 else ''}")

            if input("Show context? (y/n): ").lower() == 'y':
                self.show_line_range(file_info, match['context_start'], match['context_end'])

    def _insert_at_line_menu(self, file_info: Dict[str, Any]):
        """Insert code at specific line"""
        try:
            line_num = int(input("\nEnter line number to insert at: "))
            if line_num < 1 or line_num > file_info['lines'] + 1:
                print("❌ Invalid line number")
                return

            print(f"\nCurrent content at line {line_num}:")
            if line_num <= file_info['lines']:
                current_line = file_info['line_list'][line_num-1]
                if self.config["enable_syntax_hints"]:
                    current_line = self._highlight_syntax(current_line, file_info['language'])
                print(f"{line_num:4d} │ {current_line}")
            else:
                print("(end of file)")

            print("\nEnter code to insert:")
            new_code = self._get_multiline_input()

            if new_code:
                self._add_patch({
                    'type': 'insert_at_line',
                    'line_number': line_num,
                    'code': new_code,
                    'description': f'Insert {len(new_code)} lines at line {line_num}'
                })
                print("✅ Patch queued for application")
        except ValueError:
            print("❌ Invalid line number")

    def _replace_block_menu(self, file_info: Dict[str, Any]):
        """Replace a code block with enhanced options"""
        print("\n🔄 Replace Code Block")
        print("1. Replace by line range")
        print("2. Replace by pattern match")
        print("3. Replace all pattern matches")

        choice = input("Choose method (1-3): ").strip()

        if choice == '1':
            self._replace_by_line_range(file_info)
        elif choice == '2':
            self._replace_by_pattern(file_info, single_match=True)
        elif choice == '3':
            self._replace_by_pattern(file_info, single_match=False)
        else:
            print("❌ Invalid choice")

    def _replace_by_line_range(self, file_info: Dict[str, Any]):
        """Replace code by line range"""
        try:
            start_line = int(input("Start line: "))
            end_line = int(input("End line: "))

            if start_line < 1 or end_line > file_info['lines'] or start_line > end_line:
                print("❌ Invalid line range")
                return

            print(f"\nCurrent content (lines {start_line}-{end_line}):")
            self.show_line_range(file_info, start_line, end_line)

            print("\nEnter replacement code:")
            new_code = self._get_multiline_input()

            if new_code:
                self._add_patch({
                    'type': 'replace_range',
                    'start_line': start_line,
                    'end_line': end_line,
                    'code': new_code,
                    'description': f'Replace lines {start_line}-{end_line} with {len(new_code)} lines'
                })
                print("✅ Patch queued for application")

        except ValueError:
            print("❌ Invalid line numbers")

    def _replace_by_pattern(self, file_info: Dict[str, Any], single_match: bool = True):
        """Replace code by pattern matching"""
        pattern = input("Enter pattern to replace (regex): ").strip()
        if not pattern:
            return

        matches = self.find_code_block(file_info, pattern, context_lines=2)
        if not matches:
            print("❌ No matches found")
            return

        if single_match:
            # Replace first match only
            match = matches[0]
            print(f"\nFound match at line {match['line_number']}:")
            self.show_line_range(file_info, match['context_start'], match['context_end'])

            print("\nEnter replacement code:")
            new_code = self._get_multiline_input()

            if new_code:
                self._add_patch({
                    'type': 'replace_pattern',
                    'pattern': pattern,
                    'code': new_code,
                    'description': f'Replace pattern at line {match["line_number"]}',
                    'match_line': match['line_number']
                })
                print("✅ Patch queued for application")
        else:
            # Replace all matches - FIXED THE INCOMPLETE LOOP
            print(f"\nFound {len(matches)} matches. Replace all?")
            if input("Confirm (y/n): ").lower() == 'y':
                print("\nEnter replacement code (will be applied to all matches):")
                new_code = self._get_multiline_input()

                if new_code:
                    for match in matches:
                        self._add_patch({
                            'type': 'replace_pattern_all',
                            'pattern': pattern,
                            'code': new_code,
                            'description': f'Replace pattern at line {match["line_number"]}',
                            'match_line': match['line_number']
                        })
                    print(f"✅ Queued replacement for {len(matches)} matches")

    def _insert_after_menu(self, file_info: Dict[str, Any]):
        """Insert code after pattern"""
        pattern = input("\nEnter pattern to insert after (regex): ").strip()
        if not pattern:
            return

        matches = self.find_code_block(file_info, pattern)
        if not matches:
            print("❌ Pattern not found")
            return

        print(f"\nFound {len(matches)} matches. Will insert after first match at line {matches[0]['line_number']}")
        self.show_line_range(file_info, matches[0]['line_number']-1, matches[0]['line_number']+1)

        print("\nEnter code to insert:")
        new_code = self._get_multiline_input()

        if new_code:
            self._add_patch({
                'type': 'insert_after',
                'after': pattern,
                'code': new_code,
                'description': f'Insert {len(new_code)} lines after pattern at line {matches[0]["line_number"]}'
            })
            print("✅ Patch queued for application")

    def _insert_before_menu(self, file_info: Dict[str, Any]):
        """Insert code before pattern"""
        pattern = input("\nEnter pattern to insert before (regex): ").strip()
        if not pattern:
            return

        matches = self.find_code_block(file_info, pattern)
        if not matches:
            print("❌ Pattern not found")
            return

        print(f"\nFound {len(matches)} matches. Will insert before first match at line {matches[0]['line_number']}")
        self.show_line_range(file_info, matches[0]['line_number']-1, matches[0]['line_number']+1)

        print("\nEnter code to insert:")
        new_code = self._get_multiline_input()

        if new_code:
            self._add_patch({
                'type': 'insert_before',
                'before': pattern,
                'code': new_code,
                'description': f'Insert {len(new_code)} lines before pattern at line {matches[0]["line_number"]}'
            })
            print("✅ Patch queued for application")

    def _append_menu(self, file_info: Dict[str, Any]):
        """Append code to end of file"""
        print(f"\nAppending to end of file (currently {file_info['lines']} lines)")
        print("Last 5 lines:")
        self.show_line_range(file_info, max(1, file_info['lines']-4), file_info['lines'])

        print("\nEnter code to append:")
        new_code = self._get_multiline_input()

        if new_code:
            self._add_patch({
                'type': 'append',
                'code': new_code,
                'description': f'Append {len(new_code)} lines to end of file'
            })
            print("✅ Patch queued for application")

    def _delete_block_menu(self, file_info: Dict[str, Any]):
        """Delete a code block"""
        try:
            start_line = int(input("Start line to delete: "))
            end_line = int(input("End line to delete: "))

            if start_line < 1 or end_line > file_info['lines'] or start_line > end_line:
                print("❌ Invalid line range")
                return

            print(f"\nContent to delete (lines {start_line}-{end_line}):")
            self.show_line_range(file_info, start_line, end_line)

            confirm = input("\n❌ Confirm deletion? (type 'DELETE' to confirm): ")
            if confirm == 'DELETE':
                self._add_patch({
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

    def _get_multiline_input(self) -> List[str]:
        """Get multiline input from user with multiple options"""
        print("\nEnter code:")
        print("Options: [t]ype, [f]ile, [e]nd marker")
        
        while True:
            method = input("Choose input method (t/f/e): ").strip().lower()
            if method in ['t', 'f', 'e']:
                break
            elif method == '':
                method = 't'  # Default to type if empty
                break
            else:
                print("❌ Invalid choice. Please enter 't', 'f', or 'e'")
    
        if method == 'f':  # Load from file
            file_path = input("Enter file path: ").strip()
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().split('\n')
                    print(f"✅ Loaded {len(content)} lines from {file_path}")
                    return [line.rstrip('\r') for line in content if line.strip() != '']
                except Exception as e:
                    print(f"❌ Error reading file: {e}")
            return []
        
        elif method == 'e':  # End marker
            end_marker = input("Enter end marker [END]: ").strip() or "END"
            print(f"Enter code (type '{end_marker}' on a new line to finish):")
            print(">" * 40)
            lines = []
            while True:
                try:
                    line = input()
                    if line.strip() == end_marker:
                        break
                    lines.append(line)
                except EOFError:
                    break
            print("<" * 40)
            return lines
        
        else:  # Default: type input
            print("Enter code (empty line to finish):")
            print(">" * 40)
            lines = []
            while True:
                try:
                    line = input()
                    if line == "":
                        break
                    lines.append(line)
                except EOFError:
                    break
            print("<" * 40)
            return lines

    def _add_patch(self, patch: Dict[str, Any]):
        """Add a patch to the queue"""
        self.applied_patches.append(patch)

    def _show_patch_queue(self):
        """Show current patch queue"""
        if not self.applied_patches:
            print("❌ No patches in queue")
            return

        print(f"\n📋 PATCH QUEUE ({len(self.applied_patches)} patches):")
        for i, patch in enumerate(self.applied_patches):
            print(f"  {i+1}. {patch['description']}")

            # Show patch details
            if 'code' in patch and patch['code']:
                code_preview = ' | '.join(patch['code'][:2])
                if len(patch['code']) > 2:
                    code_preview += f" ... (+{len(patch['code'])-2} lines)"
                print(f"      Code: {code_preview}")

    def _apply_patches(self, file_path: str, file_info: Dict[str, Any]) -> bool:
        """Apply all queued patches"""
        if not self.applied_patches:
            print("❌ No patches to apply")
            return False

        print(f"\n📋 Patches to apply ({len(self.applied_patches)}):")
        for i, patch in enumerate(self.applied_patches):
            print(f"  {i+1}. {patch['description']}")

        if self.config["confirm_applications"]:
            confirm = input("\n✅ Apply these patches? (y/n): ").lower()
            if confirm != 'y':
                print("❌ Patch application cancelled")
                return False

        # Create backup
        backup_path = ""
        if self.config["auto_backup"]:
            backup_path = self.create_backup(file_path)
            if backup_path:
                print(f"💾 Backup created: {backup_path}")
            else:
                print("⚠️  Backup creation failed, continuing without backup")

        # Apply patches
        file_abs_path = os.path.join(self.base_path, file_path)
        try:
            with open(file_abs_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False

        original_line_count = len(lines)
        successful_patches = 0

        # Sort patches to apply from bottom to top (avoid line number issues)
        sorted_patches = sorted(self.applied_patches,
                              key=lambda x: x.get('line_number', x.get('start_line', 0)),
                              reverse=True)

        for patch in sorted_patches:
            try:
                if self._apply_single_patch(lines, patch):
                    successful_patches += 1
            except Exception as e:
                print(f"❌ Error applying patch '{patch['description']}': {e}")

        if successful_patches > 0:
            try:
                with open(file_abs_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)

                print(f"\n🎉 Successfully applied {successful_patches}/{len(self.applied_patches)} patches")
                print(f"📊 File changed: {original_line_count} → {len(lines)} lines")

                # Save patch queue for persistence
                self._save_patch_queue(file_path)
                
                # Show summary of changes
                self._show_patch_summary(file_path)
                return True
            except Exception as e:
                print(f"❌ Error writing file: {e}")
                # Restore from backup if available
                if backup_path and os.path.exists(backup_path):
                    shutil.copy2(backup_path, file_abs_path)
                    print("🔄 Restored original file from backup")
                return False
        else:
            print("❌ No patches were successfully applied")
            return False

    def _apply_single_patch(self, lines: List[str], patch: Dict[str, Any]) -> bool:
        """Apply a single patch to lines array"""
        patch_type = patch['type']

        try:
            if patch_type == 'insert_at_line':
                return self._patch_insert_at_line(lines, patch['line_number'], patch['code'])
            elif patch_type == 'replace_range':
                return self._patch_replace_range(lines, patch['start_line'], patch['end_line'], patch['code'])
            elif patch_type == 'replace_pattern':
                return self._patch_replace_pattern(lines, patch['pattern'], patch['code'], patch.get('match_line'))
            elif patch_type == 'replace_pattern_all':
                return self._patch_replace_pattern_all(lines, patch['pattern'], patch['code'])
            elif patch_type == 'insert_after':
                return self._patch_insert_after(lines, patch['after'], patch['code'])
            elif patch_type == 'insert_before':
                return self._patch_insert_before(lines, patch['before'], patch['code'])
            elif patch_type == 'append':
                return self._patch_append(lines, patch['code'])
            elif patch_type == 'delete_range':
                return self._patch_delete_range(lines, patch['start_line'], patch['end_line'])
            else:
                print(f"❌ Unknown patch type: {patch_type}")
                return False
        except Exception as e:
            print(f"❌ Error applying patch '{patch['description']}': {e}")
            return False

    def _patch_insert_at_line(self, lines: List[str], line_number: int, new_code: List[str]) -> bool:
        """Insert code at specific line - FIXED to handle empty lines properly"""
        insert_pos = line_number - 1
        # Ensure we don't go beyond the end of the file
        if insert_pos > len(lines):
            insert_pos = len(lines)
            
        for i, line in enumerate(new_code):
            # Add proper newline for each inserted line
            lines.insert(insert_pos + i, line + '\n')
        print(f"   ✅ Inserted {len(new_code)} lines at line {line_number}")
        return True

    def _patch_replace_range(self, lines: List[str], start_line: int, end_line: int, new_code: List[str]) -> bool:
        """Replace a range of lines"""
        # Remove old lines
        del lines[start_line-1:end_line]

        # Insert new lines with proper newlines
        for i, line in enumerate(new_code):
            lines.insert(start_line-1 + i, line + '\n')

        print(f"   ✅ Replaced lines {start_line}-{end_line} with {len(new_code)} lines")
        return True

    def _patch_replace_pattern(self, lines: List[str], pattern: str, new_code: List[str], match_line: int = None) -> bool:
        """Replace lines matching pattern at specific line"""
        regex = self._get_compiled_regex(pattern)
        if not regex:
            return False

        if match_line:
            # Replace at specific line
            line_idx = match_line - 1
            if 0 <= line_idx < len(lines) and regex.search(lines[line_idx]):
                # Replace single line with potentially multiple lines
                del lines[line_idx]
                for j, new_line in enumerate(new_code):
                    lines.insert(line_idx + j, new_line + '\n')
                print(f"   ✅ Replaced pattern at line {match_line}")
                return True
        else:
            # Find and replace first occurrence
            for i, line in enumerate(lines):
                if regex.search(line):
                    # Replace single line with potentially multiple lines
                    del lines[i]
                    for j, new_line in enumerate(new_code):
                        lines.insert(i + j, new_line + '\n')
                    print(f"   ✅ Replaced pattern at line {i+1}")
                    return True
        
        print(f"   ❌ Pattern not found: {pattern}")
        return False

    def _patch_replace_pattern_all(self, lines: List[str], pattern: str, new_code: List[str]) -> bool:
        """Replace all occurrences of pattern - COMPLETED IMPLEMENTATION"""
        regex = self._get_compiled_regex(pattern)
        if not regex:
            return False

        replacements = 0
        i = 0
        while i < len(lines):
            if regex.search(lines[i]):
                # Replace this occurrence
                del lines[i]
                for j, new_line in enumerate(new_code):
                    lines.insert(i + j, new_line + '\n')
                replacements += 1
                i += len(new_code)  # Skip the newly inserted lines
            else:
                i += 1

        if replacements > 0:
            print(f"   ✅ Replaced pattern at {replacements} locations")
            return True
        else:
            print(f"   ❌ Pattern not found: {pattern}")
            return False

    def _patch_insert_after(self, lines: List[str], pattern: str, new_code: List[str]) -> bool:
        """Insert code after pattern"""
        regex = self._get_compiled_regex(pattern)
        if not regex:
            return False

        for i, line in enumerate(lines):
            if regex.search(line):
                insert_pos = i + 1
                for j, new_line in enumerate(new_code):
                    lines.insert(insert_pos + j, new_line + '\n')
                print(f"   ✅ Inserted after pattern at line {i+1}")
                return True
        print(f"   ❌ Pattern not found: {pattern}")
        return False

    def _patch_insert_before(self, lines: List[str], pattern: str, new_code: List[str]) -> bool:
        """Insert code before pattern"""
        regex = self._get_compiled_regex(pattern)
        if not regex:
            return False

        for i, line in enumerate(lines):
            if regex.search(line):
                for j, new_line in enumerate(new_code):
                    lines.insert(i + j, new_line + '\n')
                print(f"   ✅ Inserted before pattern at line {i+1}")
                return True
        print(f"   ❌ Pattern not found: {pattern}")
        return False

    def _patch_append(self, lines: List[str], new_code: List[str]) -> bool:
        """Append code to end of file"""
        for line in new_code:
            lines.append(line + '\n')
        print(f"   ✅ Appended {len(new_code)} lines to end of file")
        return True

    def _patch_delete_range(self, lines: List[str], start_line: int, end_line: int) -> bool:
        """Delete a range of lines"""
        del lines[start_line-1:end_line]
        print(f"   ✅ Deleted lines {start_line}-{end_line}")
        return True

    def _show_patch_summary(self, file_path: str):
        """Show summary of applied patches"""
        file_info = self.get_file_info(file_path)
        if file_info:
            print(f"\n📄 Final file state: {file_info['lines']} lines")

            # Show first and last few lines
            if file_info['lines'] > 0:
                print("\nFirst 5 lines:")
                self.show_line_range(file_info, 1, min(5, file_info['lines']))

                if file_info['lines'] > 5:
                    print("\nLast 5 lines:")
                    self.show_line_range(file_info, max(1, file_info['lines']-4), file_info['lines'])

    def _save_patch_queue(self, file_path: str):
        """Save patch queue to file for persistence"""
        queue_file = os.path.join(self.base_path, '.patch_queue.json')
        try:
            queue_data = {
                'file_path': file_path,
                'patches': self.applied_patches,
                'timestamp': datetime.datetime.now().isoformat()
            }
            with open(queue_file, 'w') as f:
                json.dump(queue_data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save patch queue: {e}")

    def _settings_menu(self):
        """Configuration settings menu"""
        while True:
            print(f"\n⚙️  SETTINGS")
            print(f"1. Auto backup: {'ON' if self.config['auto_backup'] else 'OFF'}")
            print(f"2. Confirm applications: {'ON' if self.config['confirm_applications'] else 'OFF'}")
            print(f"3. Syntax hints: {'ON' if self.config['enable_syntax_hints'] else 'OFF'}")
            print(f"4. Max preview lines: {self.config['max_preview_lines']}")
            print(f"5. Show hidden files: {'ON' if self.config['show_hidden_files'] else 'OFF'}")
            print("6. Save and back")

            try:
                choice = input("\nToggle setting (1-6): ").strip()

                if choice == '1':
                    self.config["auto_backup"] = not self.config["auto_backup"]
                elif choice == '2':
                    self.config["confirm_applications"] = not self.config["confirm_applications"]
                elif choice == '3':
                    self.config["enable_syntax_hints"] = not self.config["enable_syntax_hints"]
                elif choice == '4':
                    try:
                        new_max = int(input("New max preview lines: "))
                        if 10 <= new_max <= 100:
                            self.config["max_preview_lines"] = new_max
                        else:
                            print("❌ Must be between 10 and 100")
                    except ValueError:
                        print("❌ Invalid number")
                elif choice == '5':
                    self.config["show_hidden_files"] = not self.config["show_hidden_files"]
                elif choice == '6':
                    self._save_config()
                    break
                else:
                    print("❌ Invalid choice")
            except KeyboardInterrupt:
                print("\n⏹️  Settings cancelled.")
                break

    def restore_backup(self, file_path: str) -> bool:
        """Restore from the most recent backup"""
        safe_path = file_path.replace('/', '__').replace('\\', '__')
        backup_pattern = f"{safe_path}.*.bak"

        backups = list(Path(self.backup_dir).glob(backup_pattern))
        if not backups:
            print(f"❌ No backups found for {file_path}")
            return False

        # Get most recent backup
        latest_backup = max(backups, key=lambda x: x.stat().st_mtime)

        print(f"🔙 Restoring from backup: {latest_backup.name}")
        print(f"📅 Backup date: {datetime.datetime.fromtimestamp(latest_backup.stat().st_mtime)}")

        file_abs_path = os.path.join(self.base_path, file_path)
        try:
            shutil.copy2(latest_backup, file_abs_path)
            print(f"✅ Successfully restored {file_path}")
            return True
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False

    def cleanup_old_backups(self, days: int = 30):
        """Clean up backups older than specified days"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=days)
        deleted_count = 0

        for backup_file in Path(self.backup_dir).glob('*.bak'):
            if backup_file.stat().st_mtime < cutoff_time.timestamp():
                try:
                    backup_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"⚠️  Could not delete {backup_file}: {e}")

        print(f"🧹 Cleaned up {deleted_count} backups older than {days} days")

def main():
    """Main interactive interface"""
    tool = ProfessionalPatchTool()
    
    print("🚀 PROFESSIONAL PATCH TOOL")
    print("="*60)
    print(f"📁 Started in: {tool.current_directory}")
    
    try:
        while True:
            print("\n📁 MAIN MENU")
            print("1. 📝 Navigate & patch file (UNIX-style)")
            print("2. 📝 Enter file path directly")
            print("3. 🔄 Restore from backup")
            print("4. 📂 File history")
            print("5. 🛠️ Predefined fixes")
            print("6. ⚙️ Settings")
            print("7. 🧹 Cleanup old backups")
            print("8. ❌ Exit")
            
            try:
                choice = input("\nSelect option (1-8): ").strip()
                
                if choice == '1':
                    # UNIX-style navigation
                    file_path = tool.navigate_to_file()
                    if file_path:
                        tool.patch_file_interactive(file_path)
                        tool.applied_patches = []  # Reset for next operation
                
                elif choice == '2':
                    # Direct file path entry
                    file_path = input("Enter file path (absolute or relative): ").strip()
                    if file_path:
                        # Convert to absolute path
                        abs_path = tool._resolve_path(file_path)
                        if os.path.isfile(abs_path):
                            # Get relative path from base for display
                            try:
                                relative_path = os.path.relpath(abs_path, tool.base_path)
                            except ValueError:
                                relative_path = abs_path
                            print(f"✅ Selected file: {relative_path}")
                            tool.patch_file_interactive(relative_path)
                            tool.applied_patches = []
                        else:
                            print(f"❌ File not found: {abs_path}")
                    else:
                        print("❌ No file path provided")
                
                elif choice == '3':
                    file_path = input("Enter file path to restore: ").strip()
                    if file_path:
                        tool.restore_backup(file_path)
                
                elif choice == '4':
                    print("\n📂 RECENT FILES:")
                    if tool.file_history:
                        for i, file_path in enumerate(tool.file_history, 1):
                            print(f"{i}. {file_path}")
                        
                        selection = input("\nSelect file number or [c]ancel: ").strip()
                        if selection.isdigit():
                            idx = int(selection) - 1
                            if 0 <= idx < len(tool.file_history):
                                tool.patch_file_interactive(tool.file_history[idx])
                    else:
                        print("No recent files")
                
                elif choice == '5':
                    apply_predefined_fixes(tool)
                
                elif choice == '6':
                    tool._settings_menu()
                
                elif choice == '7':
                    try:
                        days = int(input("Delete backups older than (days) [30]: ") or "30")
                        tool.cleanup_old_backups(days)
                    except ValueError:
                        print("❌ Invalid number")
                
                elif choice == '8':
                    print("👋 Goodbye!")
                    break
                
                else:
                    print("❌ Invalid choice")
                    
            except KeyboardInterrupt:
                print("\n⏹️  Operation cancelled.")
                continue
                
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")

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
