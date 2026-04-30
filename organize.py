import os
import shutil
import logging
import sys
from datetime import datetime
from collections import Counter
from pathlib import Path

# What kind of files go where
CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".md"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".flv"],
    "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
    "Code": [".py", ".js", ".html", ".css", ".cpp", ".java", ".json", ".xml"],
}

def get_category(filename):
    """Look at the file extension and figure out its group"""
    ext = Path(filename).suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Others"

def setup_logging(target_folder):
    """Set up a log file so we can see what happened later"""
    log_file = os.path.join(target_folder, "organize_log.txt")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return log_file

def generate_report(target_folder, file_counter, dry_run):
    """Create a little report with all the numbers"""
    report_path = os.path.join(target_folder, f"report_{datetime.now().strftime('%Y%m%d')}.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=== File Organization Report ===\n")
        f.write(f"Target folder: {target_folder}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Mode: {'DRY RUN (nothing actually moved)' if dry_run else 'LIVE'}\n\n")
        f.write("Summary:\n")
        for cat, count in file_counter.items():
            f.write(f"  - {cat}: {count} files\n")
        f.write(f"\nTotal files processed: {sum(file_counter.values())}\n")
    print(f"📄 Report saved: {report_path}")

def organize_files(target_folder, dry_run=False):
    """Main function – moves (or pretends to move) files into categories"""
    if not os.path.exists(target_folder):
        print(f"❌ Error: Folder '{target_folder}' does not exist.")
        return

    original_dir = os.getcwd()
    os.chdir(target_folder)

    all_files = [f for f in os.listdir() if os.path.isfile(f)]
    if not all_files:
        print("✨ No files to organize here.")
        os.chdir(original_dir)
        return

    setup_logging(target_folder)
    file_counter = Counter()

    print(f"\n🚀 Starting organization in: {target_folder}")
    if dry_run:
        print("⚠️  DRY RUN mode – just pretending.\n")
    else:
        print("\n")

    for filename in all_files:
        category = get_category(filename)
        file_counter[category] += 1
        dest_dir = os.path.join(target_folder, category)

        if not os.path.exists(dest_dir) and not dry_run:
            os.makedirs(dest_dir)

        if dry_run:
            print(f"[DRY RUN] Would move: {filename} -> {category}/")
            logging.info(f"[DRY RUN] {filename} -> {category}")
        else:
            try:
                shutil.move(filename, dest_dir)
                print(f"✅ Moved: {filename} -> {category}/")
                logging.info(f"Moved: {filename} -> {category}")
            except Exception as e:
                print(f"❌ Failed to move {filename}: {e}")
                logging.error(f"Failed to move {filename}: {e}")

    print("\n" + "="*50)
    print("📊 ORGANIZATION SUMMARY")
    for cat, count in file_counter.items():
        print(f"   {cat}: {count} file(s)")
    print(f"   Total: {sum(file_counter.values())} files")
    print("="*50)

    generate_report(target_folder, file_counter, dry_run)
    if not dry_run:
        print("✅ All done! Check the log file for details.")
    else:
        print("✅ Dry run finished. Run again without --dry-run to actually move.")

    os.chdir(original_dir)

def interactive_shell():
    """A friendly shell where you can cd around and then organize"""
    current_dir = os.getcwd()
    print("\n📂 Smart File Organizer - Interactive Shell")
    print("Commands: cd, pwd, ls, organize [--dry-run], cls/clear, help, exit\n")
    while True:
        try:
            prompt = f"📁 [{current_dir}] > "
            user_input = input(prompt).strip()
            if not user_input:
                continue
            parts = user_input.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == "exit":
                print("Goodbye!")
                break
            elif cmd == "help":
                print("""
  cd <folder>           - change directory
  pwd                   - show current path
  ls [path]             - list contents
  organize [--dry-run]  - sort files in current folder
  cls / clear           - clear the terminal screen
  help                  - this help
  exit                  - quit
""")
            elif cmd in ("cls", "clear"):
                # Clear screen based on OS
                os.system('cls' if os.name == 'nt' else 'clear')
            elif cmd == "pwd":
                print(current_dir)
            elif cmd == "ls":
                target = args[0] if args else "."
                full = os.path.join(current_dir, target)
                try:
                    items = os.listdir(full)
                    for i in sorted(items):
                        print(i)
                except Exception as e:
                    print(f"Error: {e}")
            elif cmd == "cd":
                if not args:
                    print("Usage: cd <folder>")
                    continue
                new_path = args[0]
                if new_path.startswith("~"):
                    new_path = os.path.expanduser(new_path)
                abs_path = os.path.abspath(os.path.join(current_dir, new_path))
                if os.path.isdir(abs_path):
                    current_dir = abs_path
                else:
                    print(f"❌ Not a directory: {new_path}")
            elif cmd == "organize":
                dry = "--dry-run" in args
                organize_files(current_dir, dry_run=dry)
            else:
                print(f"Unknown command: {cmd}. Type 'help'.")
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except EOFError:
            print("\nGoodbye!")
            break
def main():
    # If no arguments → interactive shell
    if len(sys.argv) == 1:
        interactive_shell()
    else:
        # First argument is folder path
        folder = sys.argv[1]
        dry_run = "--dry-run" in sys.argv[2:]
        organize_files(folder, dry_run=dry_run)

if __name__ == "__main__":
    main()