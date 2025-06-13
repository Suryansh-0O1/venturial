import bpy
import sys
import os
import subprocess
import importlib


PATHTOINSTALL = bpy.utils.user_resource("SCRIPTS", path="modules")
ADDON_DIR_NAME = "venturial"
CUSTOM_MODULE_NAME = "pyvnt"

restart_needed = False


def find_wheel_path(base_path, lib_folder, module_name):
    """Finds the first .whl file in the specified lib folder."""
    wheel_dir = os.path.join(base_path, lib_folder, module_name)
    if not os.path.isdir(wheel_dir):
        print(f"ERROR: Wheel directory not found: {wheel_dir}")
        return None

    for f in os.listdir(wheel_dir):
        if f.endswith(".whl"):
            return os.path.join(wheel_dir, f)

    print(f"No .whl file found in {wheel_dir}")
    return None


# Find the addon's base installation directory
user_scripts_path = bpy.utils.script_path_user()
if user_scripts_path:
    addon_base_path = os.path.join(user_scripts_path, "addons", ADDON_DIR_NAME)
    CUSTOM_WHEEL_PATH = find_wheel_path(addon_base_path, "lib", CUSTOM_MODULE_NAME)
else:
    print("Blender user script path not found. Cannot locate addon.")
    addon_base_path = None
    CUSTOM_WHEEL_PATH = None


def ensure_pip():
    """Ensures pip is importable in Blender's Python environment."""
    try:
        import pip
        print("pip is available.")
        return True
    except ImportError:
        print("pip is not available in Blender's Python environment.")
        return False


def run_pip_install(args, target_path, label=""):
    """Runs pip install with subprocess into a target path."""
    python_exe = sys.executable
    os.makedirs(target_path, exist_ok=True)
    cmd = [python_exe, "-m", "pip", "install", "--upgrade", "--no-cache-dir", f"--target={target_path}"] + args
    print(f"[{label}] Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        print(f"[{label}] pip process completed successfully.")
        if result.stdout:
            print(f"--- pip STDOUT ---\n{result.stdout}\n--- End pip STDOUT ---")
        return True
    except Exception as e:
        print(f"[{label}] An unexpected exception occurred while running pip: {e}")
        return False

def is_module_importable(module_name, search_paths=None):
    """Checks if a module can be imported, optionally searching in specific paths."""
    original_sys_path = list(sys.path)
    if search_paths:
        for spath in reversed(search_paths):
            if spath not in sys.path:
                sys.path.insert(0, spath)
        importlib.invalidate_caches()
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False
    finally:
        if search_paths:
            sys.path = original_sys_path
            importlib.invalidate_caches()


def install_dependencies():
    """
    Installs a custom wheel using pip if it's not already available.
    Returns True on success, False on failure.
    Sets global 'restart_needed' if an installation occurred.
    """
    global restart_needed

    if not ensure_pip():
        print("--- Dependency installation failed: pip is not available. ---")
        return False

    if PATHTOINSTALL not in sys.path:
        sys.path.insert(0, PATHTOINSTALL)
        importlib.invalidate_caches()
        print(f"Added '{PATHTOINSTALL}' to sys.path for this session.")

    if not CUSTOM_MODULE_NAME or not CUSTOM_WHEEL_PATH:
        print("custom module installation: Not configured.")
        return False 

    if not os.path.exists(CUSTOM_WHEEL_PATH):
        print(f"Custom wheel file not found: {CUSTOM_WHEEL_PATH}")
        if addon_base_path and not os.path.exists(addon_base_path):
             print(f"The base addon directory was not found at {addon_base_path}")
        return False

    # Check if module is already importable from our target path
    if is_module_importable(CUSTOM_MODULE_NAME, [PATHTOINSTALL]):
        print(f"Module '{CUSTOM_MODULE_NAME}' is already available. No installation needed.")
        return True

    # If not importable, attempt to install it
    print(f"Attempting to install '{CUSTOM_MODULE_NAME}' from wheel: {os.path.basename(CUSTOM_WHEEL_PATH)}")
    pip_succeeded = run_pip_install([CUSTOM_WHEEL_PATH], PATHTOINSTALL, label="CustomWheel")

    if not pip_succeeded:
        print(f"--- Dependency installation failed due to pip error for '{CUSTOM_MODULE_NAME}'. ---")
        return False

    # If pip command succeeded, mark that a restart might be needed
    restart_needed = True
    print(f"pip command for '{CUSTOM_MODULE_NAME}' completed.")

    # --- Final Verification ---
    print("--- Verifying installation ---")
    importlib.invalidate_caches() # Invalidate caches again after installation
    if is_module_importable(CUSTOM_MODULE_NAME, [PATHTOINSTALL]):
        print(f"Successfully installed and verified '{CUSTOM_MODULE_NAME}'.")
    else:
        print(f"WARNING: Module '{CUSTOM_MODULE_NAME}' was installed by pip but is not immediately importable.")
        print("This is common and requires a Blender restart to take full effect.")

    if restart_needed:
        print("\n*** A Blender restart is recommended to ensure all dependencies are loaded correctly. ***\n")

    print("--- Dependency installation process finished. ---")
    return True