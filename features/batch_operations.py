#!/usr/bin/env python3
"""
Batch Operations for Professional Patch Tool
Multi-file operations and bulk processing
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


class BatchOperations:
    """Handles batch operations across multiple files"""
    
    def __init__(self, patch_engine, file_manager):
        self.patch_engine = patch_engine
        self.file_manager = file_manager
        self.batch_history = []

    def interactive_batch_menu(self):
        """Interactive menu for batch operations"""
        while True:
            print(f"\n🔀 BATCH OPERATIONS")
            print("=" * 60)
            print("1. 📁 Find and replace across files")
            print("2. 🔍 Search patterns in directory")
            print("3. 🎯 Apply patch to multiple files")
            print("4. 📊 Batch analysis")
            print("5. 📋 Batch operation history")
            print("0. ↩️  Back to main menu")
            print("=" * 60)
            
            try:
                choice = input("\nSelect operation: ").strip()
                
                if choice == '1':
                    self._batch_find_replace()
                elif choice == '2':
                    self._batch_search()
                elif choice == '3':
                    self._batch_apply_patch()
                elif choice == '4':
                    self._batch_analysis()
                elif choice == '5':
                    self._show_batch_history()
                elif choice == '0':
                    break
                else:
                    print("❌ Invalid choice")
                    
            except KeyboardInterrupt:
                print("\n⏹️  Operation cancelled.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def _batch_find_replace(self):
        """Batch find and replace across multiple files"""
        print(f"\n📁 BATCH FIND & REPLACE")
        
        # Get search parameters
        search_pattern = input("Search pattern (regex): ").strip()
        if not search_pattern:
            print("❌ Search pattern is required")
            return
            
        replacement = input("Replacement: ").strip()
        
        # Get file patterns
        file_patterns_input = input("File patterns (comma-separated) [**/*.py]: ").strip()
        file_patterns = [p.strip() for p in file_patterns_input.split(',')] if file_patterns_input else ['**/*.py']
        
        # Get target directory
        target_dir = input(f"Search directory [{self.file_manager.base_path}]: ").strip()
        target_dir = target_dir or self.file_manager.base_path
        
        # Find matching files
        matching_files = self._find_files_by_patterns(file_patterns, target_dir)
        
        if not matching_files:
            print("❌ No files found matching the patterns")
            return
            
        print(f"\n🔍 Found {len(matching_files)} files:")
        for i, file_path in enumerate(matching_files[:10], 1):
            print(f"  {i}. {file_path}")
        if len(matching_files) > 10:
            print(f"  ... and {len(matching_files) - 10} more")
            
        # Preview matches
        print(f"\n🔍 Previewing matches...")
        preview_results = self._preview_batch_changes(matching_files, search_pattern, replacement)
        
        total_matches = sum(len(files) for files in preview_results.values())
        if total_matches == 0:
            print("❌ No matches found for the search pattern")
            return
            
        print(f"📊 Found {total_matches} total matches across {len(preview_results)} files")
        
        # Confirm application
        confirm = input("\n✅ Apply changes? (y/n): ").lower()
        if confirm != 'y':
            print("❌ Batch operation cancelled")
            return
            
        # Apply changes
        print(f"\n🔄 Applying changes...")
        results = self._apply_batch_find_replace(matching_files, search_pattern, replacement)
        
        # Show results
        self._show_batch_results(results)
        
        # Record operation
        self.batch_history.append({
            'type': 'batch_find_replace',
            'timestamp': self._get_timestamp(),
            'pattern': search_pattern,
            'replacement': replacement,
            'files_processed': len(results),
            'changes_applied': sum(r['changes_applied'] for r in results),
            'total_files': len(matching_files)
        })

    def _batch_search(self):
        """Search for patterns across multiple files"""
        print(f"\n🔍 BATCH SEARCH")
        
        search_pattern = input("Search pattern (regex): ").strip()
        if not search_pattern:
            print("❌ Search pattern is required")
            return
            
        file_patterns_input = input("File patterns (comma-separated) [**/*]: ").strip()
        file_patterns = [p.strip() for p in file_patterns_input.split(',')] if file_patterns_input else ['**/*']
        
        target_dir = input(f"Search directory [{self.file_manager.base_path}]: ").strip()
        target_dir = target_dir or self.file_manager.base_path
        
        print(f"\n🔍 Searching...")
        
        matching_files = self._find_files_by_patterns(file_patterns, target_dir)
        results = []
        
        for file_path in matching_files:
            file_info = self.file_manager.get_file_info(file_path)
            if file_info:
                matches = self.patch_engine.find_code_blocks(file_info, search_pattern)
                if matches:
                    results.append({
                        'file': file_path,
                        'matches': matches
                    })
        
        # Display results
        if results:
            print(f"\n📊 Found {sum(len(r['matches']) for r in results)} matches in {len(results)} files:")
            for result in results[:20]:  # Limit display
                print(f"\n📄 {result['file']}:")
                for match in result['matches'][:5]:  # Limit matches per file
                    print(f"  📍 Line {match['line_number']}: {match['full_match'][:100]}")
                if len(result['matches']) > 5:
                    print(f"  ... and {len(result['matches']) - 5} more matches")
        else:
            print("❌ No matches found")

    def _batch_apply_patch(self):
        """Apply the same patch to multiple files"""
        print(f"\n🎯 BATCH PATCH APPLICATION")
        
        # Get patch definition
        print("Define the patch to apply:")
        patch_type = input("Patch type (insert_at_line/replace_range/replace_pattern/append) [replace_pattern]: ").strip() or "replace_pattern"
        
        patch_config = {'type': patch_type}
        
        if patch_type == 'insert_at_line':
            patch_config['line_number'] = int(input("Line number: "))
        elif patch_type == 'replace_range':
            patch_config['start_line'] = int(input("Start line: "))
            patch_config['end_line'] = int(input("End line: "))
        elif patch_type in ['replace_pattern', 'insert_after', 'insert_before']:
            patch_config['pattern'] = input("Pattern (regex): ").strip()
            
        patch_config['code'] = self._get_multiline_input("Code (empty line to finish): ")
        patch_config['description'] = input("Patch description: ").strip() or "Batch patch"
        
        # Get target files
        file_patterns_input = input("File patterns (comma-separated) [**/*.py]: ").strip()
        file_patterns = [p.strip() for p in file_patterns_input.split(',')] if file_patterns_input else ['**/*.py']
        
        target_dir = input(f"Target directory [{self.file_manager.base_path}]: ").strip()
        target_dir = target_dir or self.file_manager.base_path
        
        matching_files = self._find_files_by_patterns(file_patterns, target_dir)
        
        if not matching_files:
            print("❌ No files found matching the patterns")
            return
            
        print(f"\n📄 Found {len(matching_files)} files")
        
        # Preview
        print(f"\n🔍 Previewing changes...")
        preview_success = 0
        for file_path in matching_files[:5]:  # Preview first 5
            file_info = self.file_manager.get_file_info(file_path)
            if file_info:
                valid, message = self.patch_engine.validate_patch(patch_config, file_info)
                if valid:
                    preview_success += 1
                    print(f"  ✅ {file_path}: Can be patched")
                else:
                    print(f"  ❌ {file_path}: {message}")
        
        if preview_success == 0:
            print("❌ No files can be patched with the current configuration")
            return
            
        # Confirm
        confirm = input(f"\n✅ Apply patch to {len(matching_files)} files? (y/n): ").lower()
        if confirm != 'y':
            print("❌ Batch patch cancelled")
            return
            
        # Apply
        print(f"\n🔄 Applying patch...")
        results = []
        
        for file_path in matching_files:
            success, result = self.patch_engine.apply_patches(file_path, [patch_config])
            results.append({
                'file': file_path,
                'success': success,
                'result': result
            })
        
        # Show results
        successful = sum(1 for r in results if r['success'])
        print(f"\n📊 Batch patch completed: {successful}/{len(results)} files updated")
        
        # Record operation
        self.batch_history.append({
            'type': 'batch_patch',
            'timestamp': self._get_timestamp(),
            'patch_type': patch_type,
            'files_processed': len(results),
            'successful': successful,
            'total_files': len(matching_files)
        })

    def _batch_analysis(self):
        """Analyze multiple files for patterns and statistics"""
        print(f"\n📊 BATCH ANALYSIS")
        
        file_patterns_input = input("File patterns (comma-separated) [**/*.py]: ").strip()
        file_patterns = [p.strip() for p in file_patterns_input.split(',')] if file_patterns_input else ['**/*.py']
        
        target_dir = input(f"Analysis directory [{self.file_manager.base_path}]: ").strip()
        target_dir = target_dir or self.file_manager.base_path
        
        analysis_patterns_input = input("Analysis patterns (comma-separated, e.g., 'TODO,FIXME') [optional]: ").strip()
        analysis_patterns = [p.strip() for p in analysis_patterns_input.split(',')] if analysis_patterns_input else []
        
        print(f"\n🔍 Analyzing files...")
        
        matching_files = self._find_files_by_patterns(file_patterns, target_dir)
        
        if not matching_files:
            print("❌ No files found matching the patterns")
            return
            
        # Collect statistics
        stats = {
            'total_files': len(matching_files),
            'total_lines': 0,
            'total_size': 0,
            'by_extension': {},
            'pattern_matches': {pattern: 0 for pattern in analysis_patterns}
        }
        
        for file_path in matching_files:
            file_info = self.file_manager.get_file_info(file_path)
            if file_info:
                stats['total_lines'] += file_info['lines']
                stats['total_size'] += file_info['size']
                
                # Count by extension
                ext = file_info['extension']
                stats['by_extension'][ext] = stats['by_extension'].get(ext, 0) + 1
                
                # Count pattern matches
                for pattern in analysis_patterns:
                    matches = self.patch_engine.find_code_blocks(file_info, pattern)
                    stats['pattern_matches'][pattern] += len(matches)
        
        # Display results
        print(f"\n📊 ANALYSIS RESULTS")
        print(f"📁 Files analyzed: {stats['total_files']}")
        print(f"📄 Total lines: {stats['total_lines']:,}")
        print(f"💾 Total size: {self._format_size(stats['total_size'])}")
        
        if stats['by_extension']:
            print(f"\n📁 Files by extension:")
            for ext, count in sorted(stats['by_extension'].items()):
                print(f"  {ext or 'no extension'}: {count} files")
                
        if analysis_patterns:
            print(f"\n🔍 Pattern matches:")
            for pattern, count in stats['pattern_matches'].items():
                print(f"  '{pattern}': {count} matches")

    def _find_files_by_patterns(self, patterns: List[str], base_dir: str) -> List[str]:
        """Find files matching the given patterns"""
        matching_files = []
        base_dir = self.file_manager.resolve_path(base_dir)
        
        for pattern in patterns:
            for root, dirs, files in os.walk(base_dir):
                # Filter hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.file_manager.base_path)
                    
                    if any(fnmatch.fnmatch(rel_path, pattern) for pattern in patterns):
                        matching_files.append(rel_path)
                        
        return list(set(matching_files))  # Remove duplicates

    def _preview_batch_changes(self, files: List[str], search_pattern: str, replacement: str) -> Dict[str, List]:
        """Preview changes without applying them"""
        preview_results = {}
        
        for file_path in files[:50]:  # Limit preview to 50 files
            file_info = self.file_manager.get_file_info(file_path)
            if file_info:
                matches = self.patch_engine.find_code_blocks(file_info, search_pattern)
                if matches:
                    preview_results[file_path] = matches
                    
        return preview_results

    def _apply_batch_find_replace(self, files: List[str], search_pattern: str, replacement: str) -> List[Dict]:
        """Apply find and replace to multiple files"""
        results = []
        replacement_lines = replacement.split('\n') if '\n' in replacement else [replacement]
        
        for file_path in files:
            patches = [{
                'type': 'replace_pattern_all',
                'pattern': search_pattern,
                'code': replacement_lines,
                'description': f'Batch find/replace: {search_pattern}'
            }]
            
            success, result = self.patch_engine.apply_patches(file_path, patches)
            results.append({
                'file': file_path,
                'success': success,
                'changes_applied': result.get('successful_patches', 0) if success else 0,
                'result': result
            })
            
        return results

    def _show_batch_results(self, results: List[Dict]):
        """Display batch operation results"""
        successful = sum(1 for r in results if r['success'])
        total_changes = sum(r['changes_applied'] for r in results if r['success'])
        
        print(f"\n📊 BATCH OPERATION COMPLETED")
        print(f"✅ Successful: {successful}/{len(results)} files")
        print(f"🔧 Changes applied: {total_changes} total")
        
        # Show failed files if any
        failed_files = [r for r in results if not r['success']]
        if failed_files:
            print(f"\n❌ Failed files:")
            for failed in failed_files[:10]:
                print(f"  • {failed['file']}")

    def _show_batch_history(self):
        """Show history of batch operations"""
        if not self.batch_history:
            print("❌ No batch operation history")
            return
            
        print(f"\n📋 BATCH OPERATION HISTORY")
        for operation in self.batch_history[-10:]:  # Show last 10
            print(f"\n⏰ {operation['timestamp']}")
            print(f"📝 Type: {operation['type']}")
            print(f"📊 Results: {operation.get('files_processed', 0)} files processed")
            if 'changes_applied' in operation:
                print(f"🔧 Changes: {operation['changes_applied']} applied")
            if 'successful' in operation:
                print(f"✅ Successful: {operation['successful']} files")

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def _get_multiline_input(self, prompt: str) -> List[str]:
        """Get multiline input from user"""
        print(prompt)
        lines = []
        while True:
            line = input().strip()
            if not line:
                break
            lines.append(line)
        return lines
