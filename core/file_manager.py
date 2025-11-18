#!/usr/bin/env python3
"""
File Manager for Professional Patch Tool
Handles file operations, backups, and file history
"""

import os
import shutil
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import hashlib


class FileManager:
    """Manages file operations, backups, and file history"""
    
    def __init__(self, base_path: str, config_manager):
        self.base_path = base_path
        self.config_manager = config_manager
        self.backup_dir = os.path.join(base_path, '.patch_backups')
        self.file_history = []
        self.max_history = 10
        
        # Create backup directory
        os.makedirs(self.backup_dir, exist_ok=True)

    def resolve_path(self, path: str) -> str:
        """Resolve a path relative to current directory"""
        if path.startswith('/'):
            return path  # Absolute path
        elif path.startswith('~'):
            return os.path.expanduser(path)  # Home directory
        else:
            return os.path.join(self.base_path, path)

    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a file"""
        file_abs_path = self.resolve_path(file_path)

        if not os.path.exists(file_abs_path):
            return None

        try:
            with open(file_abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            stat = os.stat(file_abs_path)
            
            # Calculate file hash for change detection
            file_hash = self._calculate_file_hash(file_abs_path)
            
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
                'created': datetime.datetime.fromtimestamp(stat.st_ctime),
                'language': self._detect_language(file_abs_path),
                'hash': file_hash,
                'encoding': 'utf-8'  # Could be enhanced to detect encoding
            }
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext_map = {
            '.py': 'python',
            '.zx': 'zexus',
            '.js': 'javascript', '.jsx': 'javascript',
            '.ts': 'typescript', '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp', '.hpp': 'cpp',
            '.c': 'c', '.h': 'c',
            '.html': 'html', '.htm': 'html',
            '.css': 'css', '.scss': 'css', '.less': 'css',
            '.md': 'markdown', '.markdown': 'markdown',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml', '.yml': 'yaml',
            '.sql': 'sql',
            '.sh': 'bash', '.bash': 'bash',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust'
        }
        return ext_map.get(os.path.splitext(file_path)[1].lower(), 'text')

    def create_backup(self, file_path: str) -> Tuple[bool, str]:
        """Create a backup of the file with rotation"""
        if not self.config_manager.get('auto_backup', True):
            return True, "backup_disabled"

        file_abs_path = self.resolve_path(file_path)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Safe backup name encoding
        safe_path = file_path.replace('/', '__').replace('\\', '__')
        backup_name = f"{safe_path}.{timestamp}.bak"
        backup_path = os.path.join(self.backup_dir, backup_name)

        try:
            shutil.copy2(file_abs_path, backup_path)
            
            # Apply backup rotation
            self._rotate_backups(safe_path)
            
            return True, backup_path
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False, ""

    def _rotate_backups(self, safe_path: str):
        """Rotate backups to prevent unlimited growth"""
        max_backups = self.config_manager.get('backup_rotation_count', 10)
        backup_pattern = f"{safe_path}.*.bak"
        
        backups = list(Path(self.backup_dir).glob(backup_pattern))
        if len(backups) > max_backups:
            # Sort by modification time and remove oldest
            backups_sorted = sorted(backups, key=lambda x: x.stat().st_mtime)
            for old_backup in backups_sorted[:-max_backups]:
                try:
                    old_backup.unlink()
                except Exception as e:
                    print(f"⚠️  Could not delete old backup {old_backup}: {e}")

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

        file_abs_path = self.resolve_path(file_path)
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

    def add_to_history(self, file_path: str):
        """Add file to history with deduplication"""
        if file_path in self.file_history:
            self.file_history.remove(file_path)
        
        self.file_history.insert(0, file_path)
        self.file_history = self.file_history[:self.max_history]

    def get_history(self) -> List[str]:
        """Get file history"""
        return self.file_history.copy()

    def read_file_lines(self, file_path: str) -> Optional[List[str]]:
        """Read file and return lines with proper error handling"""
        file_abs_path = self.resolve_path(file_path)
        
        try:
            with open(file_abs_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None

    def write_file_lines(self, file_path: str, lines: List[str]) -> bool:
        """Write lines to file with proper error handling"""
        file_abs_path = self.resolve_path(file_path)
        
        try:
            with open(file_abs_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        except Exception as e:
            print(f"❌ Error writing file: {e}")
            return False

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return os.path.isfile(self.resolve_path(file_path))

    def directory_exists(self, dir_path: str) -> bool:
        """Check if directory exists"""
        return os.path.isdir(self.resolve_path(dir_path))
