import os
import json
import subprocess
from pathlib import Path

# Configuration
FOLDERS_TO_TRACK = ["Movies"]  # Change this to all your shared folder names
BASE_DIR = Path("F:/ShareMedia").resolve()  # Change this to your shared folder path
INDEX_FILE = BASE_DIR / "file_index.json"
GIT_REPO_PATH = BASE_DIR  # Git repository should be initialized here


def scan_folders():
    file_data = {}
    for folder in FOLDERS_TO_TRACK:
        folder_path = BASE_DIR / folder
        if not folder_path.exists():
            continue

        file_data[folder] = []
        for file in folder_path.glob("**/*"):
            if file.is_file():
                file_data[folder].append(
                    {"filename": file.name, "size": file.stat().st_size}
                )

    return file_data


def update_index():
    print("Scanning folders...")
    new_data = scan_folders()

    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r") as f:
            old_data = json.load(f)
    else:
        old_data = {}

    if new_data != old_data:
        with open(INDEX_FILE, "w") as f:
            json.dump(new_data, f, indent=4)
        print("Index updated!")
        return True

    print("No changes detected.")
    return False


def git_commit_and_push():
    try:
        subprocess.run(["git", "add", "file_index.json"], cwd=GIT_REPO_PATH, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Updated file index"], cwd=GIT_REPO_PATH, check=True
        )
        subprocess.run(["git", "push"], cwd=GIT_REPO_PATH, check=True)
        print("Changes pushed to Git.")
    except subprocess.CalledProcessError:
        print("Git operation failed. Ensure your repository is set up correctly.")


def show_missing_files():
    subprocess.run(["git", "pull"], cwd=GIT_REPO_PATH, check=True)
    with open(INDEX_FILE, "r") as f:
        latest_index = json.load(f)

    local_files = scan_folders()
    missing_files = {}

    for folder in FOLDERS_TO_TRACK:
        if folder not in latest_index:
            continue

        latest_filenames = {file["filename"] for file in latest_index[folder]}
        local_filenames = {file["filename"] for file in local_files.get(folder, [])}
        missing = latest_filenames - local_filenames

        if missing:
            missing_files[folder] = list(missing)

    if missing_files:
        print("You are missing these files:")
        for folder, files in missing_files.items():
            print(f"{folder}:")
            for file in files:
                print(f"  - {file}")
    else:
        print("You have all the latest files!")


if __name__ == "__main__":
    if update_index():
        git_commit_and_push()
    else:
        show_missing_files()
