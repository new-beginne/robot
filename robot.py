# filename: robot.py (The All-in-One: Professional File Handling)
import os
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple, Callable
import argparse

# --- MAJOR CHANGE: Centralized application data directory ---
# All generated files will now be stored in the user's home directory to keep project folders clean.
APP_DIR = Path.home() / ".craftly-robot"
BACKUP_DIR = APP_DIR / "backups"
INSTRUCTIONS_DIR = APP_DIR / "instructions"

@dataclass
class FileOperator:
    # This class is perfect, no changes needed.
    action: Dict[str, Any]
    op: str = field(init=False)
    mode: str = field(init=False)
    path: Path = field(init=False)

    def __post_init__(self):
        self.op = self.action['operation']
        self.mode = self.action['mode']
        self.path = Path(self.action['path'])
        self.OPERATIONS: Dict[Tuple[str, str], Callable] = {
            ('create', 'folder'): self._create_folder, ('delete', 'folder'): self._delete_folder,
            ('create', 'file'): self._create_file, ('delete', 'file'): self._delete_file,
        }
    def run(self) -> Tuple[str, Dict[str, Any]]:
        method = self.OPERATIONS.get((self.op, self.mode))
        if not method: raise ValueError(f"Unsupported operation: {self.op} {self.mode}")
        return method()
    def _create_folder(self) -> Tuple[str, dict]:
        if not self.path.parent.exists(): raise FileNotFoundError(f"Missing parent directory: {self.path.parent}")
        self.path.mkdir(exist_ok=False); return f"created folder: {self.path}", {'operation': 'delete', 'mode': 'folder', 'path': str(self.path)}
    def _delete_folder(self) -> Tuple[str, dict]:
        if not self.path.is_dir(): raise FileNotFoundError(f"No such folder: {self.path}")
        if any(self.path.iterdir()): raise OSError(f"Folder not empty: {self.path}")
        self.path.rmdir(); return f"deleted folder: {self.path}", {'operation': 'create', 'mode': 'folder', 'path': str(self.path)}
    def _create_file(self) -> Tuple[str, dict]:
        if not self.path.parent.exists(): raise FileNotFoundError(f"Missing parent folder: {self.path.parent}")
        self.path.touch(exist_ok=False)
        content = self.action.get('content')
        if content is not None: self.path.write_text(content)
        return f"created file: {self.path}", {'operation': 'delete', 'mode': 'file', 'path': str(self.path)}
    def _delete_file(self) -> Tuple[str, dict]:
        if not self.path.is_file(): raise FileNotFoundError(f"No such file: {self.path}")
        content = self.path.read_text()
        self.path.unlink(); return f"deleted file: {self.path}", {'operation': 'create', 'mode': 'file', 'path': str(self.path), 'content': content}

def save_backup(backup_file: Path, reverse_actions: List[dict]):
    if not reverse_actions: return
    # --- CHANGE: Ensure the central backup directory exists ---
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    reverse_actions.reverse()
    backup_file.write_text(json.dumps(reverse_actions, indent=4))

# --- Wizard and Review logic (No changes needed in their internal logic) ---
def run_wizard_flow(instructions: List[dict], base_path: Path):
    path_stack = [base_path]
    print("\n--- Interactive Instruction Builder ---")
    if instructions:
        print("Continuing from where you left off. You can add more items.")
    while True:
        current_path = path_stack[-1]
        print("\n" + "="*40)
        print(f"📍 Current Location: {current_path}")
        print("What would you like to do?")
        print("  1. Create a new folder")
        print("  2. Create a new file")
        sub_folders = [Path(instr['path']) for instr in instructions if instr['mode'] == 'folder' and Path(instr['path']).parent == current_path]
        if sub_folders: print("  3. Navigate into a sub-folder")
        if len(path_stack) > 1: print("  4. Go back to the parent folder")
        print("  5. List planned items in current folder")
        print("  0. Finish and review structure")
        print("="*40)
        choice = input("👉 Enter your choice: ").strip()
        if choice == '1':
            folder_name = input("📁 Enter new folder name: ").strip()
            if not folder_name: print("❌ Name cannot be empty."); continue
            new_path = current_path / folder_name
            instructions.append({"operation": "create", "mode": "folder", "path": str(new_path)})
            print(f"✅ Added folder instruction: '{folder_name}'")
        elif choice == '2':
            file_name = input("📄 Enter new file name: ").strip()
            if not file_name: print("❌ Name cannot be empty."); continue
            content = input(f"📝 Content for '{file_name}' (press Enter for empty): ")
            new_path = current_path / file_name
            instructions.append({"operation": "create", "mode": "file", "path": str(new_path), "content": content})
            print(f"✅ Added file instruction: '{file_name}'")
        elif choice == '3' and sub_folders:
            print("\nWhich folder to enter?")
            for i, folder in enumerate(sub_folders, 1): print(f"  {i}. {folder.name}")
            try:
                folder_choice = int(input("👉 Enter folder number: ").strip())
                if 1 <= folder_choice <= len(sub_folders): path_stack.append(sub_folders[folder_choice - 1])
                else: print("❌ Invalid number.")
            except ValueError: print("❌ Please enter a valid number.")
        elif choice == '4' and len(path_stack) > 1:
            path_stack.pop(); print(f"✅ Navigated back to: {path_stack[-1]}")
        elif choice == '5':
            print(f"--- Planned items in {current_path} ---")
            items = [instr for instr in instructions if Path(instr['path']).parent == current_path]
            if not items: print("  (empty)")
            for item in items: print(f"  - {'📁' if item['mode'] == 'folder' else '📄'} {Path(item['path']).name}")
            input("\n(Press Enter to continue...)")
        elif choice == '0':
            if not instructions: print("⚠️ No instructions created."); break
            print("\n✅ Finished collecting instructions. Moving to review stage...")
            break
        else: print("❌ Invalid choice.")
    return instructions

def review_and_edit_instructions(instructions: List[dict]) -> List[dict] or None:
    instructions_backup = None
    while True:
        tree = {}; item_map = {}; item_counter = 1
        if not instructions: return []
        try:
            common_path_str = os.path.commonpath([instr['path'] for instr in instructions])
            common_base = Path(common_path_str).parent
        except ValueError: common_base = Path('/')
        for instr in instructions:
            node = tree
            for part in Path(instr['path']).relative_to(common_base).parts: node = node.setdefault(part, {})
        print("\n" + "="*50); print("📄 FINAL STRUCTURE PREVIEW"); print("="*50)
        def print_tree(node, current_base_path):
            nonlocal item_counter; sorted_items = sorted(node.items(), key=lambda x: not bool(x[1]))
            for i, (name, children) in enumerate(sorted_items):
                is_last, connector = i == len(sorted_items) - 1, "└── " if i == len(sorted_items) - 1 else "├── "
                full_path, is_folder = current_base_path / name, bool(children)
                item_map[item_counter] = {'path': str(full_path), 'is_folder': is_folder}
                print(f"{' ' * len(str(current_base_path.relative_to(common_base)))}{connector}[{item_counter}] {'📁' if is_folder else '📄'} {name}")
                item_counter += 1
                if children: print_tree(children, full_path)
        print_tree(tree, common_base)
        print("\n" + "-"*50); print("What to do now?"); 
        print("  1. Rename an item"); print("  2. Delete an item")
        print("  3. Copy an item"); print("  4. Move an item")
        print("  5. Go back and add more items")
        if instructions_backup: print("  6. Undo the last change")
        print("  0. Looks good! Continue and execute."); print("-" * 50)
        
        choice = input("👉 Enter your choice: ").strip()
        
        if choice == '0': return instructions
        elif choice == '5': print("✅ Returning to the builder..."); return None
        elif choice == '6' and instructions_backup:
            instructions, instructions_backup = instructions_backup, None
            print("✅ The last change has been undone."); continue
        elif choice in ['1', '2', '3', '4']:
            try:
                instructions_backup = [instr.copy() for instr in instructions]
                item_num = int(input("👉 Enter the number of the item to act on: ").strip())
                if item_num not in item_map: print("❌ Invalid item number."); instructions_backup = None; continue
                source_path_str = item_map[item_num]['path']
                if choice == '1':
                    new_name = input(f"👉 Enter new name for '{Path(source_path_str).name}': ").strip()
                    if not new_name: print("❌ Name cannot be empty."); instructions_backup = None; continue
                    for instr in instructions:
                        if instr['path'].startswith(source_path_str):
                            old_p, new_p = Path(instr['path']), Path(source_path_str)
                            instr['path'] = str(new_p.parent / new_name / old_p.relative_to(new_p))
                    print(f"✅ Renamed successfully!")
                elif choice == '2':
                    instructions = [i for i in instructions if not i['path'].startswith(source_path_str)]
                    if not instructions: print("✅ All items deleted."); return []
                    print(f"✅ Deleted successfully!")
                elif choice in ['3', '4']:
                    folder_map = {k: v['path'] for k, v in item_map.items() if v['is_folder']}
                    if not folder_map: print("❌ No destination folders available."); instructions_backup = None; continue
                    print("\nAvailable destination folders:");
                    for num, path in folder_map.items(): print(f"  [{num}] {path}")
                    dest_num = int(input("👉 Enter destination folder number: ").strip())
                    if dest_num not in folder_map: print("❌ Invalid destination number."); instructions_backup = None; continue
                    dest_path_str = folder_map[dest_num]
                    if Path(dest_path_str).is_relative_to(source_path_str):
                        print("❌ Cannot copy/move a folder into itself."); instructions_backup = None; continue
                    source_children = [i.copy() for i in instructions if i['path'].startswith(source_path_str)]
                    for instr in source_children:
                        instr['path'] = str(Path(dest_path_str) / Path(instr['path']).relative_to(Path(source_path_str).parent))
                        instructions.append(instr)
                    if choice == '4':
                        instructions = [i for i in instructions if not i['path'].startswith(source_path_str)]
                        print(f"✅ Moved successfully!")
                    else: print(f"✅ Copied successfully!")
            except ValueError: print("❌ Please enter a valid number."); instructions_backup = None
            except Exception as e: print(f"An error occurred: {e}"); instructions_backup = None
        else: print("❌ Invalid choice.")

def get_directory_from_user():
    current_dir = os.getcwd()
    print(f"\nCurrent Directory: {current_dir}")
    custom_dir = input("Enter target directory path (press Enter to use current directory): ").strip()
    dir_path = Path(custom_dir) if custom_dir else Path(current_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    print(f"✅ Working directory set to: {dir_path}")
    return dir_path

# --- Main Execution and Argument Parsing ---
def execute_instructions(instructions: List[dict], input_path: Path):
    if not instructions: print("No operations to perform."); return
    # --- CHANGE: Backup file path now uses the central backup directory ---
    backup_file = BACKUP_DIR / f"{input_path.stem}.bak"
    print(f"\n⚙️ Running operations... (Backup will be saved to {backup_file})")
    completed_reverse_actions, was_successful = [], True
    for idx, instr in enumerate(instructions, 1):
        try:
            result, reverse_action = FileOperator(instr).run()
            print(f"✓ [{idx}/{len(instructions)}] {result}")
            completed_reverse_actions.append(reverse_action)
        except Exception as e:
            print(f"✗ [{idx}/{len(instructions)}] {e}", file=sys.stderr)
            was_successful = False; break
    save_backup(backup_file, completed_reverse_actions)
    print("\n" + "-"*20)
    if not was_successful: print(f"🔥 Operation failed.")
    else: print(f"🎉 Operation completed successfully!")
    if completed_reverse_actions:
        script_name = Path(sys.argv[0]).name
        print(f"⏪ To undo these changes, run:\npython3 {script_name} -i \"{input_path}\" --undo")
    if not was_successful: sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(description="A reversible file operator with a built-in wizard.")
    parser.add_argument('-i', '--input', help='Path to JSON file (skips wizard).')
    parser.add_argument('--undo', action='store_true', help='Revert actions from a backup file.')
    return parser.parse_args()

def main():
    args = parse_args()
    if args.undo:
        if not args.input: print("✗ Error: --undo requires -i <file>", file=sys.stderr); sys.exit(1)
        # --- CHANGE: Undo logic now looks for files in the central app directory ---
        input_path = Path(args.input)
        if not input_path.is_absolute() and not input_path.exists():
            # If a relative path is given (like instructions/auto_generated.json), check in the app dir
            potential_path = INSTRUCTIONS_DIR / input_path.name
            if potential_path.exists():
                input_path = potential_path
        
        backup_file = BACKUP_DIR / f"{input_path.stem}.bak"
        if not backup_file.exists(): print(f"✗ No backup for '{input_path}' found at '{backup_file}'.", file=sys.stderr); sys.exit(1)
        try:
            instructions_to_undo = json.loads(backup_file.read_text()); print(f"🔄 Undoing {len(instructions_to_undo)} actions...");
            for idx, instr in enumerate(instructions_to_undo, 1):
                result, _ = FileOperator(instr).run(); print(f"✓ [{idx}/{len(instructions_to_undo)}] UNDO: {result}")
            backup_file.unlink(); print(f"\n✅ Undo successful.")
        except Exception as e: print(f"✗ FATAL: Undo failed: {e}", file=sys.stderr); sys.exit(1)
        sys.exit(0)

    if args.input:
        print(f"📄 Running in File Mode: {args.input}"); input_file_path = Path(args.input)
        try:
            instructions = json.loads(input_file_path.read_text())
            if not isinstance(instructions, list): instructions = [instructions]
        except Exception as e: print(f"✗ Error reading file: {e}", file=sys.stderr); sys.exit(1)
    else: 
        print("🧙 Welcome to Craftly Robot Wizard!")
        base_dir = get_directory_from_user()
        instructions = []
        while True:
            instructions = run_wizard_flow(instructions, base_dir)
            if not instructions: break 
            final_instructions = review_and_edit_instructions(instructions)
            if final_instructions is None: continue
            else: instructions = final_instructions; break
        if not instructions: print("Process cancelled by user."); sys.exit(0)
        
        # --- CHANGE: Save generated instructions to the central app directory ---
        INSTRUCTIONS_DIR.mkdir(parents=True, exist_ok=True)
        # We can use a unique name, e.g., based on the root folder, to avoid overwrites
        root_folder_name = Path(instructions[0]['path']).name
        input_file_path = INSTRUCTIONS_DIR / f"{root_folder_name}_{os.getpid()}.json"
        
        input_file_path.write_text(json.dumps(instructions, indent=4))
        print(f"\n✅ Instructions saved to '{input_file_path}' for undo purposes.")

    execute_instructions(instructions, input_file_path)

if __name__ == '__main__':
    try: main()
    except KeyboardInterrupt: print("\n\nProgram interrupted by user. Exiting.")
    except Exception as e: print(f"\n\nAn unexpected error occurred: {e}")
