#!/usr/bin/env python3
"""
Patch History for Professional Patch Tool
Undo/Redo functionality and change tracking
"""

import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Deque
from collections import deque
from datetime import datetime


class PatchHistory:
    """Manages patch history with undo/redo capabilities"""
    
    def __init__(self, file_manager, history_file: str = ".patch_history.json"):
        self.file_manager = file_manager
        self.history_file = history_file
        self.undo_stack: Deque[Dict] = deque(maxlen=100)  # Last 100 operations
        self.redo_stack: Deque[Dict] = deque(maxlen=100)
        self.current_session = []
        
        self._load_history()

    def _load_history(self):
        """Load history from file"""
        history_path = os.path.join(self.file_manager.base_path, self.history_file)
        
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r') as f:
                    history_data = json.load(f)
                    self.undo_stack = deque(history_data.get('undo_stack', []), maxlen=100)
                    self.redo_stack = deque(history_data.get('redo_stack', []), maxlen=100)
            except Exception as e:
                print(f"⚠️  Error loading history: {e}")

    def _save_history(self):
        """Save history to file"""
        history_path = os.path.join(self.file_manager.base_path, self.history_file)
        
        try:
            with open(history_path, 'w') as f:
                json.dump({
                    'undo_stack': list(self.undo_stack),
                    'redo_stack': list(self.redo_stack),
                    'last_saved': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving history: {e}")

    def record_operation(self, file_path: str, patches: List[Dict], 
                        original_content: List[str], result: Dict):
        """Record a patch operation for undo capability"""
        operation = {
            'timestamp': datetime.now().isoformat(),
            'file_path': file_path,
            'patches_applied': patches.copy(),
            'original_content': original_content.copy(),
            'result': result.copy(),
            'backup_file': result.get('backup_path', ''),
            'operation_id': self._generate_operation_id()
        }
        
        self.undo_stack.append(operation)
        self.current_session.append(operation)
        self.redo_stack.clear()  # Clear redo stack when new operation is recorded
        self._save_history()

    def undo_last_operation(self) -> bool:
        """Undo the last patch operation"""
        if not self.undo_stack:
            print("❌ Nothing to undo")
            return False
            
        operation = self.undo_stack.pop()
        
        print(f"\n↩️  UNDOING: {operation['file_path']}")
        print(f"⏰ Original operation: {operation['timestamp']}")
        
        # Restore from backup if available
        if operation['backup_file'] and os.path.exists(operation['backup_file']):
            success = self.file_manager.restore_backup(operation['file_path'])
            if success:
                print("✅ Successfully undone using backup")
                self.redo_stack.append(operation)
                self._save_history()
                return True
        
        # If no backup, try to reverse patches
        print("⚠️  No backup available, attempting to reverse patches...")
        
        # This would require implementing reverse patches
        # For now, we'll just inform the user
        print("❌ Automatic reversal not implemented. Please use backup restoration.")
        return False

    def redo_operation(self) -> bool:
        """Redo the last undone operation"""
        if not self.redo_stack:
            print("❌ Nothing to redo")
            return False
            
        operation = self.redo_stack.pop()
        
        print(f"\n↪️  REDOING: {operation['file_path']}")
        
        # Re-apply the patches
        success, result = self.file_manager.patch_engine.apply_patches(
            operation['file_path'], 
            operation['patches_applied']
        )
        
        if success:
            print("✅ Successfully redone")
            self.undo_stack.append(operation)
            self._save_history()
            return True
        else:
            print("❌ Failed to redo operation")
            return False

    def get_undo_info(self) -> Optional[Dict]:
        """Get information about the next undo operation"""
        if self.undo_stack:
            return self.undo_stack[-1]
        return None

    def get_redo_info(self) -> Optional[Dict]:
        """Get information about the next redo operation"""
        if self.redo_stack:
            return self.redo_stack[-1]
        return None

    def interactive_history_menu(self):
        """Interactive history management menu"""
        while True:
            print(f"\n📋 PATCH HISTORY")
            print("=" * 60)
            
            undo_info = self.get_undo_info()
            redo_info = self.get_redo_info()
            
            if undo_info:
                print(f"1. ↩️  Undo last operation")
                print(f"   📄 {undo_info['file_path']}")
                print(f"   ⏰ {undo_info['timestamp']}")
            else:
                print("1. ↩️  Undo last operation (nothing to undo)")
                
            if redo_info:
                print(f"2. ↪️  Redo last operation") 
                print(f"   📄 {redo_info['file_path']}")
                print(f"   ⏰ {redo_info['timestamp']}")
            else:
                print("2. ↪️  Redo last operation (nothing to redo)")
                
            print("3. 📊 View operation history")
            print("4. 🧹 Clear history")
            print("0. ↩️  Back to main menu")
            print("=" * 60)
            
            try:
                choice = input("\nSelect option: ").strip()
                
                if choice == '1' and undo_info:
                    self.undo_last_operation()
                elif choice == '2' and redo_info:
                    self.redo_operation()
                elif choice == '3':
                    self._view_operation_history()
                elif choice == '4':
                    self._clear_history()
                elif choice == '0':
                    break
                else:
                    print("❌ Invalid choice or operation not available")
                    
            except KeyboardInterrupt:
                print("\n⏹️  Operation cancelled.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def _view_operation_history(self):
        """View detailed operation history"""
        print(f"\n📊 OPERATION HISTORY")
        print("=" * 80)
        
        if not self.undo_stack and not self.redo_stack:
            print("❌ No history available")
            return
            
        all_operations = list(self.redo_stack) + list(self.undo_stack)
        all_operations.sort(key=lambda x: x['timestamp'], reverse=True)
        
        for i, operation in enumerate(all_operations[:20], 1):  # Show last 20
            status = "🔴 UNDONE" if operation in self.redo_stack else "🟢 APPLIED"
            print(f"\n{i}. {status} - {operation['timestamp']}")
            print(f"   📄 File: {operation['file_path']}")
            print(f"   🔧 Patches: {len(operation['patches_applied'])} applied")
            print(f"   📝 Description: {operation['patches_applied'][0].get('description', 'No description') if operation['patches_applied'] else 'No patches'}")

    def _clear_history(self):
        """Clear all history"""
        confirm = input("\n❌ Are you sure you want to clear ALL history? (type 'CLEAR' to confirm): ")
        if confirm == 'CLEAR':
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.current_session.clear()
            
            # Delete history file
            history_path = os.path.join(self.file_manager.base_path, self.history_file)
            try:
                if os.path.exists(history_path):
                    os.remove(history_path)
            except:
                pass
                
            print("✅ History cleared")
        else:
            print("❌ History clearance cancelled")

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        return {
            'session_start': self.current_session[0]['timestamp'] if self.current_session else None,
            'operations_count': len(self.current_session),
            'files_modified': len(set(op['file_path'] for op in self.current_session)),
            'total_patches': sum(len(op['patches_applied']) for op in self.current_session)
        }

    def _generate_operation_id(self) -> str:
        """Generate a unique operation ID"""
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    def export_history(self, export_file: str = "patch_history_export.json") -> bool:
        """Export history to file"""
        try:
            with open(export_file, 'w') as f:
                json.dump({
                    'export_timestamp': datetime.now().isoformat(),
                    'undo_stack': list(self.undo_stack),
                    'redo_stack': list(self.redo_stack),
                    'current_session': self.current_session,
                    'session_summary': self.get_session_summary()
                }, f, indent=2, default=str)
            print(f"✅ History exported to {export_file}")
            return True
        except Exception as e:
            print(f"❌ Error exporting history: {e}")
            return False

    def search_history(self, query: str) -> List[Dict]:
        """Search history by filename or patch description"""
        query = query.lower()
        results = []
        
        all_operations = list(self.redo_stack) + list(self.undo_stack)
        
        for operation in all_operations:
            if (query in operation['file_path'].lower() or
                any(query in patch.get('description', '').lower() 
                    for patch in operation['patches_applied'])):
                results.append(operation)
                
        return results
