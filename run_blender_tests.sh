#!/bin/bash
# run_blender_tests.sh
# Shared wrapper for running headless blender integration tests with OpenFOAM sourced

# Source OpenFOAM environment if not already loaded (e.g. in a container)
if [ -f /usr/lib/openfoam/openfoam2312/etc/bashrc ]; then
    source /usr/lib/openfoam/openfoam2312/etc/bashrc
elif [ -f /opt/openfoam9/etc/bashrc ]; then
    source /opt/openfoam9/etc/bashrc
fi

# Run the provided arguments through blender in background
# Usage: ./run_blender_tests.sh ./blender-4.0.0-linux-x64/blender tests/integration/test_blender_integration.py
BLENDER_EXECUTABLE=$1
TEST_SCRIPT=$2

echo "Running headless Blender tests using $BLENDER_EXECUTABLE on $TEST_SCRIPT"
$BLENDER_EXECUTABLE -b -P $TEST_SCRIPT
