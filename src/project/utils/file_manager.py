import os
import re
import shutil

def create_project_folder(folder_name):
    """
    Creates a folder inside 'generated_projects/' based on user input.

    Args:
        folder_name (str): Name of the project folder.

    Returns:
        str: The full path to the created folder.
    """
    project_root = os.path.join("generated_projects", folder_name)
    os.makedirs(project_root, exist_ok=True)  # ✅ Ensure the folder exists
    print(f"📂 Project folder created: {project_root}")
    return project_root



def clean_filename(filename):
    """
    Removes invalid characters from a filename to make it OS-compatible.
    """
    return re.sub(r'[<>:"/\\|?*📂]', "", filename).strip()

def clean_filename(filename):
    """
    Cleans and sanitizes the filename to prevent invalid or unsafe file names.
    """
    filename = filename.replace("..", "").replace("\\", "/").strip()
    return filename if filename else None  # Return None for empty filenames

def is_valid_filename(filename):
    invalid_patterns = [
        r"^project_root/?$",
        r"^[#\s]*$",
        r"^[0-9]+\.",                  # e.g., "3. Configure..."
        r".*[:*?\"<>|].*",             # Windows forbidden characters
        r"^bash$",                    # Ignore shell commands
    ]
    return not any(re.match(p, filename.strip(), re.IGNORECASE) for p in invalid_patterns)

def sanitize_filename(filename, fallback_name="misc_file"):
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.strip()
    return filename or f"{fallback_name}.txt"

def save_generated_code(generated_code_dict, project_root):
    """
    Saves the AI-generated code into the user-defined project folder.

    Args:
        generated_code_dict (dict): Dictionary containing file paths and their code.
        project_root (str): Path to the user-specified project folder.
    """
    if not generated_code_dict:
        print("⚠️ No code files to save.")
        return

    os.makedirs(project_root, exist_ok=True)  # Ensure root project folder exists
    saved_files = []

    for file_name, code in generated_code_dict.items():
        if not is_valid_filename(file_name):
            print(f"⚠️ Skipping invalid filename: {file_name}")
            continue

        clean_file_name = sanitize_filename(file_name)

        # Preserve folder structure if '/' is in the original path
        path_parts = file_name.replace("\\", "/").split("/")
        if len(path_parts) > 1:
            clean_file_name = os.path.join(*path_parts)

        file_path = os.path.join(project_root, clean_file_name)

        # ✅ Ensure all intermediate folders are created
        folder_path = os.path.dirname(file_path)
        if folder_path != project_root:
            os.makedirs(folder_path, exist_ok=True)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            saved_files.append(file_path)
            print(f"✅ Code saved: {file_path}")
        except PermissionError:
            print(f"❌ Permission Error: Could not save file {file_path}. Check folder permissions.")
        except OSError as e:
            print(f"❌ OS Error: {e} — while saving file {file_path}")

    print(f"\n✅ Code successfully saved in {len(saved_files)} files inside '{project_root}'")

def clear_project_folder(folder_path: str):
    """
    Deletes all files and subfolders in the given project folder.

    Args:
        folder_path (str): The path to the folder containing generated code.
    """
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Check if it's a file or folder and delete accordingly
            if os.path.isfile(file_path):
                os.remove(file_path)  # Remove file
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Remove folder and its contents
