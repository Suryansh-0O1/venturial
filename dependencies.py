import bpy
import sys
import os
import subprocess
import ensurepip
import importlib


PATHTOINSTALL = bpy.utils.user_resource("SCRIPTS", path="modules")

addon_dir_name = "venturial"

# 3. Paths derived from addon structure
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

def read_required_modules_from_reqs():
    """Parses requirements.txt, returns list of import names (maps pyyaml->yaml)."""
    module_name_map = {'pyyaml': 'yaml'}
    modules = []
    if REQUIREMENTS_PATH is None or not os.path.exists(REQUIREMENTS_PATH):
        print(f"Requirements file not found or path not configured: {REQUIREMENTS_PATH}")
        return modules
    try:
        with open(REQUIREMENTS_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    package_name = line.split("==")[0].split(">=")[0].split("<=")[0].split("!=")[0].split("~=")[0].strip()
                    if package_name:
                         import_name = module_name_map.get(package_name.lower(), package_name)
                         modules.append(import_name)
            return modules
    except Exception as e:
        print(f"Error reading requirements file {REQUIREMENTS_PATH}: {e}")
        return []

def is_module_importable(module_name, search_paths=None):
    """Checks if a module can be imported. Handles 'pyyaml' -> 'yaml'."""
    original_name = module_name
    if module_name.lower() == 'pyyaml':
        module_name = 'yaml'

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
    print("\n--- Dependency Installation Start (reqs + wheel) ---")

    if not ensure_pip():
        print("--- Dependency installation failed: pip unavailable ---")
        return False

    # 2. Add target path to sys.path
    pip_path_added = False
    if PATHTOINSTALL not in sys.path:
        sys.path.insert(0, PATHTOINSTALL)
        pip_path_added = True
        print(f"Added '{PATHTOINSTALL}' to sys.path.")
    if pip_path_added:
        importlib.invalidate_caches()

    # 3. Install from requirements.txt
    pip_reqs_succeeded = True
    modules_installed_from_reqs = False
    if REQUIREMENTS_PATH is None or not os.path.exists(REQUIREMENTS_PATH):
         print("Skipping requirements.txt: File not found or path not configured.")
    else:
        modules_from_reqs = read_required_modules_from_reqs()
        if not modules_from_reqs:
            print("No modules found in requirements.txt or failed to read.")
        else:
            print(f"Checking required modules from requirements.txt: {modules_from_reqs}")
            missing_initially = [m for m in modules_from_reqs if not is_module_importable(m, [PATHTOINSTALL])]
            if not missing_initially:
                print("All modules from requirements.txt seem to be installed and importable.")
            else:
                print(f"Missing modules found: {missing_initially}. Attempting installation from requirements.txt...")
                success = run_pip_install(["-r", REQUIREMENTS_PATH], PATHTOINSTALL, label="Requirements")
                if success:
                    print("pip command for requirements.txt completed successfully.")
                    modules_installed_from_reqs = True
                    restart_needed = True
                else:
                    print("ERROR: pip command for requirements.txt failed.")
                    pip_reqs_succeeded = False

    # 4. Install custom wheel
    pip_custom_succeeded = True
    custom_module_installed_this_run = False
    if not pip_reqs_succeeded:
         print("Skipping custom module wheel installation due to previous errors.")
         pip_custom_succeeded = False
    elif not CUSTOM_MODULE_NAME or not CUSTOM_WHEEL_PATH:
         print("Skipping custom module wheel: Not configured.")
    elif not os.path.exists(CUSTOM_WHEEL_PATH):
         print(f"ERROR: Custom wheel file not found: {CUSTOM_WHEEL_PATH}")
         # Check if the base addon path exists, helps debugging path issues
         if addon_base_path and not os.path.exists(addon_base_path):
             print(f"Hint: The base addon directory was not found at {addon_base_path}")
         pip_custom_succeeded = False
    else:
        # Check if already importable (maybe installed in a previous run)
        # Note: if you *always* want to force install from the wheel, remove this check
        if is_module_importable(CUSTOM_MODULE_NAME, [PATHTOINSTALL]):
             print(f"Custom module '{CUSTOM_MODULE_NAME}' seems to be already importable.")
             # Optionally, force upgrade?
             # print(f"Attempting upgrade for '{CUSTOM_MODULE_NAME}' from wheel...")
             # success = run_pip_install([CUSTOM_WHEEL_PATH], PATHTOINSTALL, label="CustomWheelUpgrade")
             # if not success: pip_custom_succeeded = False # etc.
        else:
             print(f"Attempting to install custom module '{CUSTOM_MODULE_NAME}' from wheel: {os.path.basename(CUSTOM_WHEEL_PATH)}")
             success = run_pip_install([CUSTOM_WHEEL_PATH], PATHTOINSTALL, label="CustomWheel")
             if success:
                  print(f"pip command for custom wheel '{CUSTOM_MODULE_NAME}' completed successfully.")
                  custom_module_installed_this_run = True
                  restart_needed = True
             else:
                  print(f"ERROR: pip command for custom wheel '{CUSTOM_MODULE_NAME}' failed.")
                  pip_custom_succeeded = False

    print("--- Running Final Checks ---")
    importlib.invalidate_caches()
    overall_pip_success = pip_reqs_succeeded and pip_custom_succeeded
    final_import_check_passed = True
    modules_to_check = read_required_modules_from_reqs()
    if CUSTOM_MODULE_NAME and CUSTOM_MODULE_NAME not in modules_to_check:
         modules_to_check.append(CUSTOM_MODULE_NAME)

    if not modules_to_check:
        print("No modules specified for final check.")
    else:
        print("Verifying imports after installation attempt...")
        still_missing_final = []
        for m in modules_to_check:
             if not is_module_importable(m, [PATHTOINSTALL]):
                  is_req_module = m != CUSTOM_MODULE_NAME
                  if (is_req_module and pip_reqs_succeeded) or (not is_req_module and pip_custom_succeeded):
                       still_missing_final.append(m)
                       final_import_check_passed = False
        if still_missing_final:
             print(f"WARNING: Some modules installed by pip are not immediately importable: {still_missing_final}")
             print("This often requires a Blender restart for the changes to take full effect.")
             restart_needed = True
        elif overall_pip_success:
             print("All required modules appear to be installed and importable.")

    if overall_pip_success:
        print("--- Dependency installation process finished based on pip command success. ---")
        if restart_needed:
             print("*** Please restart Blender to ensure all dependencies are loaded correctly. ")
        return True # Return True because pip commands succeeded
    else:
        print("--- Dependency installation failed due to pip errors. See logs above. ---")
        return False # Return False because pip commands failed
