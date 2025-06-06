#!/bin/bash

# Ensure the script exits on error
set -e

# Define variables
MAIN_PY="main.py"
OUTPUT_DIR="tools"
OUTPUT_EXE="MixPlanApp"

# Activate the venv
if [ -d "../.venv" ]; then
    echo "Activating virtual environment..."
    source ../.venv/Scripts/activate
else
    echo "Virtual environment not found. Please create it first."
    exit 1
fi

# Check if pyinstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller is not installed. Installing it now..."
    pip install pyinstaller
fi

# Build the .exe using PyInstaller, no verbose output
echo "Building $MAIN_PY into $OUTPUT_EXE..."
pyinstaller --onefile --name "$OUTPUT_EXE" "$MAIN_PY" --log-level=ERROR --windowed --hidden-import=sklearn.externals.array_api_compat.numpy.fft

# Move the built .exe to the output directory
mkdir -p "$OUTPUT_DIR"
mv "dist/$OUTPUT_EXE" "$OUTPUT_DIR"

# Cleanup build artifacts
rm -rf build "$MAIN_PY.spec" dist

echo "Build complete. The executable is located at $OUTPUT_DIR/$OUTPUT_EXE.exe"

# Deactivate the virtual environment
deactivate
echo "Virtual environment deactivated."
echo "Done."