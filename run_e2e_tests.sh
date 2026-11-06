#!/bin/bash
# run_e2e_tests.sh
# End-to-End test runner for OpenFOAM physical validation inside Docker container

set -e

echo "=== Sourcing OpenFOAM Environment ==="
if [ -f /usr/lib/openfoam/openfoam2312/etc/bashrc ]; then
    source /usr/lib/openfoam/openfoam2312/etc/bashrc
elif [ -f /usr/lib/openfoam/openfoam2412/etc/bashrc ]; then
    source /usr/lib/openfoam/openfoam2412/etc/bashrc
elif [ -f /opt/openfoam9/etc/bashrc ]; then
    source /opt/openfoam9/etc/bashrc
elif [ -f /usr/local/openfoam/etc/bashrc ]; then
    source /usr/local/openfoam/etc/bashrc
fi

echo "OpenFOAM version check:"
which blockMesh || true
which checkMesh || true

echo "=== Running E2E Test Suite ==="
python3 tests/e2e/test_openfoam_mesh.py

