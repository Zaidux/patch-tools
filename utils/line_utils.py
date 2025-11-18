#!/usr/bin/env python3
"""
Line Manipulation Utilities for Professional Patch Tool
Line processing, indentation handling, and block detection
"""

import re
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass


@dataclass
class LineInfo:
    """Information about a single line"""
    number: int
    content: str
    stripped: str
    indentation: int
    is_empty: bool
    is_comment: bool
    
    @classmethod
    def from_line(cls, line: str, line_number: int, comment_patterns: List[str] = None):
        """Create LineInfo from a line string"""
        if comment_patterns is None:
            comment_patterns = ['#', '//']
        
        stripped = line.strip()
        indentation = len(line) - len(line.lstrip())
        is_empty = not bool(stripped)
        
        # Check if it's a comment
        is_comment = False
        if not is_empty:
            for pattern in comment_patterns:
                if stripped.startswith(pattern):
                    is_comment = True
                    break
        
        return cls(
            number=line_number,
            content=line.rstrip('\n\r'),
            stripped=stripped,
            indentation=indentation,
            is_empty=is_empty,
            is_comment=is_comment
        )


class LineUtils:
    """Utility functions for line manipulation"""
    
    def __init__(self):
        self.comment_patterns = ['#', '//', '/*', '*', '--']
    
    def normalize_lines(self, lines: List[str], preserve_empty: bool = True, 
                       preserve_comments: bool = True) -> List[str]:
        """Normalize lines by stripping whitespace and handling empty lines/comments"""
        normalized = []
        
        for line in lines:
            stripped = line.rstrip('\n\r')
            
            # Create line info
            line_info = LineInfo.from_line(stripped, len(normalized) + 1, self.comment_patterns)
            
            # Apply filters
            if not preserve_empty and line_info.is_empty:
                continue
            
            if not preserve_comments and line_info.is_comment:
                continue
            
            normalized.append(stripped)
        
        return normalized
    
    def detect_indentation(self, lines: List[str], sample_size: int = 10) -> Tuple[str, int]:
        """Detect the predominant indentation style and size"""
        if not lines:
            return "spaces", 4  # Default
        
        # Analyze first few non-empty lines
        indentation_samples = []
        
        for line in lines[:sample_size]:
            line_info = LineInfo.from_line(line, 0, self.comment_patterns)
            
            if not line_info.is_empty and not line_info.is_comment and line_info.indentation > 0:
                # Get the indentation characters
                indentation_str = line[:line_info.indentation]
                indentation_samples.append(indentation_str)
        
        if not indentation_samples:
            return "spaces", 4  # Default
        
        # Count spaces vs tabs
        space_count = 0
        tab_count = 0
        
        for sample in indentation_samples:
            if sample.startswith(' '):
                space_count += 1
                # Count consecutive spaces for size
                spaces = len(re.match(r'^ +', sample).group())
            elif sample.startswith('\t'):
                tab_count += 1
        
        # Determine style
        if space_count > tab_count:
            style = "spaces"
            # Find most common indentation size
            sizes = []
            for sample in indentation_samples:
                if sample.startswith(' '):
                    match = re.match(r'^( +)', sample)
                    if match:
                        sizes.append(len(match.group(1)))
            
            if sizes:
                size = max(set(sizes), key=sizes.count)
            else:
                size = 4
        else:
            style = "tabs"
            size = 1  # Tabs are always size 1 for counting
        
        return style, size
    
    def reindent_lines(self, lines: List[str], new_indentation: int, 
                      indentation_style: str = "spaces") -> List[str]:
        """Reindent lines to specified indentation level"""
        if not lines:
            return lines
        
        reindented = []
        indent_char = ' ' if indentation_style == "spaces" else '\t'
        indent_str = indent_char * new_indentation
        
        for line in lines:
            if line.strip():  # Non-empty line
                reindented.append(indent_str + line.lstrip())
            else:
                reindented.append('')  # Preserve empty lines
        
        return reindented
    
    def preserve_context_indentation(self, new_lines: List[str], context_lines: List[str], 
                                   insertion_point: int) -> List[str]:
        """Preserve indentation from context when inserting new lines"""
        if not context_lines or not new_lines:
            return new_lines
        
        # Find the closest non-empty line before insertion point for indentation reference
        reference_line = None
        reference_indentation = 0
        
        # Look backwards from insertion point
        for i in range(insertion_point - 1, -1, -1):
            if i < len(context_lines):
                line_info = LineInfo.from_line(context_lines[i], i, self.comment_patterns)
                if not line_info.is_empty:
                    reference_line = context_lines[i]
                    reference_indentation = line_info.indentation
                    break
        
        # If no reference found, look forwards
        if reference_line is None:
            for i in range(insertion_point, len(context_lines)):
                if i < len(context_lines):
                    line_info = LineInfo.from_line(context_lines[i], i, self.comment_patterns)
                    if not line_info.is_empty:
                        reference_line = context_lines[i]
                        reference_indentation = line_info.indentation
                        break
        
        # Apply indentation to new lines
        if reference_line is not None:
            indent_str = reference_line[:reference_indentation]
            indented_new_lines = []
            
            for line in new_lines:
                if line.strip():  # Non-empty line
                    indented_new_lines.append(indent_str + line)
                else:
                    indented_new_lines.append('')  # Preserve empty lines
            
            return indented_new_lines
        
        return new_lines
    
    def calculate_line_similarity(self, line1: str, line2: str, 
                                ignore_whitespace: bool = True) -> float:
        """Calculate similarity between two lines (0.0 to 1.0)"""
        from difflib import SequenceMatcher
        
        if ignore_whitespace:
            line1_clean = line1.strip()
            line2_clean = line2.strip()
        else:
            line1_clean = line1
            line2_clean = line2
        
        if not line1_clean and not line2_clean:
            return 1.0  # Both empty
        
        matcher = SequenceMatcher(None, line1_clean, line2_clean)
        return matcher.ratio()
    
    def find_most_similar_line(self, target_line: str, candidate_lines: List[str], 
                             threshold: float = 0.7) -> Optional[Tuple[int, float]]:
        """Find the most similar line to target line"""
        best_match_index = -1
        best_similarity = 0.0
        
        for i, candidate in enumerate(candidate_lines):
            similarity = self.calculate_line_similarity(target_line, candidate)
            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_match_index = i
        
        if best_match_index >= 0:
            return best_match_index, best_similarity
        return None
    
    def align_blocks(self, original_block: List[str], modified_block: List[str]) -> List[Tuple[Optional[int], Optional[int]]]:
        """Align lines between original and modified blocks"""
        from difflib import SequenceMatcher
        
        # Create a mapping between original and modified lines
        matcher = SequenceMatcher(None, original_block, modified_block)
        alignment = []
        
        for opcode in matcher.get_opcodes():
            tag, i1, i2, j1, j2 = opcode
            
            if tag == 'equal':
                # Lines match
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    alignment.append((i, j))
            elif tag == 'replace':
                # Lines replaced
                for i in range(i1, i2):
                    alignment.append((i, None))
                for j in range(j1, j2):
                    alignment.append((None, j))
            elif tag == 'delete':
                # Lines deleted
                for i in range(i1, i2):
                    alignment.append((i, None))
            elif tag == 'insert':
                # Lines inserted
                for j in range(j1, j2):
                    alignment.append((None, j))
        
        return alignment


class IndentationDetector:
    """Advanced indentation detection and handling"""
    
    def __init__(self):
        self.common_indent_sizes = {2, 4, 8}  # Common indentation sizes
    
    def detect_indentation_level(self, line: str, base_indentation: int = 0) -> int:
        """Detect indentation level relative to base"""
        line_info = LineInfo.from_line(line, 0)
        if line_info.indentation <= base_indentation:
            return 0
        
        # Calculate level based on common sizes
        indent_diff = line_info.indentation - base_indentation
        for size in sorted(self.common_indent_sizes, reverse=True):
            if indent_diff % size == 0:
                return indent_diff // size
        
        # Fallback: round to nearest common size
        closest_size = min(self.common_indent_sizes, key=lambda x: abs(x - indent_diff))
        return round(indent_diff / closest_size)
    
    def normalize_indentation(self, lines: List[str], target_size: int = 4, 
                            style: str = "spaces") -> List[str]:
        """Normalize indentation to consistent size and style"""
        if not lines:
            return lines
        
        normalized = []
        indent_char = ' ' if style == "spaces" else '\t'
        
        for line in lines:
            line_info = LineInfo.from_line(line, 0)
            
            if line_info.is_empty:
                normalized.append('')
                continue
            
            # Calculate normalized indentation
            current_indent = line_info.indentation
            if current_indent > 0:
                # Convert to target indentation
                indent_level = max(1, round(current_indent / target_size))
                new_indent = indent_char * (indent_level * target_size)
            else:
                new_indent = ''
            
            normalized.append(new_indent + line_info.stripped)
        
        return normalized
    
    def detect_scope_changes(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Detect scope changes based on indentation"""
        scope_changes = []
        current_indentation = 0
        stack = [0]  # Stack of indentation levels
        
        for i, line in enumerate(lines):
            line_info = LineInfo.from_line(line, i + 1)
            
            if line_info.is_empty or line_info.is_comment:
                continue
            
            if line_info.indentation > current_indentation:
                # Indentation increased - new scope
                scope_changes.append({
                    'line': i + 1,
                    'type': 'scope_start',
                    'indentation': line_info.indentation,
                    'content': line_info.stripped
                })
                stack.append(line_info.indentation)
                current_indentation = line_info.indentation
            
            elif line_info.indentation < current_indentation:
                # Indentation decreased - scope ended
                while stack and stack[-1] > line_info.indentation:
                    popped_indent = stack.pop()
                    scope_changes.append({
                        'line': i + 1,
                        'type': 'scope_end',
                        'indentation': popped_indent,
                        'content': line_info.stripped
                    })
                
                if stack:
                    current_indentation = stack[-1]
                else:
                    current_indentation = 0
                    stack.append(0)
        
        return scope_changes


class BlockDetector:
    """Detect code blocks (functions, classes, control structures)"""
    
    def __init__(self):
        self.block_patterns = {
            'python': {
                'function': re.compile(r'^def\s+(\w+)\s*\('),
                'class': re.compile(r'^class\s+(\w+)'),
                'if': re.compile(r'^if\s+(.+):'),
                'for': re.compile(r'^for\s+(.+):'),
                'while': re.compile(r'^while\s+(.+):'),
                'with': re.compile(r'^with\s+(.+):'),
            },
            'zexus': {
                'function': re.compile(r'^fn\s+(\w+)\s*\('),
                'action': re.compile(r'^action\s+(\w+)'),
                'entity': re.compile(r'^entity\s+(\w+)'),
                'contract': re.compile(r'^contract\s+(\w+)'),
            }
        }
    
    def detect_blocks(self, lines: List[str], language: str = 'python') -> List[Dict[str, Any]]:
        """Detect code blocks in the file"""
        blocks = []
        patterns = self.block_patterns.get(language, self.block_patterns['python'])
        
        for i, line in enumerate(lines):
            line_info = LineInfo.from_line(line, i + 1)
            
            if line_info.is_empty or line_info.is_comment:
                continue
            
            # Check for block starters
            for block_type, pattern in patterns.items():
                match = pattern.match(line_info.stripped)
                if match:
                    blocks.append({
                        'type': block_type,
                        'name': match.group(1) if match.groups() else None,
                        'start_line': i + 1,
                        'content': line_info.stripped,
                        'indentation': line_info.indentation
                    })
                    break
        
        return blocks
    
    def find_block_by_name(self, blocks: List[Dict[str, Any]], name: str, 
                         block_type: str = None) -> Optional[Dict[str, Any]]:
        """Find a block by name and optional type"""
        for block in blocks:
            if block['name'] == name:
                if block_type is None or block['type'] == block_type:
                    return block
        return None
    
    def get_block_content(self, lines: List[str], block: Dict[str, Any], 
                         include_blank_lines: bool = True) -> List[str]:
        """Get the content of a block based on indentation"""
        start_line = block['start_line'] - 1  # Convert to 0-based
        base_indentation = block['indentation']
        block_lines = []
        
        # Start from the line after the block declaration
        i = start_line + 1
        while i < len(lines):
            line_info = LineInfo.from_line(lines[i], i + 1)
            
            # Check if we're still in the block
            if not line_info.is_empty and line_info.indentation <= base_indentation:
                break
            
            if include_blank_lines or not line_info.is_empty:
                block_lines.append(lines[i])
            
            i += 1
        
        return block_lines


# Example usage
if __name__ == "__main__":
    # Test line utilities
    line_utils = LineUtils()
    
    test_lines = [
        "    def hello():",
        "        print('hello')",
        "        return True",
        "",
        "    # This is a comment",
        "    def goodbye():",
        "        print('goodbye')"
    ]
    
    # Detect indentation
    style, size = line_utils.detect_indentation(test_lines)
    print(f"Indentation: {style}, size: {size}")
    
    # Normalize lines
    normalized = line_utils.normalize_lines(test_lines, preserve_empty=False)
    print(f"Normalized lines: {len(normalized)}")
    
    # Test block detection
    detector = BlockDetector()
    blocks = detector.detect_blocks(test_lines, 'python')
    print(f"Found {len(blocks)} blocks")
    for block in blocks:
        print(f"  {block['type']}: {block['name']} at line {block['start_line']}")
