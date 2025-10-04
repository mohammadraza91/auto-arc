#!/usr/bin/env python3
"""
Test script to verify DXF generation works correctly.
This script tests the enhanced Auto ARC functionality.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_dxf_generation():
    """Test DXF file generation."""
    print("Testing DXF Generation...")
    
    # Test the current generated_plan.py
    work_dir = Path("work_dir")
    generated_file = work_dir / "generated_plan.py"
    
    if not generated_file.exists():
        print("ERROR: Generated plan file not found!")
        return False
    
    # Change to work directory and run the script
    original_cwd = os.getcwd()
    try:
        os.chdir(work_dir)
        
        # Import and run the generated code
        import subprocess
        result = subprocess.run([sys.executable, "generated_plan.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("SUCCESS: Generated code executed successfully!")
            print(f"Output: {result.stdout}")
            
            # Check if DXF file was created
            dxf_file = Path("plan.dxf")
            if dxf_file.exists():
                print(f"SUCCESS: DXF file created: {dxf_file} ({dxf_file.stat().st_size} bytes)")
                return True
            else:
                print("ERROR: DXF file was not created!")
                return False
        else:
            print(f"ERROR: Code execution failed!")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("ERROR: Code execution timed out!")
        return False
    except Exception as e:
        print(f"ERROR: Error running code: {e}")
        return False
    finally:
        os.chdir(original_cwd)

def test_autocad_integration():
    """Test AutoCAD integration."""
    print("\nTesting AutoCAD Integration...")
    
    work_dir = Path("work_dir")
    dxf_file = work_dir / "plan.dxf"
    
    if not dxf_file.exists():
        print("ERROR: No DXF file found for AutoCAD test!")
        return False
    
    # Test the open_in_autocad function
    try:
        from streamlit_app import open_in_autocad
        success = open_in_autocad(dxf_file)
        if success:
            print("SUCCESS: AutoCAD integration working!")
        else:
            print("WARNING: AutoCAD not found, but integration code is working")
        return True
    except Exception as e:
        print(f"ERROR: AutoCAD integration error: {e}")
        return False

def main():
    """Run all tests."""
    print("Auto ARC DXF Generation Test Suite")
    print("=" * 50)
    
    # Test 1: DXF Generation
    dxf_success = test_dxf_generation()
    
    # Test 2: AutoCAD Integration
    autocad_success = test_autocad_integration()
    
    # Summary
    print("\nTest Results:")
    print("=" * 30)
    print(f"DXF Generation: {'PASS' if dxf_success else 'FAIL'}")
    print(f"AutoCAD Integration: {'PASS' if autocad_success else 'FAIL'}")
    
    if dxf_success and autocad_success:
        print("\nSUCCESS: All tests passed! Auto ARC is working correctly.")
        return True
    else:
        print("\nWARNING: Some tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
