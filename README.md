# Venturial: A Comprehensive GUI for OpenFOAM

Venturial is a Blender addon that alleviates the effort to build and manage OpenFOAM cases. 

Originally inspired by `reynolds-blender`, Venturial has evolved into a unified suite that merges three separate FOSSEE intern projects (`classy_blocks`, `openfoam_blender_bridge`, and `cfmesh`) into a single, cohesive, and easily extensible platform. It seeks to procedurally introduce OpenFOAM’s case-building process to newcomers through instructive interfaces, while retaining deep customization for experienced users.

The main features include:

1. **Structured Meshing:** Compose hexahedral primitives within Blender to procedurally generate `blockMesh` dictionaries.
2. **Unstructured Meshing:** Import CAD files into Blender and generate `snappyHexMesh` and `cfMesh` dictionaries using Venturial's geometry setup tools.
3. **Smart Dependency Sandboxing:** Venturial features a robust internal dependency manager that safely installs `numpy`, `scipy`, `pyvista`, `numba`, and `classy_blocks` directly into its own isolated folder, completely protecting your system Python and Blender installations from dependency conflicts.
4. **Post-Processing Integration:** Visualize mesh structural data and simulation results directly inside Blender with built-in ParaView launching and PyVista hooks.
5. **Solver Management:** Graphically customize solver parameters, use editable templates, and control/monitor solver execution.
6. **Geometry Conversion:** Import mesh dictionaries and convert geometry definitions to Blender-editable objects for real-time modification.

## Architecture & Testing
Venturial is built with a test-driven architecture designed to keep future features cheap to add and simple to test:

- **Strict Separation of Concerns:** UI code (`bpy`) is strictly separated from logic and computation. If a function computes a mesh or a dictionary, it never imports `bpy`.
- **The Testing Pyramid:** 
  - `tests/unit/`: Blazing fast, pure-Python tests for math and dictionary generation (runs without Blender).
  - `tests/integration/`: Headless Blender tests to verify UI registration and scene state updates.
  - `tests/e2e/`: Full OpenFOAM physical execution tests on the generated cases.
- **CI/CD Automation:** Every push, PR, and tag triggers a GitHub Actions pipeline (`.github/workflows/main.yml`) that validates the addon against the testing pyramid (running OpenFOAM via Docker) and automatically packages release zips.

## Installation

Venturial installs like most standard Blender addons, but comes with an automated dependency installer built into the UI.

1. Visit Blender's [Download page](https://www.blender.org/download/). (Venturial is tested on Blender 3.2.1 through Blender 5.1).
2. Download the `venturial.zip` package from the repository releases.
3. In Blender, go to **Edit >> Preferences >> Add-ons**. Click **Install**, locate the zip file, and enable the checkbox.
4. **Important:** Open the Venturial sidebar in the 3D Viewport. If you see a warning about missing dependencies, simply click the **"Install Python Dependencies"** button. Venturial will safely download and sandbox the required math libraries into its own folder in the background!

## Genesis

Venturial is inspired from [reynolds-blender](https://github.com/dmsurti/reynolds-blender), a reference implementation of [reynolds](https://github.com/dmsurti/reynolds). It is among the open-sourced software products built by the [FOSSEE](https://fossee.in/) project at [IIT Bombay](https://www.iitb.ac.in/) and managed by [CFD-FOSSEE Team](https://cfd.fossee.in/home). 

If you wish to contribute to Venturial or be a part of the development team, reach out to us at `contact-cfd@fossee.in`.

## Licensing
1. Venturial is a free and fully open-sourced software built by the FOSSEE project and licensed under GPL 3.0.
2. Venturial is not approved or endorsed by OpenLimited, producer and distributor of the OpenFOAM software via www.openfoam.com, and owner of the OPENFOAM® and OpenCFD® trademarks.
3. Copyright (c) 2023 FOSSEE, CFD-FOSSEE.

## Citations
Venturial is an ongoing project and has several papers associated with it:

- A poster about Venturial was published in the [Proceedings of the 23rd Python in Science Conference 2024, Tacoma Washington, USA](https://doi.org/10.25080/tpwg2365).  
- A short paper about Venturial's development process and history has been published in the [2023 IEEE T4E conference, Mumbai India](https://doi.org/10.5281/zenodo.14162151).  
- Venturial was first published in the [18th OpenFOAM Workshop (OFW) 2023, Genoa, Italy](https://oxford-abstracts.s3.amazonaws.com/83ca7ab4-c356-4411-be07-070eaeffd43a.pdf).
