"""
Test script to verify file system operations.
"""
import os

def test_filesystem():
    # Get current working directory
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    
    # List files in current directory
    print("\nFiles in current directory:")
    for f in os.listdir('.'):
        print(f"- {f} (dir)" if os.path.isdir(f) else f"- {f}")
    
    # Try to create a test file
    test_file = "test_fs_output.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("This is a test file.\n")
        print(f"\n✅ Successfully created test file: {os.path.abspath(test_file)}")
        
        # Verify file exists
        if os.path.exists(test_file):
            print(f"✅ Verified file exists. Size: {os.path.getsize(test_file)} bytes")
            
            # Read file content
            with open(test_file, 'r') as f:
                content = f.read()
                print(f"✅ File content: {content.strip()}")
                
            # Delete test file
            os.remove(test_file)
            print(f"✅ Test file removed successfully")
        else:
            print("❌ Test file was not created")
            
    except Exception as e:
        print(f"\n❌ Error during file operations: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_filesystem()
