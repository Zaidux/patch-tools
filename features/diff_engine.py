#!/usr/bin/env python3
"""
Diff Engine for Professional Patch Tool
Advanced diff generation, preview, and patch file creation
"""

import difflib
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


class DiffEngine:
    """Advanced diff generation and visualization"""
    
    def __init__(self, file_manager):
        self.file_manager = file_manager
        self.diff_cache = {}

    def generate_unified_diff(self, original_lines: List[str], modified_lines: List[str], 
                            fromfile: str, tofile: str, context_lines: int = 3) -> List[str]:
        """Generate unified diff between two sets of lines"""
        diff = list(difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=fromfile,
            tofile=tofile,
            lineterm='',
            n=context_lines
        ))
        return diff

    def generate_patch_file(self, original_file: str, modified_file: str, 
                          patch_file: str = None) -> Optional[str]:
        """Generate a standard patch file from two files"""
        original_info = self.file_manager.get_file_info(original_file)
        modified_info = self.file_manager.get_file_info(modified_file)
        
        if not original_info or not modified_info:
            return None
            
        if not patch_file:
            patch_file = f"{original_file}.patch"
            
        original_lines = [line + '\n' for line in original_info['line_list']]
        modified_lines = [line + '\n' for line in modified_info['line_list']]
        
        diff = self.generate_unified_diff(
            original_lines, modified_lines, 
            f"a/{original_file}", f"b/{modified_file}"
        )
        
        try:
            with open(patch_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(diff))
            return patch_file
        except Exception as e:
            print(f"❌ Error writing patch file: {e}")
            return None

    def preview_changes(self, file_path: str, patches: List[Dict]) -> Tuple[bool, List[str], List[str]]:
        """Preview changes without applying them"""
        original_lines = self.file_manager.read_file_lines(file_path)
        if original_lines is None:
            return False, [], []
            
        # Create a copy for simulation
        simulated_lines = original_lines.copy()
        
        # Sort patches in reverse order to avoid line number issues during simulation
        sorted_patches = sorted(patches,
                              key=lambda x: x.get('line_number', x.get('start_line', 0)),
                              reverse=True)
        
        # Simulate applying patches
        successful_patches = 0
        patch_engine = self._get_patch_engine()
        
        for patch in sorted_patches:
            success, _ = patch_engine._apply_single_patch(simulated_lines, patch)
            if success:
                successful_patches += 1
        
        # Generate diff
        diff = self.generate_unified_diff(
            original_lines, simulated_lines,
            f"a/{file_path}", f"b/{file_path}"
        )
        
        return successful_patches > 0, diff, simulated_lines

    def display_side_by_side_diff(self, original_lines: List[str], modified_lines: List[str], 
                                file_path: str, context_lines: int = 5):
        """Display side-by-side diff preview"""
        print(f"\n🔍 SIDE-BY-SIDE DIFF PREVIEW: {file_path}")
        print("=" * 100)
        print(f"{'ORIGINAL':<50} | {'MODIFIED':<50}")
        print("-" * 100)
        
        # Create a differ that shows changes
        differ = difflib.Differ()
        diff = list(differ.compare(
            [line.rstrip('\n') for line in original_lines],
            [line.rstrip('\n') for line in modified_lines]
        ))
        
        original_display = []
        modified_display = []
        
        for line in diff:
            if line.startswith('  '):  # Unchanged
                content = line[2:]
                original_display.append(f"  {content}")
                modified_display.append(f"  {content}")
            elif line.startswith('- '):  # Removed
                original_display.append(f"🔴 {line[2:]}")
                modified_display.append(" " * 50)
            elif line.startswith('+ '):  # Added
                original_display.append(" " * 50)
                modified_display.append(f"🟢 {line[2:]}")
            elif line.startswith('? '):  # Changes within line
                # This would require more sophisticated handling
                pass
        
        # Display side by side
        for i in range(min(len(original_display), 50)):  # Limit display
            orig = original_display[i] if i < len(original_display) else ""
            mod = modified_display[i] if i < len(modified_display) else ""
            print(f"{orig:<50} | {mod:<50}")
        
        print("=" * 100)
        print("Legend: 🔴 Removed  🟢 Added  ⚫ Changed")

    def interactive_diff_menu(self, file_path: str, patches: List[Dict]):
        """Interactive diff preview menu"""
        success, diff, modified_lines = self.preview_changes(file_path, patches)
        
        if not success:
            print("❌ No changes to preview")
            return
            
        while True:
            print(f"\n🔍 DIFF PREVIEW: {file_path}")
            print("=" * 60)
            print("1. 📋 View unified diff")
            print("2. 👁️  View side-by-side diff")
            print("3. 📄 View modified file preview")
            print("4. 💾 Generate patch file")
            print("0. ↩️  Back")
            print("=" * 60)
            
            try:
                choice = input("\nSelect view: ").strip()
                
                if choice == '1':
                    self._display_unified_diff(diff)
                elif choice == '2':
                    original_lines = self.file_manager.read_file_lines(file_path) or []
                    self.display_side_by_side_diff(original_lines, modified_lines, file_path)
                elif choice == '3':
                    self._display_modified_preview(modified_lines, file_path)
                elif choice == '4':
                    self._generate_patch_file_interactive(file_path, patches)
                elif choice == '0':
                    break
                else:
                    print("❌ Invalid choice")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def _display_unified_diff(self, diff: List[str]):
        """Display unified diff with syntax highlighting"""
        if not diff:
            print("❌ No differences to display")
            return
            
        print(f"\n📋 UNIFIED DIFF")
        print("=" * 80)
        
        for line in diff:
            if line.startswith('---'):
                print(f"🔴 {line}")
            elif line.startswith('+++'):
                print(f"🟢 {line}")
            elif line.startswith('@'):
                print(f"🔵 {line}")
            elif line.startswith('-'):
                print(f"🔴 {line}")
            elif line.startswith('+'):
                print(f"🟢 {line}")
            else:
                print(f"  {line}")
                
        print("=" * 80)

    def _display_modified_preview(self, modified_lines: List[str], file_path: str):
        """Display preview of modified file"""
        print(f"\n📄 MODIFIED FILE PREVIEW: {file_path}")
        print("=" * 80)
        
        for i, line in enumerate(modified_lines[:30], 1):  # Show first 30 lines
            print(f"{i:4d} │ {line.rstrip()}")
            
        if len(modified_lines) > 30:
            print(f"... and {len(modified_lines) - 30} more lines")
        print("=" * 80)

    def _generate_patch_file_interactive(self, file_path: str, patches: List[Dict]):
        """Interactive patch file generation"""
        print(f"\n💾 GENERATE PATCH FILE")
        
        patch_filename = input(f"Patch filename [{file_path}.patch]: ").strip()
        if not patch_filename:
            patch_filename = f"{file_path}.patch"
            
        # Create temporary modified file for diff
        temp_file = f"{file_path}.temp_patch"
        original_lines = self.file_manager.read_file_lines(file_path)
        
        if original_lines:
            # Apply patches to temporary copy
            modified_lines = original_lines.copy()
            patch_engine = self._get_patch_engine()
            
            sorted_patches = sorted(patches,
                                  key=lambda x: x.get('line_number', x.get('start_line', 0)),
                                  reverse=True)
            
            for patch in sorted_patches:
                patch_engine._apply_single_patch(modified_lines, patch)
            
            # Write temporary file
            self.file_manager.write_file_lines(temp_file, modified_lines)
            
            # Generate patch file
            patch_file = self.generate_patch_file(file_path, temp_file, patch_filename)
            
            # Clean up
            try:
                os.remove(self.file_manager.resolve_path(temp_file))
            except:
                pass
                
            if patch_file:
                print(f"✅ Patch file generated: {patch_file}")
            else:
                print("❌ Failed to generate patch file")
        else:
            print("❌ Could not read original file")

    def apply_patch_file(self, patch_file: str, target_file: str = None) -> bool:
        """Apply a standard patch file to a target file"""
        if not os.path.exists(patch_file):
            print(f"❌ Patch file not found: {patch_file}")
            return False
            
        # For now, this is a placeholder for actual patch application
        # In a real implementation, you would use patch command or implement patch parsing
        print(f"⚠️  Patch file application not yet implemented")
        print(f"   Patch file: {patch_file}")
        print(f"   Target file: {target_file}")
        return False

    def _get_patch_engine(self):
        """Get a patch engine instance for simulation"""
        # This would normally come from dependency injection
        # For now, create a minimal implementation
        from core.patch_engine import PatchEngine
        return PatchEngine(self.file_manager, None)

    def calculate_change_statistics(self, original_lines: List[str], modified_lines: List[str]) -> Dict[str, int]:
        """Calculate statistics about changes"""
        added = 0
        removed = 0
        modified = 0
        
        differ = difflib.Differ()
        diff = list(differ.compare(
            [line.rstrip('\n') for line in original_lines],
            [line.rstrip('\n') for line in modified_lines]
        ))
        
        for line in diff:
            if line.startswith('+ '):
                added += 1
            elif line.startswith('- '):
                removed += 1
            elif line.startswith('? '):
                modified += 1
                
        return {
            'added': added,
            'removed': removed, 
            'modified': modified,
            'total_changes': added + removed + modified
        }
