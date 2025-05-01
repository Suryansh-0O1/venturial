import bpy
import sys
import os
import subprocess
import ensurepip
import importlib
import zipfile
import pkg_resources
import shutil


PATHTOINSTALL = bpy.utils.user_resource("SCRIPTS", path="modules")

addon_dir_name = "venturial"

user_scripts_path = bpy.utils.script_path_user()
if user_scripts_path is None:
    print("ERROR: Blender user script path not found. Cannot locate addon.")
    REQUIREMENTS_PATH = None
    CUSTOM_WHEEL_PATH = None
    addon_base_path = None
else:
    addon_base_path = os.path.join(user_scripts_path, "addons", addon_dir_name)
    REQUIREMENTS_PATH = os.path.join(addon_base_path, "requirements.txt")

    folder_path = os.path.join(addon_base_path, "lib", "pyvnt")
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    if files:
        CUSTOM_WHEEL_FILENAME = files[0]
        CUSTOM_WHEEL_PATH = os.path.join(folder_path, CUSTOM_WHEEL_FILENAME)
        print(CUSTOM_WHEEL_PATH)
    else:
        print("No file found in the folder.")

CUSTOM_MODULE_NAME = "pyvnt"

restart_needed = False

PYVNT_VERSION_WHL=None

def get_pyvnt_version():
    global PYVNT_VERSION_WHL
    try:
        with zipfile.ZipFile(CUSTOM_WHEEL_PATH, 'r') as whl:
            for name in whl.namelist():
                if name.endswith('METADATA') and '.dist-info/' in name:
                    metadata = whl.read(name).decode('utf-8')
                    for line in metadata.splitlines():
                        if line.startswith('Version:'):
                            PYVNT_VERSION_WHL= line.split(':', 1)[1].strip()
                            return
    except:
        print(f"Failed to get pyvnt ")

def ensure_pip():
    """Ensures pip is installed in Blender's Python environment."""
    global restart_needed
    try:
        import pip
        print("pip is available.")
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True, text=True, check=True)
            print(f"Found pip version: {result.stdout.strip()}")
        except Exception as e:
            print(f"Could not determine pip version: {e}")
        return True
    except ImportError:
        print("pip not found. Attempting to bootstrap pip...")
        try:
            ensurepip.bootstrap()
            restart_needed = True
            print("pip bootstrapped successfully. A restart may be required to use pip fully.")
            return True
        except Exception as e:
            print(f"ERROR: Failed to bootstrap pip: {e}")
            return False
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while checking for pip: {e}")
        return False

def run_pip_install(args, target_path, label=""):
    """Runs pip install with subprocess into target_path. Returns True on success, False on failure."""
    python_exe = sys.executable
    os.makedirs(target_path, exist_ok=True)
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'

    for item in os.listdir(target_path):
        item_path = os.path.join(target_path, item)
        if item.startswith("pyvnt") and (item.endswith(".dist-info") or os.path.isdir(item)):
            print(f"[{label}] Removing old: {item_path}")
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            except Exception as e:
                print(f"[{label}] Warning: Failed to remove {item_path}: {e}")


    cmd = [python_exe, "-m", "pip", "install", "--upgrade", "--no-cache-dir", f"--target={target_path}"] + args
    print(f"[{label}] Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env, encoding='utf-8', errors='replace')
        print(f"[{label}] pip process completed.")
        if result.stdout:
             print(f"--- pip STDOUT ---\n{result.stdout}\n--- End pip STDOUT ---")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[{label}] ERROR: pip install failed with code {e.returncode}")
        if e.stdout:
             print(f"--- pip STDOUT ---\n{e.stdout}\n--- End pip STDOUT ---")
        if e.stderr:
             print(f"--- pip STDERR ---\n{e.stderr}\n--- End pip STDERR ---")
        return False
    except Exception as e:
        print(f"[{label}] ERROR: Failed to run pip command: {e}")
        return False

def get_module_version(module_name=None,iswhl=False):
    """Get module version , returns version"""
    try:
        return pkg_resources.get_distribution(module_name).version
    except:
        return None

# def read_required_modules_from_reqs():
#     """Parses requirements.txt, returns list of import names (maps pyyaml->yaml)."""
#     module_name_map = {'pyyaml': 'yaml'}
#     modules = []
#     if REQUIREMENTS_PATH is None or not os.path.exists(REQUIREMENTS_PATH):
#         print(f"Requirements file not found or path not configured: {REQUIREMENTS_PATH}")
#         return modules
#     try:
#         with open(REQUIREMENTS_PATH) as f:
#             for line in f:
#                 line = line.strip()
#                 try:
#                     req = pkg_resources.Requirement.parse(line)
#                     name = req.project_name
#                     version = str(req.specifier) if req.specifier else None
#                     modules.append([ name, version])
#                 except Exception as e:
#                     print(f"Failed to parse line: {line} - {e}")
                
#             return modules
#     except Exception as e:
#         print(f"Error reading requirements file {REQUIREMENTS_PATH}: {e}")
#         return []

def is_module_importable(module_name, search_paths=None):
    """Checks if a module can be imported."""
    original_name = module_name

    original_sys_path = list(sys.path)
    if search_paths:
        for spath in reversed(search_paths):
             if spath not in sys.path:
                  sys.path.insert(0, spath)
        importlib.invalidate_caches()
    try:
        importlib.import_module(original_name)
        print(PYVNT_VERSION_WHL)
        print(get_module_version(original_name))
        if PYVNT_VERSION_WHL!=get_module_version(original_name):
            return False
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"Warning: Unexpected error checking module '{module_name}' (from '{original_name}'): {e}")
        return False
    finally:
        if search_paths:
            sys.path = original_sys_path
            importlib.invalidate_caches()
        
def install_dependencies():
    """
    Installs dependencies from requirements.txt and a custom wheel using pip.
    Returns True if pip commands likely succeeded, False if any pip command failed.
    Sets global 'restart_needed' if installation occurred.
    """
    global restart_needed
    print("\n--- Dependency Installation Start ---")

    get_pyvnt_version()
    if not ensure_pip():
        print("--- Dependency installation failed: pip unavailable ---")
        return False

    pip_path_added = False
    if PATHTOINSTALL not in sys.path:
        sys.path.insert(0, PATHTOINSTALL)
        pip_path_added = True
        print(f"Added '{PATHTOINSTALL}' to sys.path.")
    if pip_path_added:
        importlib.invalidate_caches()

    if not CUSTOM_MODULE_NAME or not CUSTOM_WHEEL_PATH:
         print("Skipping custom module wheel: Not configured.")
    elif not os.path.exists(CUSTOM_WHEEL_PATH):
         print(f"ERROR: Custom wheel file not found: {CUSTOM_WHEEL_PATH}")
         if addon_base_path and not os.path.exists(addon_base_path):
             print(f"Hint: The base addon directory was not found at {addon_base_path}")
    else:
        if is_module_importable(CUSTOM_MODULE_NAME, [PATHTOINSTALL]):
             print(f"Custom module '{CUSTOM_MODULE_NAME}' seems to be already importable.")
        else:
             print(f"Attempting to install custom module '{CUSTOM_MODULE_NAME}' from wheel: {os.path.basename(CUSTOM_WHEEL_PATH)}")
             success = run_pip_install([CUSTOM_WHEEL_PATH], PATHTOINSTALL, label="CustomWheel")
             if success:
                  print(f"pip command for custom wheel '{CUSTOM_MODULE_NAME}' completed successfully.")
             else:
                  print(f"ERROR: pip command for custom wheel '{CUSTOM_MODULE_NAME}' failed.")
    if restart_needed:
        print("Please restart the application or environment to apply the changes from the new 'pyvnt' module.")

    print("--- Running Final Checks ---")
    importlib.invalidate_caches()
    
    if is_module_importable(CUSTOM_MODULE_NAME, [PATHTOINSTALL]):
        return True
    else:
        return False