#!/usr/bin/env python3
"""
Syntax Highlighter for Professional Patch Tool
Enhanced syntax highlighting with Pygments support
"""

import re
from typing import List, Dict, Any, Optional

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.formatters import TerminalFormatter, Terminal256Formatter
    from pygments.style import Style
    from pygments.token import Token
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False


class SyntaxHighlighter:
    """Advanced syntax highlighting with fallback to basic highlighting"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.pygments_available = PYGMENTS_AVAILABLE
        self.styles = self._initialize_styles()

    def _initialize_styles(self) -> Dict[str, Any]:
        """Initialize highlighting styles"""
        return {
            'basic': {
                'keywords': {'color': '\033[95m', 'reset': '\033[0m'},
                'strings': {'color': '\033[92m', 'reset': '\033[0m'},
                'comments': {'color': '\033[90m', 'reset': '\033[0m'},
                'numbers': {'color': '\033[93m', 'reset': '\033[0m'},
                'functions': {'color': '\033[96m', 'reset': '\033[0m'}
            }
        }

    def highlight_line(self, line: str, language: str) -> str:
        """Highlight a single line of code"""
        if not self.config_manager.get('enable_syntax_hints', True):
            return line
            
        if self.pygments_available and self.config_manager.get('use_advanced_highlighting', False):
            return self._highlight_with_pygments(line, language)
        else:
            return self._highlight_basic(line, language)

    def _highlight_with_pygments(self, line: str, language: str) -> str:
        """Highlight using Pygments (if available)"""
        try:
            # Get appropriate lexer
            if language == 'auto':
                lexer = guess_lexer(line)
            else:
                lexer = get_lexer_by_name(language, stripall=True)
            
            # Use 256-color formatter for better colors
            formatter = Terminal256Formatter(style='default')
            
            # Highlight the line
            highlighted = highlight(line, lexer, formatter)
            return highlighted.strip()
            
        except Exception:
            # Fall back to basic highlighting if Pygments fails
            return self._highlight_basic(line, language)

    def _highlight_basic(self, line: str, language: str) -> str:
        """Basic syntax highlighting using regex patterns"""
        if language == 'python':
            return self._highlight_python(line)
        elif language == 'zexus':
            return self._highlight_zexus(line)
        elif language in ['javascript', 'typescript']:
            return self._highlight_javascript(line)
        elif language == 'java':
            return self._highlight_java(line)
        elif language in ['cpp', 'c']:
            return self._highlight_cpp(line)
        elif language == 'html':
            return self._highlight_html(line)
        elif language == 'css':
            return self._highlight_css(line)
        else:
            return line

    def _highlight_python(self, line: str) -> str:
        """Highlight Python code"""
        styles = self.styles['basic']
        
        # Keywords
        keywords = [
            'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'return', 
            'import', 'from', 'as', 'with', 'try', 'except', 'finally', 
            'raise', 'assert', 'pass', 'break', 'continue', 'del', 
            'global', 'nonlocal', 'lambda', 'yield', 'async', 'await'
        ]
        
        for kw in keywords:
            line = re.sub(rf'\b{kw}\b', f"{styles['keywords']['color']}{kw}{styles['keywords']['reset']}", line)
        
        # Strings (simple detection)
        line = re.sub(r'(\".*?\"|\'.*?\')', f"{styles['strings']['color']}\\1{styles['strings']['reset']}", line)
        
        # Comments
        line = re.sub(r'(#.*)$', f"{styles['comments']['color']}\\1{styles['comments']['reset']}", line)
        
        # Numbers
        line = re.sub(r'\b(\d+\.?\d*|\.\d+)\b', f"{styles['numbers']['color']}\\1{styles['numbers']['reset']}", line)
        
        # Function calls (basic)
        line = re.sub(r'\b(\w+)\s*\(', f"{styles['functions']['color']}\\1{styles['functions']['reset']}(", line)
        
        return line

    def _highlight_zexus(self, line: str) -> str:
        """Highlight Zexus code"""
        styles = self.styles['basic']
        
        # Zexus keywords
        keywords = [
            'action', 'entity', 'contract', 'export', 'use', 'let', 'if', 
            'else', 'for', 'while', 'return', 'fn', 'struct', 'enum', 
            'impl', 'trait', 'pub', 'mut', 'const'
        ]
        
        for kw in keywords:
            line = re.sub(rf'\b{kw}\b', f"{styles['keywords']['color']}{kw}{styles['keywords']['reset']}", line)
        
        # Strings
        line = re.sub(r'(\".*?\"|\'.*?\')', f"{styles['strings']['color']}\\1{styles['strings']['reset']}", line)
        
        # Comments
        line = re.sub(r'(//.*|/\*.*?\*/)', f"{styles['comments']['color']}\\1{styles['comments']['reset']}", line)
        
        return line

    def _highlight_javascript(self, line: str) -> str:
        """Highlight JavaScript/TypeScript code"""
        styles = self.styles['basic']
        
        keywords = [
            'function', 'var', 'let', 'const', 'if', 'else', 'for', 'while',
            'return', 'class', 'extends', 'import', 'export', 'from', 'default',
            'async', 'await', 'try', 'catch', 'finally', 'throw', 'new', 'this'
        ]
        
        for kw in keywords:
            line = re.sub(rf'\b{kw}\b', f"{styles['keywords']['color']}{kw}{styles['keywords']['reset']}", line)
        
        # Strings
        line = re.sub(r'(\".*?\"|\'.*?\'|`.*?`)', f"{styles['strings']['color']}\\1{styles['strings']['reset']}", line)
        
        # Comments
        line = re.sub(r'(//.*|/\*.*?\*/)', f"{styles['comments']['color']}\\1{styles['comments']['reset']}", line)
        
        return line

    def _highlight_java(self, line: str) -> str:
        """Highlight Java code"""
        styles = self.styles['basic']
        
        keywords = [
            'class', 'public', 'private', 'protected', 'static', 'void', 'int',
            'String', 'boolean', 'if', 'else', 'for', 'while', 'return', 'new',
            'this', 'extends', 'implements', 'interface', 'package', 'import'
        ]
        
        for kw in keywords:
            line = re.sub(rf'\b{kw}\b', f"{styles['keywords']['color']}{kw}{styles['keywords']['reset']}", line)
        
        # Strings
        line = re.sub(r'(\".*?\")', f"{styles['strings']['color']}\\1{styles['strings']['reset']}", line)
        
        # Comments
        line = re.sub(r'(//.*|/\*.*?\*/)', f"{styles['comments']['color']}\\1{styles['comments']['reset']}", line)
        
        return line

    def _highlight_cpp(self, line: str) -> str:
        """Highlight C/C++ code"""
        styles = self.styles['basic']
        
        keywords = [
            'include', 'define', 'ifdef', 'ifndef', 'endif', 'class', 'struct',
            'public', 'private', 'protected', 'virtual', 'override', 'template',
            'typename', 'namespace', 'using', 'auto', 'const', 'static', 'void',
            'int', 'char', 'float', 'double', 'bool', 'if', 'else', 'for', 'while',
            'return', 'new', 'delete', 'this'
        ]
        
        for kw in keywords:
            line = re.sub(rf'\b{kw}\b', f"{styles['keywords']['color']}{kw}{styles['keywords']['reset']}", line)
        
        # Strings
        line = re.sub(r'(\".*?\")', f"{styles['strings']['color']}\\1{styles['strings']['reset']}", line)
        
        # Comments
        line = re.sub(r'(//.*|/\*.*?\*/)', f"{styles['comments']['color']}\\1{styles['comments']['reset']}", line)
        
        return line

    def _highlight_html(self, line: str) -> str:
        """Highlight HTML code"""
        styles = self.styles['basic']
        
        # Tags
        line = re.sub(r'(&lt;/?\w+&gt;?)', f"{styles['keywords']['color']}\\1{styles['keywords']['reset']}", line)
        
        # Attributes
        line = re.sub(r'(\w+)=', f"{styles['functions']['color']}\\1{styles['functions']['reset']}=", line)
        
        # Strings
        line = re.sub(r'(\".*?\")', f"{styles['strings']['color']}\\1{styles['strings']['reset']}", line)
        
        # Comments
        line = re.sub(r'(<!--.*?-->)', f"{styles['comments']['color']}\\1{styles['comments']['reset']}", line)
        
        return line

    def _highlight_css(self, line: str) -> str:
        """Highlight CSS code"""
        styles = self.styles['basic']
        
        # Properties
        line = re.sub(r'(\w+)\s*:', f"{styles['keywords']['color']}\\1{styles['keywords']['reset']}:", line)
        
        # Values
        line = re.sub(r':\s*([^;]+);', f": {styles['strings']['color']}\\1{styles['strings']['reset']};", line)
        
        # Selectors
        line = re.sub(r'([.#]?\w+)\s*{', f"{styles['functions']['color']}\\1{styles['functions']['reset']}{{", line)
        
        # Comments
        line = re.sub(r'(/\*.*?\*/)', f"{styles['comments']['color']}\\1{styles['comments']['reset']}", line)
        
        return line

    def highlight_multiple_lines(self, lines: List[str], language: str) -> List[str]:
        """Highlight multiple lines of code"""
        return [self.highlight_line(line, language) for line in lines]

    def detect_language(self, filename: str, content: str = "") -> str:
        """Detect programming language from filename and content"""
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
        
        ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        return ext_map.get(ext, 'text')

    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return [
            'python', 'zexus', 'javascript', 'typescript', 'java',
            'cpp', 'c', 'html', 'css', 'markdown', 'json', 'xml',
            'yaml', 'sql', 'bash', 'php', 'ruby', 'go', 'rust'
        ]

    def enable_advanced_highlighting(self, enable: bool = True):
        """Enable or disable advanced Pygments highlighting"""
        if enable and not self.pygments_available:
            print("⚠️  Pygments not available. Using basic highlighting.")
            return False
            
        self.config_manager.set('use_advanced_highlighting', enable)
        return True
