#!/usr/bin/env python3
"""
Navigation System for Professional Patch Tool
UNIX-style file navigation and directory listing
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path


class NavigationSystem:
    """Handles UNIX-style file navigation and directory operations"""
    
    def __init__(self, file_manager, config_manager):
        self.file_manager = file_manager
        self.config_manager = config_manager
        self.current_directory = os.path.expanduser('~')

    def list_directory(self, path: str = None) -> Dict[str, List[str]]:
        """List directory contents like ls command with enhanced info"""
        target_dir = path if path else self.current_directory
        target_dir = self.file_manager.resolve_path(target_dir)

        if not os.path.exists(target_dir):
            print(f"❌ Directory not found: {target_dir}")
            return {"directories": [], "files": []}

        try:
            items = os.listdir(target_dir)
        except PermissionError:
            print(f"❌ Permission denied: {target_dir}")
            return {"directories": [], "files": []}

        # Filter out hidden files if not enabled
        if not self.config_manager.get("show_hidden_files", False):
            items = [item for item in items if not item.startswith('.')]

        # Separate directories and files with enhanced info
        directories = []
        files = []

        for item in sorted(items):
            item_path = os.path.join(target_dir, item)
            if os.path.isdir(item_path):
                # Count items in directory
                try:
                    item_count = len(os.listdir(item_path))
                    directories.append(f"{item}/ ({item_count} items)")
                except:
                    directories.append(f"{item}/")
            else:
                # Get file size
                try:
                    size = os.path.getsize(item_path)
                    size_str = self._format_file_size(size)
                    files.append(f"{item} ({size_str})")
                except:
                    files.append(item)

        return {
            "directories": directories,
            "files": files,
            "path": target_dir
        }

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
            
        return f"{size_bytes:.1f} {size_names[i]}"

    def display_directory_listing(self, path: str = None):
        """Display formatted directory listing"""
        result = self.list_directory(path)
        
        if not result["directories"] and not result["files"]:
            return

        print(f"\n📁 {result['path']}/")
        print("=" * 60)

        if result["directories"]:
            print("\n📂 DIRECTORIES:")
            for dir_info in result["directories"]:
                print(f"  {dir_info}")

        if result["files"]:
            print("\n📄 FILES:")
            for file_info in result["files"]:
                print(f"  {file_info}")

    def navigate_to_file(self) -> Optional[str]:
        """UNIX-style file navigation with enhanced features"""
        print(f"\n🚀 PROFESSIONAL PATCH TOOL - FILE NAVIGATION")
        print(f"📁 Current: {self.current_directory}")
        print("\n💡 TIPS:")
        print("  • Enter path: 'api/main.py' or 'src/'")
        print("  • Commands: 'ls', 'cd <dir>', 'pwd', '~' for home, '..' for parent")
        print("  • Navigation: '../' to go up, '/' for root, '-' for previous directory")
        print("  • Type filename to select, 'q' to quit, 'h' for history")
        print("  • Press Enter to list current directory")
        print("=" * 60)

        previous_directory = self.current_directory

        while True:
            try:
                user_input = input(f"\n📁 {self.current_directory} $ ").strip()

                if not user_input:
                    self.display_directory_listing()
                    continue

                if user_input.lower() == 'q':
                    return None
                elif user_input.lower() == 'h':
                    self._show_navigation_history()
                    continue

                # Handle navigation commands
                result = self._handle_navigation_command(user_input, previous_directory)
                if result == "continue":
                    continue
                elif result == "break":
                    break
                elif isinstance(result, str):
                    return result

            except KeyboardInterrupt:
                print("\n❌ Navigation cancelled.")
                return None
            except Exception as e:
                print(f"❌ Error: {e}")

    def _handle_navigation_command(self, user_input: str, previous_directory: str) -> str:
        """Handle navigation commands and return appropriate action"""
        # Handle commands
        if user_input.lower() == 'ls':
            self.display_directory_listing()
            return "continue"
        elif user_input.lower() == 'pwd':
            print(f"📁 {self.current_directory}")
            return "continue"
        elif user_input.lower() == '~':
            self.current_directory = os.path.expanduser('~')
            print(f"📁 Moved to: {self.current_directory}")
            return "continue"
        elif user_input.lower() == '-':
            # Go back to previous directory
            temp = self.current_directory
            self.current_directory = previous_directory
            previous_directory = temp
            print(f"📁 Moved to previous: {self.current_directory}")
            return "continue"
        elif user_input.lower().startswith('cd '):
            new_dir = user_input[3:].strip()
            return self._handle_cd_command(new_dir, previous_directory)
        else:
            # Handle path navigation or file selection
            return self._handle_path_navigation(user_input)

    def _handle_cd_command(self, new_dir: str, previous_directory: str) -> str:
        """Handle cd command"""
        if not new_dir:
            self.current_directory = os.path.expanduser('~')
        elif new_dir == '-':
            # Swap with previous directory
            temp = self.current_directory
            self.current_directory = previous_directory
            previous_directory = temp
        else:
            new_dir = self.file_manager.resolve_path(new_dir)
            if os.path.isdir(new_dir):
                self.current_directory = new_dir
            else:
                print(f"❌ Directory not found: {new_dir}")
                return "continue"
        
        print(f"📁 Moved to: {self.current_directory}")
        return "continue"

    def _handle_path_navigation(self, user_input: str) -> str:
        """Handle path navigation and file selection"""
        target_path = self.file_manager.resolve_path(user_input)

        if os.path.isdir(target_path):
            # It's a directory - move there
            self.current_directory = target_path
            print(f"📁 Moved to: {self.current_directory}")
            self.display_directory_listing()
            return "continue"
        elif os.path.isfile(target_path):
            # It's a file - select it
            relative_path = self._get_relative_path(target_path)
            print(f"✅ Selected file: {relative_path}")
            return relative_path
        else:
            # Check if it's a relative path to a file that exists
            if self._is_likely_file_path(user_input):
                if os.path.exists(target_path):
                    relative_path = self._get_relative_path(target_path)
                    print(f"✅ Selected file: {relative_path}")
                    return relative_path
                else:
                    print(f"❌ File not found: {target_path}")
            else:
                # Check if it's a file in current directory
                current_file = os.path.join(self.current_directory, user_input)
                if os.path.isfile(current_file):
                    relative_path = self._get_relative_path(current_file)
                    print(f"✅ Selected file: {relative_path}")
                    return relative_path
                else:
                    print(f"❌ Not found: {user_input}")
            
            return "continue"

    def _get_relative_path(self, absolute_path: str) -> str:
        """Get relative path from base path"""
        try:
            return os.path.relpath(absolute_path, self.file_manager.base_path)
        except ValueError:
            return absolute_path

    def _is_likely_file_path(self, user_input: str) -> bool:
        """Check if input looks like a file path"""
        file_extensions = ['.py', '.zx', '.js', '.ts', '.java', '.cpp', '.c', 
                          '.html', '.css', '.md', '.json', '.xml', '.yaml', '.yml']
        
        return ('/' in user_input or 
                any(user_input.endswith(ext) for ext in file_extensions) or
                '.' in user_input.split('/')[-1])

    def _show_navigation_history(self):
        """Show navigation history"""
        history = self.file_manager.get_history()
        if history:
            print("\n📂 RECENT FILES:")
            for i, file_path in enumerate(history, 1):
                print(f"  {i}. {file_path}")
        else:
            print("No recent files in history")

    def find_files_by_pattern(self, pattern: str, search_dir: str = None) -> List[str]:
        """Find files matching pattern in directory"""
        search_dir = search_dir or self.current_directory
        search_dir = self.file_manager.resolve_path(search_dir)
        
        matching_files = []
        
        try:
            for root, dirs, files in os.walk(search_dir):
                # Filter hidden directories if not enabled
                if not self.config_manager.get("show_hidden_files", False):
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if pattern in file:
                        full_path = os.path.join(root, file)
                        relative_path = self._get_relative_path(full_path)
                        matching_files.append(relative_path)
        except Exception as e:
            print(f"❌ Error searching files: {e}")
        
        return matching_files
