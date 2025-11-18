#!/usr/bin/env python3
"""
Validation Utilities for Professional Patch Tool
Input validation, patch validation, and file validation
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple, Callable
from pathlib import Path


class Validation:
    """General validation utilities"""
    
    @staticmethod
    def is_valid_filename(filename: str) -> Tuple[bool, str]:
        """Validate filename for safety"""
        if not filename or not filename.strip():
            return False, "Filename cannot be empty"
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
        for char in invalid_chars:
            if char in filename:
                return False, f"Filename contains invalid character: {char}"
        
        # Check for reserved names (Windows)
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
            'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 
            'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        name_without_ext = Path(filename).stem.upper()
        if name_without_ext in reserved_names:
            return False, f"Filename is a reserved system name: {filename}"
        
        # Check length
        if len(filename) > 255:
            return False, "Filename too long (max 255 characters)"
        
        return True, "Valid filename"
    
    @staticmethod
    def is_valid_path(path: str, check_exists: bool = False) -> Tuple[bool, str]:
        """Validate file path"""
        if not path or not path.strip():
            return False, "Path cannot be empty"
        
        try:
            # Check if path is absolute or can be made absolute
            abs_path = os.path.abspath(path)
            
            # Check for path traversal attempts
            if '..' in path and not os.path.normpath(path) == path:
                return False, "Path traversal not allowed"
            
            # Check if path exists if requested
            if check_exists and not os.path.exists(abs_path):
                return False, "Path does not exist"
            
            return True, "Valid path"
        
        except (ValueError, OSError) as e:
            return False, f"Invalid path: {e}"
    
    @staticmethod
    def is_safe_file_operation(source: str, destination: str) -> Tuple[bool, str]:
        """Validate that a file operation is safe"""
        # Check if source and destination are the same
        if os.path.abspath(source) == os.path.abspath(destination):
            return False, "Source and destination are the same"
        
        # Check if destination is inside source (to prevent recursive copies)
        source_abs = os.path.abspath(source)
        dest_abs = os.path.abspath(destination)
        
        if dest_abs.startswith(source_abs + os.sep):
            return False, "Destination cannot be inside source directory"
        
        return True, "Safe file operation"
    
    @staticmethod
    def validate_integer(value: str, min_value: int = None, max_value: int = None) -> Tuple[bool, Optional[int]]:
        """Validate integer input"""
        try:
            int_value = int(value)
            
            if min_value is not None and int_value < min_value:
                return False, f"Value must be at least {min_value}"
            
            if max_value is not None and int_value > max_value:
                return False, f"Value must be at most {max_value}"
            
            return True, int_value
        
        except ValueError:
            return False, "Value must be a valid integer"
    
    @staticmethod
    def validate_choice(choice: str, valid_choices: List[str], case_sensitive: bool = False) -> Tuple[bool, str]:
        """Validate user choice from a list of valid options"""
        if not case_sensitive:
            choice = choice.lower()
            valid_choices = [c.lower() for c in valid_choices]
        
        if choice in valid_choices:
            return True, "Valid choice"
        else:
            return False, f"Choice must be one of: {', '.join(valid_choices)}"
    
    @staticmethod
    def validate_regex_pattern(pattern: str) -> Tuple[bool, str]:
        """Validate regex pattern syntax"""
        try:
            re.compile(pattern)
            return True, "Valid regex pattern"
        except re.error as e:
            return False, f"Invalid regex: {e}"


class PatchValidator:
    """Validate patches before application"""
    
    def __init__(self, regex_utils=None):
        self.regex_utils = regex_utils
        self.validation_rules = self._initialize_validation_rules()
    
    def _initialize_validation_rules(self) -> Dict[str, Callable]:
        """Initialize validation rules for different patch types"""
        return {
            'insert_at_line': self._validate_insert_at_line,
            'replace_range': self._validate_replace_range,
            'replace_pattern': self._validate_replace_pattern,
            'replace_pattern_all': self._validate_replace_pattern,
            'insert_after': self._validate_pattern_based,
            'insert_before': self._validate_pattern_based,
            'append': self._validate_append,
            'delete_range': self._validate_delete_range
        }
    
    def validate_patch(self, patch: Dict[str, Any], file_info: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Validate a patch before application"""
        if not patch or 'type' not in patch:
            return False, "Patch must have a type"
        
        patch_type = patch['type']
        validator = self.validation_rules.get(patch_type)
        
        if not validator:
            return False, f"Unknown patch type: {patch_type}"
        
        return validator(patch, file_info)
    
    def _validate_insert_at_line(self, patch: Dict[str, Any], file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate insert_at_line patch"""
        if 'line_number' not in patch:
            return False, "Missing line_number"
        
        if 'code' not in patch or not patch['code']:
            return False, "Missing code to insert"
        
        line_num = patch['line_number']
        
        if not isinstance(line_num, int) or line_num < 1:
            return False, "Line number must be a positive integer"
        
        if file_info and line_num > file_info['lines'] + 1:
            return False, f"Line number {line_num} exceeds file length {file_info['lines']}"
        
        return True, "Valid insert_at_line patch"
    
    def _validate_replace_range(self, patch: Dict[str, Any], file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate replace_range patch"""
        required_fields = ['start_line', 'end_line', 'code']
        for field in required_fields:
            if field not in patch:
                return False, f"Missing {field}"
        
        start_line = patch['start_line']
        end_line = patch['end_line']
        
        if not isinstance(start_line, int) or not isinstance(end_line, int):
            return False, "Line numbers must be integers"
        
        if start_line < 1 or end_line < 1:
            return False, "Line numbers must be positive"
        
        if start_line > end_line:
            return False, "Start line must be less than or equal to end line"
        
        if file_info:
            if start_line > file_info['lines']:
                return False, f"Start line {start_line} exceeds file length {file_info['lines']}"
            if end_line > file_info['lines']:
                return False, f"End line {end_line} exceeds file length {file_info['lines']}"
        
        return True, "Valid replace_range patch"
    
    def _validate_replace_pattern(self, patch: Dict[str, Any], file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate replace_pattern patch"""
        if 'pattern' not in patch:
            return False, "Missing pattern"
        
        if 'code' not in patch:
            return False, "Missing replacement code"
        
        # Validate regex pattern
        pattern = patch['pattern']
        is_valid, message = Validation.validate_regex_pattern(pattern)
        if not is_valid:
            return False, f"Invalid regex pattern: {message}"
        
        return True, "Valid replace_pattern patch"
    
    def _validate_pattern_based(self, patch: Dict[str, Any], file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate insert_after and insert_before patches"""
        pattern_field = None
        for field in ['after', 'before']:
            if field in patch:
                pattern_field = field
                break
        
        if not pattern_field:
            return False, "Missing 'after' or 'before' pattern"
        
        if 'code' not in patch:
            return False, "Missing code to insert"
        
        # Validate regex pattern
        pattern = patch[pattern_field]
        is_valid, message = Validation.validate_regex_pattern(pattern)
        if not is_valid:
            return False, f"Invalid regex pattern: {message}"
        
        return True, f"Valid {patch['type']} patch"
    
    def _validate_append(self, patch: Dict[str, Any], file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate append patch"""
        if 'code' not in patch or not patch['code']:
            return False, "Missing code to append"
        
        return True, "Valid append patch"
    
    def _validate_delete_range(self, patch: Dict[str, Any], file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate delete_range patch"""
        if 'start_line' not in patch or 'end_line' not in patch:
            return False, "Missing start_line or end_line"
        
        start_line = patch['start_line']
        end_line = patch['end_line']
        
        if not isinstance(start_line, int) or not isinstance(end_line, int):
            return False, "Line numbers must be integers"
        
        if start_line < 1 or end_line < 1:
            return False, "Line numbers must be positive"
        
        if start_line > end_line:
            return False, "Start line must be less than or equal to end line"
        
        if file_info:
            if start_line > file_info['lines']:
                return False, f"Start line {start_line} exceeds file length {file_info['lines']}"
            if end_line > file_info['lines']:
                return False, f"End line {end_line} exceeds file length {file_info['lines']}"
        
        return True, "Valid delete_range patch"
    
    def validate_patch_sequence(self, patches: List[Dict[str, Any]], file_info: Dict[str, Any] = None) -> Tuple[bool, List[str]]:
        """Validate a sequence of patches"""
        errors = []
        all_valid = True
        
        for i, patch in enumerate(patches):
            is_valid, message = self.validate_patch(patch, file_info)
            if not is_valid:
                all_valid = False
                errors.append(f"Patch {i+1} ({patch.get('type', 'unknown')}): {message}")
        
        return all_valid, errors
    
    def check_patch_conflicts(self, patches: List[Dict[str, Any]]) -> List[Tuple[int, int, str]]:
        """Check for conflicts between patches in a sequence"""
        conflicts = []
        
        for i in range(len(patches)):
            for j in range(i + 1, len(patches)):
                patch1 = patches[i]
                patch2 = patches[j]
                
                conflict = self._detect_patch_conflict(patch1, patch2)
                if conflict:
                    conflicts.append((i, j, conflict))
        
        return conflicts
    
    def _detect_patch_conflict(self, patch1: Dict[str, Any], patch2: Dict[str, Any]) -> Optional[str]:
        """Detect conflict between two patches"""
        type1 = patch1['type']
        type2 = patch2['type']
        
        # Check for overlapping line ranges
        if type1 in ['replace_range', 'delete_range'] and type2 in ['replace_range', 'delete_range', 'insert_at_line']:
            range1 = self._get_patch_range(patch1)
            range2 = self._get_patch_range(patch2)
            
            if range1 and range2 and self._ranges_overlap(range1, range2):
                return f"Overlapping line ranges: {range1} and {range2}"
        
        # Check for pattern-based conflicts
        if type1 in ['replace_pattern', 'replace_pattern_all'] and type2 in ['replace_pattern', 'replace_pattern_all']:
            if patch1.get('pattern') == patch2.get('pattern'):
                return f"Same pattern used in multiple replacements: {patch1['pattern']}"
        
        return None
    
    def _get_patch_range(self, patch: Dict[str, Any]) -> Optional[Tuple[int, int]]:
        """Get the line range affected by a patch"""
        patch_type = patch['type']
        
        if patch_type in ['replace_range', 'delete_range']:
            return (patch['start_line'], patch['end_line'])
        elif patch_type == 'insert_at_line':
            line_num = patch['line_number']
            return (line_num, line_num + len(patch.get('code', [])) - 1)
        
        return None
    
    def _ranges_overlap(self, range1: Tuple[int, int], range2: Tuple[int, int]) -> bool:
        """Check if two line ranges overlap"""
        start1, end1 = range1
        start2, end2 = range2
        return not (end1 < start2 or end2 < start1)


class FileValidator:
    """File-specific validation utilities"""
    
    @staticmethod
    def validate_file_readable(file_path: str) -> Tuple[bool, str]:
        """Validate that a file exists and is readable"""
        if not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}"
        
        if not os.path.isfile(file_path):
            return False, f"Path is not a file: {file_path}"
        
        if not os.access(file_path, os.R_OK):
            return False, f"File is not readable: {file_path}"
        
        return True, "File is readable"
    
    @staticmethod
    def validate_file_writable(file_path: str) -> Tuple[bool, str]:
        """Validate that a file can be written to"""
        # Check if directory exists and is writable
        directory = os.path.dirname(file_path) or '.'
        
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError:
                return False, f"Cannot create directory: {directory}"
        
        if not os.access(directory, os.W_OK):
            return False, f"Directory is not writable: {directory}"
        
        # If file exists, check if it's writable
        if os.path.exists(file_path):
            if not os.access(file_path, os.W_OK):
                return False, f"File is not writable: {file_path}"
        
        return True, "File is writable"
    
    @staticmethod
    def validate_file_size(file_path: str, max_size_mb: int = 10) -> Tuple[bool, str]:
        """Validate that file size is within limits"""
        try:
            file_size = os.path.getsize(file_path)
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if file_size > max_size_bytes:
                size_mb = file_size / (1024 * 1024)
                return False, f"File too large: {size_mb:.1f}MB (max {max_size_mb}MB)"
            
            return True, f"File size OK: {file_size} bytes"
        
        except OSError as e:
            return False, f"Cannot check file size: {e}"
    
    @staticmethod
    def validate_file_encoding(file_path: str, expected_encoding: str = 'utf-8') -> Tuple[bool, str]:
        """Validate file encoding (basic detection)"""
        try:
            with open(file_path, 'r', encoding=expected_encoding) as f:
                # Try to read a sample to test encoding
                f.read(1024)
            return True, f"File encoding appears to be {expected_encoding}"
        
        except UnicodeDecodeError:
            return False, f"File is not {expected_encoding} encoded"
        except Exception as e:
            return False, f"Error checking encoding: {e}"
    
    @staticmethod
    def validate_backup_safety(original_path: str, backup_path: str) -> Tuple[bool, str]:
        """Validate that backup operation is safe"""
        # Check if original file exists and is readable
        readable, message = FileValidator.validate_file_readable(original_path)
        if not readable:
            return False, f"Cannot backup: {message}"
        
        # Check if backup path is different
        if os.path.abspath(original_path) == os.path.abspath(backup_path):
            return False, "Backup path cannot be the same as original path"
        
        # Check if backup directory is writable
        backup_dir = os.path.dirname(backup_path) or '.'
        if not os.access(backup_dir, os.W_OK):
            return False, f"Backup directory is not writable: {backup_dir}"
        
        return True, "Backup operation is safe"


# Example usage and testing
if __name__ == "__main__":
    # Test validation utilities
    validator = PatchValidator()
    
    # Test patch validation
    test_patch = {
        'type': 'insert_at_line',
        'line_number': 5,
        'code': ['print("hello")', 'return True']
    }
    
    is_valid, message = validator.validate_patch(test_patch)
    print(f"Patch validation: {is_valid}, {message}")
    
    # Test file validation
    file_path = "test_file.py"
    readable, msg = FileValidator.validate_file_readable(file_path)
    print(f"File readable: {readable}, {msg}")
    
    # Test general validation
    valid, value = Validation.validate_integer("42", min_value=1, max_value=100)
    print(f"Integer validation: {valid}, value: {value}")
