import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_pip():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
        return True
    except subprocess.CalledProcessError:
        return False

def check_python_version():
    if sys.version_info.major != 3:
        print("Python 3 is required. Please install Python 3 and try again.")
        sys.exit(1)

def main():
    check_python_version()

    if not check_pip():
        print("pip is not installed or not working. Please install pip and try again.")
        sys.exit(1)

    packages = [
        'tkinter',
        'threading',
        'webbrowser',
        'utm',
        'geopandas',
        'os',
        'csv',
        'time',
        'shapely',
        'requests',
        'pyarrow'
    ]

    for package in packages:
        try:
            __import__(package)
        except ImportError:
            install(package)

    # Custom modules (assuming they are in the same directory)
    custom_modules = [
        'get_elevation',
        'get_state_county',
        'get_plss_data',
        'get_watershed_info',
        'generate_google_maps_link',
        'convert_latlon_utm'
    ]

    for module in custom_modules:
        try:
            __import__(module)
        except ImportError:
            print(f"Module {module} is not found. Ensure it is available in the script's directory.")

    print("All packages are installed and ready to use.")

if __name__ == "__main__":
    main()
