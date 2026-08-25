import os
import re

base_dir = "/mnt/NewVolume/code/unstructured_cf_mesh/week8/cfmesh_tools"
ops_orig = os.path.join(base_dir, "operators.py")
ops_dir = os.path.join(base_dir, "operators")

os.makedirs(ops_dir, exist_ok=True)

with open(ops_orig, "r") as f:
    text = f.read()

# ops_utils.py
utils_headers = """import bpy
import threading
from venturial.models.unstructured_properties import global_state
from .. import utils_system

"""
# Find run_command_async up to CFMESH_OT_ImportSTL
utils_match = re.search(r'(def run_command_async.*?)class CFMESH_OT_ImportSTL', text, re.DOTALL)
with open(os.path.join(ops_dir, "ops_utils.py"), "w") as f:
    f.write(utils_headers + utils_match.group(1).strip() + "\n")

# ops_meshing.py
meshing_headers = """import bpy
import os
from .ops_utils import run_command_async, set_ui_error, clear_ui_status
from venturial.models.unstructured_properties import global_state
from venturial.utils.unstructured import utils_mesh

"""
meshing_match = re.search(r'(class CFMESH_OT_ImportSTL.*?)class CFMESH_OT_RunSolver', text, re.DOTALL)
with open(os.path.join(ops_dir, "ops_meshing.py"), "w") as f:
    f.write(meshing_headers + meshing_match.group(1).strip() + "\n")

# ops_solver.py
solver_headers = """import bpy
import os
import math
from .ops_utils import run_command_async, set_ui_error, clear_ui_status
from venturial.models.unstructured_properties import global_state
from venturial.utils.unstructured import utils_mesh

"""
solver_match = re.search(r'(class CFMESH_OT_RunSolver.*?)class CFMESH_OT_LaunchParaView', text, re.DOTALL)
with open(os.path.join(ops_dir, "ops_solver.py"), "w") as f:
    f.write(solver_headers + solver_match.group(1).strip() + "\n")

# ops_postprocess.py
post_headers = """import bpy
import os
import math
from .ops_utils import set_ui_error, clear_ui_status
from venturial.models.unstructured_properties import global_state
from .. import utils_system

"""
post_match = re.search(r'(class CFMESH_OT_LaunchParaView.*)', text, re.DOTALL)
with open(os.path.join(ops_dir, "ops_postprocess.py"), "w") as f:
    f.write(post_headers + post_match.group(1).strip() + "\n")

# __init__.py
init_content = """from .ops_meshing import CFMESH_OT_ImportSTL, CFMESH_OT_GenerateCFMesh
from .ops_solver import CFMESH_OT_RunSolver
from .ops_postprocess import (
    CFMESH_OT_LaunchParaView,
    CFMESH_OT_LoadResult,
    CFMESH_OT_RunCheckMesh,
    CFMESH_OT_ShowResiduals,
    CFMESH_OT_ColorByField,
    CFMESH_OT_OpenExportDir
)
"""
with open(os.path.join(ops_dir, "__init__.py"), "w") as f:
    f.write(init_content)

print("Split generated successfully.")
