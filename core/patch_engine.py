#!/usr/bin/env python3
"""
Patch Engine for Professional Patch Tool
Core patching logic and operations
"""

import re
import os
from typing import List, Dict, Any, Optional, Tuple
from difflib import unified_diff
from utils import RegexUtils, LineUtils, PatchValidator

class PatchEngine:
    """Core patching engine with advanced operations"""

    def __init__(self, file_manager, config_manager):
        self.file_manager = file_manager
        self.config_manager = config_manager
        self.regex_utils = RegexUtils()
        self.line_utils = LineUtils()
        self.patch_validator = PatchValidator(self.regex_utils)
        self._regex_cache = {}
        self.applied_patches = []

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

    def find_code_blocks(self, file_info: Dict[str, Any], search_pattern: str,
                        context_lines: int = 3) -> List[Dict[str, Any]]:
        """Find code blocks matching pattern with context"""
        matches = []
        regex = self._get_compiled_regex(search_pattern)
        if not regex:
            return []

        for i, line in enumerate(file_info['line_list']):
            if regex.search(line):
                start = max(0, i - context_lines)
                end = min(len(file_info['line_list']), i + context_lines + 1)

                # Calculate context with line numbers
                context_with_numbers = []
                for j in range(start, end):
                    context_with_numbers.append({
                        'line_number': j + 1,
                        'content': file_info['line_list'][j]
                    })

                matches.append({
                    'line_number': i + 1,
                    'context_start': start + 1,
                    'context_end': end,
                    'context': context_with_numbers,
                    'match_index': len(matches) + 1,
                    'full_match': line,
                    'match_groups': regex.search(line).groups() if regex.search(line) else ()
                })
        return matches

    def apply_patches(self, file_path: str, patches: List[Dict[str, Any]]) -> Tuple[bool, Dict[str, Any]]:
        """Apply all queued patches with enhanced error handling"""
        if not patches:
            return False, {"error": "No patches to apply"}

        # Validate patches before applying
        file_info = self.file_manager.get_file_info(file_path)
        if file_info:
            for patch in patches:
                is_valid, message = self.validate_patch(patch, file_info)
                if not is_valid:
                    return False, {"error": f"Patch validation failed: {message}"}

        # Create backup
        backup_success, backup_path = self.file_manager.create_backup(file_path)
        if not backup_success and self.config_manager.get('auto_backup', True):
            print("⚠️  Backup creation failed, continuing without backup")

        # Read original file
        original_lines = self.file_manager.read_file_lines(file_path)
        if original_lines is None:
            return False, {"error": "Could not read file"}

        original_line_count = len(original_lines)
        working_lines = original_lines.copy()
        successful_patches = []
        failed_patches = []

        # Sort patches to apply from bottom to top (avoid line number issues)
        sorted_patches = sorted(patches,
                              key=lambda x: x.get('line_number', x.get('start_line', 0)),
                              reverse=True)

        for patch in sorted_patches:
            try:
                success, result = self._apply_single_patch(working_lines, patch)
                if success:
                    successful_patches.append({
                        'patch': patch,
                        'result': result
                    })
                else:
                    failed_patches.append({
                        'patch': patch,
                        'error': result
                    })
            except Exception as e:
                failed_patches.append({
                    'patch': patch,
                    'error': str(e)
                })

        # Calculate changes
        changes_applied = len(successful_patches) > 0

        if changes_applied:
            # Write modified file
            if self.file_manager.write_file_lines(file_path, working_lines):
                result_info = {
                    "success": True,
                    "original_lines": original_line_count,
                    "new_lines": len(working_lines),
                    "successful_patches": len(successful_patches),
                    "failed_patches": len(failed_patches),
                    "backup_path": backup_path,
                    "changes": successful_patches
                }

                # Generate diff for summary
                diff = self._generate_diff(original_lines, working_lines, file_path)
                result_info["diff"] = diff

                return True, result_info
            else:
                # Restore from backup if write failed
                if backup_path and os.path.exists(backup_path):
                    self.file_manager.restore_backup(file_path)
                    print("🔄 Restored original file from backup due to write failure")
                return False, {"error": "Failed to write file"}
        else:
            return False, {
                "error": "No patches were successfully applied",
                "failed_patches": failed_patches
            }

    def _apply_single_patch(self, lines: List[str], patch: Dict[str, Any]) -> Tuple[bool, str]:
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
                return False, f"Unknown patch type: {patch_type}"
        except Exception as e:
            return False, f"Error applying patch: {e}"

    def _patch_insert_at_line(self, lines: List[str], line_number: int, new_code: List[str]) -> Tuple[bool, str]:
        """Insert code at specific line with indentation preservation"""
        insert_pos = line_number - 1

        # Ensure we don't go beyond the end of the file
        if insert_pos > len(lines):
            insert_pos = len(lines)

        # Detect indentation from context if available
        base_indentation = self._detect_context_indentation(lines, insert_pos)

        # Apply indentation to new code
        indented_code = self._apply_indentation(new_code, base_indentation)

        for i, line in enumerate(indented_code):
            lines.insert(insert_pos + i, line + '\n')

        return True, f"Inserted {len(new_code)} lines at line {line_number}"

    def _patch_replace_range(self, lines: List[str], start_line: int, end_line: int, new_code: List[str]) -> Tuple[bool, str]:
        """Replace a range of lines with indentation preservation"""
        # Detect indentation from the first line being replaced
        base_indentation = self._detect_line_indentation(lines[start_line - 1])

        # Apply indentation to new code
        indented_code = self._apply_indentation(new_code, base_indentation)

        # Remove old lines
        del lines[start_line-1:end_line]

        # Insert new lines with proper newlines
        for i, line in enumerate(indented_code):
            lines.insert(start_line-1 + i, line + '\n')

        return True, f"Replaced lines {start_line}-{end_line} with {len(new_code)} lines"

    def _patch_replace_pattern(self, lines: List[str], pattern: str, new_code: List[str], match_line: int = None) -> Tuple[bool, str]:
        """Replace lines matching pattern at specific line"""
        regex = self._get_compiled_regex(pattern)
        if not regex:
            return False, f"Invalid regex pattern: {pattern}"

        if match_line:
            # Replace at specific line
            line_idx = match_line - 1
            if 0 <= line_idx < len(lines) and regex.search(lines[line_idx]):
                # Detect indentation from the line being replaced
                base_indentation = self._detect_line_indentation(lines[line_idx])
                indented_code = self._apply_indentation(new_code, base_indentation)

                # Replace single line with potentially multiple lines
                del lines[line_idx]
                for j, new_line in enumerate(indented_code):
                    lines.insert(line_idx + j, new_line + '\n')
                return True, f"Replaced pattern at line {match_line}"
        else:
            # Find and replace first occurrence
            for i, line in enumerate(lines):
                if regex.search(line):
                    # Detect indentation and apply
                    base_indentation = self._detect_line_indentation(line)
                    indented_code = self._apply_indentation(new_code, base_indentation)

                    # Replace single line with potentially multiple lines
                    del lines[i]
                    for j, new_line in enumerate(indented_code):
                        lines.insert(i + j, new_line + '\n')
                    return True, f"Replaced pattern at line {i+1}"

        return False, f"Pattern not found: {pattern}"

    def _patch_replace_pattern_all(self, lines: List[str], pattern: str, new_code: List[str]) -> Tuple[bool, str]:
        """Replace all occurrences of pattern"""
        regex = self._get_compiled_regex(pattern)
        if not regex:
            return False, f"Invalid regex pattern: {pattern}"

        replacements = 0
        i = 0
        while i < len(lines):
            if regex.search(lines[i]):
                # Detect indentation from current line
                base_indentation = self._detect_line_indentation(lines[i])
                indented_code = self._apply_indentation(new_code, base_indentation)

                # Replace this occurrence
                del lines[i]
                for j, new_line in enumerate(indented_code):
                    lines.insert(i + j, new_line + '\n')
                replacements += 1
                i += len(indented_code)  # Skip the newly inserted lines
            else:
                i += 1

        if replacements > 0:
            return True, f"Replaced pattern at {replacements} locations"
        else:
            return False, f"Pattern not found: {pattern}"

    def _patch_insert_after(self, lines: List[str], pattern: str, new_code: List[str]) -> Tuple[bool, str]:
        """Insert code after pattern with context indentation"""
        regex = self._get_compiled_regex(pattern)
        if not regex:
            return False, f"Invalid regex pattern: {pattern}"

        for i, line in enumerate(lines):
            if regex.search(line):
                insert_pos = i + 1

                # Detect indentation from context
                base_indentation = self._detect_context_indentation(lines, insert_pos)
                indented_code = self._apply_indentation(new_code, base_indentation)

                for j, new_line in enumerate(indented_code):
                    lines.insert(insert_pos + j, new_line + '\n')
                return True, f"Inserted after pattern at line {i+1}"

        return False, f"Pattern not found: {pattern}"

    def _patch_insert_before(self, lines: List[str], pattern: str, new_code: List[str]) -> Tuple[bool, str]:
        """Insert code before pattern with context indentation"""
        regex = self._get_compiled_regex(pattern)
        if not regex:
            return False, f"Invalid regex pattern: {pattern}"

        for i, line in enumerate(lines):
            if regex.search(line):
                # Detect indentation from context
                base_indentation = self._detect_context_indentation(lines, i)
                indented_code = self._apply_indentation(new_code, base_indentation)

                for j, new_line in enumerate(indented_code):
                    lines.insert(i + j, new_line + '\n')
                return True, f"Inserted before pattern at line {i+1}"

        return False, f"Pattern not found: {pattern}"

    def _patch_append(self, lines: List[str], new_code: List[str]) -> Tuple[bool, str]:
        """Append code to end of file"""
        # Detect indentation from last line or use empty
        base_indentation = ""
        if lines:
            base_indentation = self._detect_line_indentation(lines[-1])

        indented_code = self._apply_indentation(new_code, base_indentation)

        for line in indented_code:
            lines.append(line + '\n')

        return True, f"Appended {len(new_code)} lines to end of file"

    def _patch_delete_range(self, lines: List[str], start_line: int, end_line: int) -> Tuple[bool, str]:
        """Delete a range of lines"""
        del lines[start_line-1:end_line]
        return True, f"Deleted lines {start_line}-{end_line}"

    def _detect_line_indentation(self, line: str) -> str:
        """Detect indentation from a line"""
        # Count leading spaces or tabs
        if not line.strip():  # Empty line
            return ""

        match = re.match(r'^(\s*)', line)
        return match.group(1) if match else ""

    def _detect_context_indentation(self, lines: List[str], position: int) -> str:
        """Detect indentation from context around position"""
        # Check previous non-empty line
        for i in range(position - 1, -1, -1):
            if i < len(lines) and lines[i].strip():
                return self._detect_line_indentation(lines[i])

        # Check next non-empty line if no previous lines
        for i in range(position, len(lines)):
            if lines[i].strip():
                return self._detect_line_indentation(lines[i])

        return ""  # No context found

    def _apply_indentation(self, code_lines: List[str], indentation: str) -> List[str]:
        """Apply indentation to code lines"""
        if not indentation:
            return code_lines

        indented_lines = []
        for line in code_lines:
            if line.strip():  # Only indent non-empty lines
                indented_lines.append(indentation + line)
            else:
                indented_lines.append(line)

        return indented_lines

    def _generate_diff(self, original_lines: List[str], new_lines: List[str], file_path: str) -> List[str]:
        """Generate unified diff between original and new content"""
        return list(unified_diff(
            original_lines,
            new_lines,
            fromfile=f'a/{file_path}',
            tofile=f'b/{file_path}',
            lineterm=''
        ))

    def validate_patch(self, patch: Dict[str, Any], file_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate if a patch can be applied to a file using PatchValidator"""
        return self.patch_validator.validate_patch(patch, file_info)
