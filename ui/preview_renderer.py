#!/usr/bin/env python3
"""
Preview Renderer for Professional Patch Tool
Advanced file preview and diff display rendering
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from difflib import unified_diff


class PreviewRenderer:
    """Advanced preview rendering with diff support"""
    
    def __init__(self, syntax_highlighter, config_manager):
        self.syntax_highlighter = syntax_highlighter
        self.config_manager = config_manager

    def render_file_preview(self, file_info: Dict[str, Any], 
                          start_line: int = 1, 
                          num_lines: int = 20,
                          highlight_changes: bool = False,
                          change_ranges: List[Tuple[int, int]] = None) -> str:
        """Render a file preview with optional change highlighting"""
        output = []
        
        # Header
        output.append(f"\n📄 File: {file_info['relative_path']}")
        output.append(f"📊 Size: {file_info['size']} bytes, Lines: {file_info['lines']}, Language: {file_info['language']}")
        output.append(f"🕒 Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("─" * 80)
        
        # Calculate line range
        end_line = min(start_line + num_lines - 1, file_info['lines'])
        change_ranges = change_ranges or []
        
        # Render lines
        for i in range(start_line - 1, end_line):
            if i < len(file_info['line_list']):
                line_num = i + 1
                line_content = file_info['line_list'][i]
                
                # Apply syntax highlighting
                if self.config_manager.get("enable_syntax_hints", True):
                    line_content = self.syntax_highlighter.highlight_line(
                        line_content, file_info['language']
                    )
                
                # Apply change highlighting if needed
                line_prefix = f"{line_num:4d} │ "
                if highlight_changes and self._is_line_changed(line_num, change_ranges):
                    line_prefix = f"{line_num:4d} 🟡│ "
                
                output.append(f"{line_prefix}{line_content}")
        
        output.append("─" * 80)
        if end_line < file_info['lines']:
            output.append(f"... and {file_info['lines'] - end_line} more lines")
            
        return "\n".join(output)

    def render_line_range(self, file_info: Dict[str, Any], 
                         start_line: int, 
                         end_line: int,
                         context_lines: int = 0) -> str:
        """Render a specific line range with context"""
        output = []
        
        # Calculate context
        actual_start = max(1, start_line - context_lines)
        actual_end = min(file_info['lines'], end_line + context_lines)
        
        output.append(f"\n🔍 Lines {start_line}-{end_line} (with context):")
        output.append("─" * 80)
        
        for i in range(actual_start - 1, actual_end):
            if i < len(file_info['line_list']):
                line_num = i + 1
                line_content = file_info['line_list'][i]
                
                # Highlight the target range
                if start_line <= line_num <= end_line:
                    line_prefix = f"{line_num:4d} 🟡│ "
                else:
                    line_prefix = f"{line_num:4d}   │ "
                
                # Apply syntax highlighting
                if self.config_manager.get("enable_syntax_hints", True):
                    line_content = self.syntax_highlighter.highlight_line(
                        line_content, file_info['language']
                    )
                
                output.append(f"{line_prefix}{line_content}")
        
        output.append("─" * 80)
        return "\n".join(output)

    def render_diff_preview(self, original_lines: List[str], 
                          modified_lines: List[str],
                          file_path: str,
                          context_lines: int = 3) -> str:
        """Render a unified diff preview"""
        output = []
        
        output.append(f"\n🔍 DIFF PREVIEW: {file_path}")
        output.append("=" * 80)
        
        diff = list(unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm='',
            n=context_lines
        ))
        
        if not diff:
            output.append("No changes detected")
            return "\n".join(output)
        
        for line in diff:
            if line.startswith('---'):
                output.append(f"🔴 {line}")
            elif line.startswith('+++'):
                output.append(f"🟢 {line}")
            elif line.startswith('@'):
                output.append(f"🔵 {line}")
            elif line.startswith('-'):
                output.append(f"🔴 {line}")
            elif line.startswith('+'):
                output.append(f"🟢 {line}")
            else:
                output.append(f"  {line}")
                
        output.append("=" * 80)
        return "\n".join(output)

    def render_side_by_side_diff(self, original_lines: List[str],
                               modified_lines: List[str],
                               file_path: str,
                               max_width: int = 40) -> str:
        """Render a side-by-side diff preview"""
        output = []
        
        output.append(f"\n🔍 SIDE-BY-SIDE DIFF: {file_path}")
        output.append("=" * (max_width * 2 + 3))
        output.append(f"{'ORIGINAL':<{max_width}} | {'MODIFIED':<{max_width}}")
        output.append("-" * (max_width * 2 + 3))
        
        # Create simple diff representation
        original_display = []
        modified_display = []
        
        # Pad lists to same length
        max_len = max(len(original_lines), len(modified_lines))
        original_padded = original_lines + [''] * (max_len - len(original_lines))
        modified_padded = modified_lines + [''] * (max_len - len(modified_lines))
        
        for i in range(min(max_len, 50)):  # Limit display
            orig_line = original_padded[i].rstrip()
            mod_line = modified_padded[i].rstrip()
            
            # Truncate long lines
            if len(orig_line) > max_width:
                orig_line = orig_line[:max_width-3] + '...'
            if len(mod_line) > max_width:
                mod_line = mod_line[:max_width-3] + '...'
            
            if orig_line != mod_line:
                if orig_line and not mod_line:  # Deleted
                    original_display.append(f"🔴 {orig_line}")
                    modified_display.append(' ' * max_width)
                elif not orig_line and mod_line:  # Added
                    original_display.append(' ' * max_width)
                    modified_display.append(f"🟢 {mod_line}")
                else:  # Modified
                    original_display.append(f"🟡 {orig_line}")
                    modified_display.append(f"🟡 {mod_line}")
            else:  # Unchanged
                original_display.append(f"  {orig_line}")
                modified_display.append(f"  {mod_line}")
        
        # Display side by side
        for i in range(len(original_display)):
            orig = original_display[i].ljust(max_width)
            mod = modified_display[i].ljust(max_width)
            output.append(f"{orig} | {mod}")
        
        output.append("=" * (max_width * 2 + 3))
        output.append("Legend: 🔴 Removed  🟢 Added  🟡 Modified")
        
        return "\n".join(output)

    def render_patch_queue_preview(self, patches: List[Dict[str, Any]]) -> str:
        """Render a preview of the patch queue"""
        output = []
        
        if not patches:
            return "❌ No patches in queue"
        
        output.append(f"\n📋 PATCH QUEUE ({len(patches)} patches):")
        output.append("─" * 80)
        
        for i, patch in enumerate(patches, 1):
            output.append(f"{i}. {patch['description']}")
            
            if 'code' in patch and patch['code']:
                # Show code preview
                code_preview = ' | '.join(patch['code'][:2])
                if len(patch['code']) > 2:
                    code_preview += f" ... (+{len(patch['code'])-2} lines)"
                output.append(f"   Code: {code_preview}")
            
            # Show patch details based on type
            patch_type = patch.get('type', 'unknown')
            if patch_type == 'insert_at_line':
                output.append(f"   📍 Insert at line: {patch['line_number']}")
            elif patch_type == 'replace_range':
                output.append(f"   🔄 Replace lines: {patch['start_line']}-{patch['end_line']}")
            elif patch_type in ['replace_pattern', 'insert_after', 'insert_before']:
                pattern = patch.get('pattern', patch.get('after', patch.get('before', '')))
                output.append(f"   🔍 Pattern: {pattern[:50]}{'...' if len(pattern) > 50 else ''}")
            
            if i < len(patches):  # Add separator between patches
                output.append("   " + "─" * 70)
        
        output.append("─" * 80)
        return "\n".join(output)

    def render_search_results(self, matches: List[Dict[str, Any]], 
                            file_info: Dict[str, Any]) -> str:
        """Render search results"""
        output = []
        
        if not matches:
            return "❌ No matches found."
        
        output.append(f"\n🔍 Found {len(matches)} matches:")
        
        for i, match in enumerate(matches, 1):
            output.append(f"\n[{i}] Line {match['line_number']}:")
            output.append(f"    Match: {match['full_match'][:100]}{'...' if len(match['full_match']) > 100 else ''}")
            
            # Show context if available
            if match.get('context'):
                output.append("    Context:")
                for ctx_line in match['context'][:3]:  # Show first 3 context lines
                    line_num = ctx_line['line_number']
                    content = ctx_line['content']
                    output.append(f"      {line_num:4d} │ {content[:80]}{'...' if len(content) > 80 else ''}")
        
        return "\n".join(output)

    def render_file_statistics(self, file_info: Dict[str, Any]) -> str:
        """Render file statistics"""
        output = []
        
        output.append(f"\n📊 FILE STATISTICS: {file_info['relative_path']}")
        output.append("─" * 60)
        output.append(f"📄 Size: {file_info['size']} bytes")
        output.append(f"📝 Lines: {file_info['lines']}")
        output.append(f"🔤 Language: {file_info['language']}")
        output.append(f"🕒 Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"📅 Created: {file_info.get('created', file_info['modified']).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Calculate additional statistics
        if file_info['line_list']:
            empty_lines = sum(1 for line in file_info['line_list'] if not line.strip())
            comment_lines = sum(1 for line in file_info['line_list'] if line.strip().startswith(('#', '//', '/*', '*')))
            code_lines = file_info['lines'] - empty_lines - comment_lines
            
            output.append(f"\n📈 LINE ANALYSIS:")
            output.append(f"   📝 Code lines: {code_lines} ({code_lines/file_info['lines']*100:.1f}%)")
            output.append(f"   💬 Comment lines: {comment_lines} ({comment_lines/file_info['lines']*100:.1f}%)")
            output.append(f"   ⬜ Empty lines: {empty_lines} ({empty_lines/file_info['lines']*100:.1f}%)")
        
        output.append("─" * 60)
        return "\n".join(output)

    def _is_line_changed(self, line_num: int, change_ranges: List[Tuple[int, int]]) -> bool:
        """Check if a line is within change ranges"""
        for start, end in change_ranges:
            if start <= line_num <= end:
                return True
        return False

    def format_line_number(self, line_num: int, max_line_num: int) -> str:
        """Format line number with consistent width"""
        width = len(str(max_line_num))
        return f"{line_num:{width}d}"

    def truncate_line(self, line: str, max_length: int = 100) -> str:
        """Truncate long lines for display"""
        if len(line) <= max_length:
            return line
        return line[:max_length-3] + '...'
