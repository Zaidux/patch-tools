#!/usr/bin/env python3
"""
Advanced Regex Utilities for Professional Patch Tool
Multi-line pattern matching, fuzzy matching, and regex building
"""

import re
import difflib
from typing import List, Dict, Any, Optional, Tuple, Pattern, Callable
from functools import lru_cache


class RegexUtils:
    """Advanced regex utilities with caching and validation"""
    
    def __init__(self):
        self.regex_cache = {}
        self.compilation_stats = {'hits': 0, 'misses': 0, 'errors': 0}
        
    @lru_cache(maxsize=1000)
    def compile_regex(self, pattern: str, flags: int = 0) -> Optional[Pattern]:
        """Compile regex with caching and error handling"""
        cache_key = f"{pattern}|{flags}"
        
        if cache_key in self.regex_cache:
            self.compilation_stats['hits'] += 1
            return self.regex_cache[cache_key]
        
        try:
            compiled = re.compile(pattern, flags)
            self.regex_cache[cache_key] = compiled
            self.compilation_stats['misses'] += 1
            return compiled
        except re.error as e:
            self.compilation_stats['errors'] += 1
            print(f"❌ Regex compilation error: {e}")
            return None
    
    def validate_regex(self, pattern: str) -> Tuple[bool, str]:
        """Validate regex pattern and return error message if invalid"""
        try:
            re.compile(pattern)
            return True, "Valid regex pattern"
        except re.error as e:
            return False, f"Invalid regex: {e}"
    
    def test_regex(self, pattern: str, test_strings: List[str]) -> Dict[str, Any]:
        """Test regex pattern against multiple test strings"""
        result = {
            'pattern': pattern,
            'is_valid': False,
            'error': None,
            'test_results': [],
            'summary': {}
        }
        
        # Validate pattern first
        is_valid, error = self.validate_regex(pattern)
        result['is_valid'] = is_valid
        result['error'] = error
        
        if not is_valid:
            return result
        
        # Test against each string
        compiled = self.compile_regex(pattern)
        if not compiled:
            return result
        
        matches_count = 0
        groups_count = 0
        
        for test_str in test_strings:
            test_result = {
                'test_string': test_str,
                'matches': False,
                'match_text': None,
                'groups': [],
                'start_end': None
            }
            
            match = compiled.search(test_str)
            if match:
                test_result['matches'] = True
                test_result['match_text'] = match.group()
                test_result['groups'] = list(match.groups())
                test_result['start_end'] = (match.start(), match.end())
                matches_count += 1
                groups_count += len(match.groups())
            
            result['test_results'].append(test_result)
        
        # Summary
        result['summary'] = {
            'total_tests': len(test_strings),
            'matches_found': matches_count,
            'total_groups': groups_count,
            'success_rate': matches_count / len(test_strings) if test_strings else 0
        }
        
        return result
    
    def build_regex_from_patterns(self, patterns: List[str], join_with: str = '|') -> str:
        """Build a combined regex from multiple patterns"""
        validated_patterns = []
        
        for pattern in patterns:
            if self.validate_regex(pattern)[0]:
                validated_patterns.append(pattern)
            else:
                print(f"⚠️  Skipping invalid pattern: {pattern}")
        
        if not validated_patterns:
            return ""
        
        if len(validated_patterns) == 1:
            return validated_patterns[0]
        
        return f"(?:{join_with.join(validated_patterns)})"
    
    def escape_for_regex(self, text: str) -> str:
        """Escape text for safe use in regex patterns"""
        return re.escape(text)
    
    def create_word_boundary_regex(self, word: str) -> str:
        """Create regex that matches whole word with boundaries"""
        return rf"\b{re.escape(word)}\b"
    
    def create_flexible_pattern(self, text: str, allow_variations: bool = True) -> str:
        """Create a flexible pattern that handles common variations"""
        # Escape the base text
        base_pattern = re.escape(text)
        
        if not allow_variations:
            return base_pattern
        
        # Common variations to handle
        variations = {
            r'\s+': r'\\s+',  # Multiple spaces
            r'\(\s*': r'\\(\\s*',  # Spaces after opening paren
            r'\s*\)': r'\\s*\\)',  # Spaces before closing paren
            r'=\s*': r'=\\s*',  # Spaces after equals
            r'\s*=': r'\\s*=',  # Spaces before equals
        }
        
        # Apply variations
        flexible_pattern = base_pattern
        for find, replace in variations.items():
            flexible_pattern = flexible_pattern.replace(find, replace)
        
        return flexible_pattern
    
    def get_compilation_stats(self) -> Dict[str, int]:
        """Get regex compilation statistics"""
        return self.compilation_stats.copy()
    
    def clear_cache(self):
        """Clear the regex cache"""
        self.regex_cache.clear()
        self.compile_regex.cache_clear()
        self.compilation_stats = {'hits': 0, 'misses': 0, 'errors': 0}


class FuzzyMatcher:
    """Fuzzy matching using Levenshtein distance and similarity"""
    
    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold
        self.matcher = difflib.SequenceMatcher()
    
    def similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings (0.0 to 1.0)"""
        self.matcher.set_seqs(a.lower(), b.lower())
        return self.matcher.ratio()
    
    def is_similar(self, a: str, b: str, threshold: float = None) -> bool:
        """Check if two strings are similar above threshold"""
        if threshold is None:
            threshold = self.threshold
        return self.similarity(a, b) >= threshold
    
    def find_best_match(self, target: str, candidates: List[str], threshold: float = None) -> Optional[Tuple[str, float]]:
        """Find the best matching candidate for target string"""
        if threshold is None:
            threshold = self.threshold
        
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            score = self.similarity(target, candidate)
            if score > best_score and score >= threshold:
                best_score = score
                best_match = candidate
        
        if best_match:
            return best_match, best_score
        return None
    
    def find_all_matches(self, target: str, candidates: List[str], threshold: float = None) -> List[Tuple[str, float]]:
        """Find all candidates that match above threshold"""
        if threshold is None:
            threshold = self.threshold
        
        matches = []
        for candidate in candidates:
            score = self.similarity(target, candidate)
            if score >= threshold:
                matches.append((candidate, score))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def fuzzy_search(self, pattern: str, texts: List[str], threshold: float = None) -> List[Tuple[str, float, int]]:
        """Fuzzy search for pattern in list of texts"""
        if threshold is None:
            threshold = self.threshold
        
        results = []
        for i, text in enumerate(texts):
            score = self.similarity(pattern, text)
            if score >= threshold:
                results.append((text, score, i))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def set_threshold(self, threshold: float):
        """Set the default similarity threshold"""
        if 0.0 <= threshold <= 1.0:
            self.threshold = threshold
        else:
            raise ValueError("Threshold must be between 0.0 and 1.0")


class MultiLineMatcher:
    """Advanced multi-line pattern matching"""
    
    def __init__(self, regex_utils: RegexUtils = None):
        self.regex_utils = regex_utils or RegexUtils()
        self.line_joiner = "\n"  # Default line joiner
    
    def set_line_joiner(self, joiner: str):
        """Set the string used to join lines for multi-line matching"""
        self.line_joiner = joiner
    
    def find_multiline_matches(self, lines: List[str], pattern: str, 
                             context_lines: int = 0) -> List[Dict[str, Any]]:
        """Find multi-line patterns in a list of lines"""
        # Join lines for multi-line matching
        full_text = self.line_joiner.join(lines)
        
        compiled = self.regex_utils.compile_regex(pattern, re.MULTILINE | re.DOTALL)
        if not compiled:
            return []
        
        matches = []
        for match in compiled.finditer(full_text):
            start_pos = match.start()
            end_pos = match.end()
            
            # Convert positions to line numbers
            start_line = self._position_to_line_number(full_text, start_pos)
            end_line = self._position_to_line_number(full_text, end_pos)
            
            # Get context
            context_start = max(0, start_line - context_lines)
            context_end = min(len(lines), end_line + context_lines)
            
            matches.append({
                'start_line': start_line + 1,  # Convert to 1-based
                'end_line': end_line + 1,
                'match_text': match.group(),
                'groups': match.groups(),
                'context_start': context_start + 1,
                'context_end': context_end + 1,
                'full_match': lines[start_line] if start_line < len(lines) else ""
            })
        
        return matches
    
    def _position_to_line_number(self, text: str, position: int) -> int:
        """Convert character position to line number (0-based)"""
        if position < 0 or position > len(text):
            return 0
        
        # Count newlines before position
        return text[:position].count(self.line_joiner)
    
    def find_code_blocks(self, lines: List[str], start_pattern: str, 
                        end_pattern: str, inclusive: bool = True) -> List[Dict[str, Any]]:
        """Find code blocks between start and end patterns"""
        blocks = []
        i = 0
        
        while i < len(lines):
            # Find start pattern
            start_match = self.regex_utils.compile_regex(start_pattern)
            if not start_match:
                break
            
            # Search for start pattern from current position
            start_found = False
            start_line = i
            
            for j in range(i, len(lines)):
                if start_match.search(lines[j]):
                    start_line = j
                    start_found = True
                    break
            
            if not start_found:
                break
            
            # Find end pattern
            end_match = self.regex_utils.compile_regex(end_pattern)
            if not end_match:
                break
            
            # Search for end pattern after start
            end_found = False
            end_line = start_line
            
            for k in range(start_line + 1, len(lines)):
                if end_match.search(lines[k]):
                    end_line = k
                    end_found = True
                    break
            
            if not end_found:
                break
            
            # Extract block
            if inclusive:
                block_lines = lines[start_line:end_line + 1]
            else:
                block_lines = lines[start_line + 1:end_line]
            
            blocks.append({
                'start_line': start_line + 1,
                'end_line': end_line + 1,
                'lines': block_lines,
                'content': self.line_joiner.join(block_lines)
            })
            
            # Continue search after this block
            i = end_line + 1
        
        return blocks
    
    def match_indented_blocks(self, lines: List[str], base_indentation: int = 0) -> List[Dict[str, Any]]:
        """Find indented code blocks (useful for Python, YAML, etc.)"""
        blocks = []
        current_block = None
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:  # Skip empty lines
                continue
            
            # Calculate indentation
            indentation = len(line) - len(line.lstrip())
            
            if indentation > base_indentation:
                # Continuing or starting a block
                if current_block is None:
                    # Start new block
                    current_block = {
                        'start_line': i + 1,
                        'end_line': i + 1,
                        'indentation': indentation,
                        'lines': [line],
                        'content': line_stripped
                    }
                else:
                    # Continue current block
                    current_block['end_line'] = i + 1
                    current_block['lines'].append(line)
                    current_block['content'] += "\n" + line_stripped
            else:
                # End current block if any
                if current_block is not None:
                    blocks.append(current_block)
                    current_block = None
        
        # Don't forget the last block
        if current_block is not None:
            blocks.append(current_block)
        
        return blocks
    
    def create_multiline_pattern(self, lines: List[str], flexible: bool = True) -> str:
        """Create a multi-line regex pattern from example lines"""
        if not lines:
            return ""
        
        # Escape each line and join with newlines
        escaped_lines = []
        for line in lines:
            if flexible:
                escaped_line = self.regex_utils.create_flexible_pattern(line)
            else:
                escaped_line = self.regex_utils.escape_for_regex(line)
            escaped_lines.append(escaped_line)
        
        # Join with newlines and make dot match newlines
        pattern = "\n".join(escaped_lines)
        return pattern


class RegexBuilder:
    """Utility class for building complex regex patterns"""
    
    @staticmethod
    def word(pattern: str) -> str:
        """Wrap pattern in word boundaries"""
        return rf"\b{pattern}\b"
    
    @staticmethod
    def group(pattern: str, name: str = None) -> str:
        """Wrap pattern in capturing group"""
        if name:
            return rf"(?P<{name}>{pattern})"
        return f"({pattern})"
    
    @staticmethod
    def non_capturing_group(pattern: str) -> str:
        """Wrap pattern in non-capturing group"""
        return f"(?:{pattern})"
    
    @staticmethod
    def optional(pattern: str) -> str:
        """Make pattern optional"""
        return f"{pattern}?"
    
    @staticmethod
    def zero_or_more(pattern: str) -> str:
        """Zero or more occurrences"""
        return f"{pattern}*"
    
    @staticmethod
    def one_or_more(pattern: str) -> str:
        """One or more occurrences"""
        return f"{pattern}+"
    
    @staticmethod
    def exactly_n(pattern: str, n: int) -> str:
        """Exactly n occurrences"""
        return f"{pattern}{{{n}}}"
    
    @staticmethod
    def between_n_m(pattern: str, n: int, m: int) -> str:
        """Between n and m occurrences"""
        return f"{pattern}{{{n},{m}}}"
    
    @staticmethod
    def either(*patterns: str) -> str:
        """Match any of the patterns"""
        return f"(?:{'|'.join(patterns)})"
    
    @staticmethod
    def lookahead(pattern: str) -> str:
        """Positive lookahead"""
        return f"(?={pattern})"
    
    @staticmethod
    def negative_lookahead(pattern: str) -> str:
        """Negative lookahead"""
        return f"(?!{pattern})"
    
    @staticmethod
    def lookbehind(pattern: str) -> str:
        """Positive lookbehind"""
        return f"(?<={pattern})"
    
    @staticmethod
    def negative_lookbehind(pattern: str) -> str:
        """Negative lookbehind"""
        return f"(?<!{pattern})"
    
    @staticmethod
    def build_pattern(*components: str) -> str:
        """Build a pattern from multiple components"""
        return "".join(components)


# Example usage and testing
if __name__ == "__main__":
    # Test the regex utilities
    regex_utils = RegexUtils()
    
    # Test pattern validation
    test_pattern = r"\d{3}-\d{2}-\d{4}"
    is_valid, message = regex_utils.validate_regex(test_pattern)
    print(f"Pattern validation: {is_valid}, {message}")
    
    # Test fuzzy matching
    fuzzy = FuzzyMatcher(threshold=0.7)
    candidates = ["hello world", "hello there", "goodbye world", "hell world"]
    target = "hello world"
    
    best_match = fuzzy.find_best_match(target, candidates)
    print(f"Best match for '{target}': {best_match}")
    
    # Test multi-line matching
    multi_line = MultiLineMatcher(regex_utils)
    lines = [
        "def hello():",
        "    print('hello')",
        "    return True",
        "",
        "def goodbye():", 
        "    print('goodbye')"
    ]
    
    blocks = multi_line.find_code_blocks(lines, r"def\s+\w+", r"return|$")
    print(f"Found {len(blocks)} code blocks")
