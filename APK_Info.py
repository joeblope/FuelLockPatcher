import subprocess
import os
import argparse
import zipfile
import json

AAPT2_PATH = os.environ.get("AAPT2_BIN","build-tools/35.0.0/aapt2.exe")

# Helper function to run aapt2 and extract specific values
def run_aapt2(apk_path, key,separator="'"):
    command = [AAPT2_PATH, "dump", "badging", apk_path]
    result = subprocess.run(command, stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    for line in output.split("\n"):
        if key in line:
            return line.split(key)[1].split(separator)[1]
    return None

# Optimized APK functions
def get_apk_package_name(apk_path):
    return run_aapt2(apk_path, "name")

def get_apk_version(apk_path):
    return run_aapt2(apk_path, "versionName")

def get_apk_version_code(apk_path):
    return run_aapt2(apk_path, "versionCode")

def get_apk_min_sdk_version(apk_path):
    return run_aapt2(apk_path, "minSdkVersion")

def get_apk_target_sdk_version(apk_path):
    return run_aapt2(apk_path, "targetSdkVersion")

def get_apk_app_name(apk_path):
    return run_aapt2(apk_path, "application-label")

def get_apk_architectures(apk_path):
    return run_aapt2(apk_path, "native-code",separator=":")

def get_apk_densities(apk_path):
    return run_aapt2(apk_path, "densities",separator=":")

# Helper function to extract data from XAPK manifest.json
def read_xapk_manifest(xapk_path, key):
    with zipfile.ZipFile(xapk_path, 'r') as zip_ref:
        with zip_ref.open("manifest.json") as file:
            manifest = json.load(file)
            return manifest.get(key)

# Optimized XAPK functions
def get_xapk_package_name(xapk_path):
    return read_xapk_manifest(xapk_path, "package_name")

def get_xapk_version(xapk_path):
    return read_xapk_manifest(xapk_path, "version_name")

def get_xapk_version_code(xapk_path):
    return read_xapk_manifest(xapk_path, "version_code")

def get_xapk_min_sdk_version(xapk_path):
    return read_xapk_manifest(xapk_path, "min_sdk_version")

def get_xapk_target_sdk_version(xapk_path):
    return read_xapk_manifest(xapk_path, "target_sdk_version")

def get_xapx_app_name(xapk_path):
    return read_xapk_manifest(xapk_path, "name")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Gets the package info of an APK')
    parser.add_argument('--input', '-i', type=str, help='The path to the APK file',
                        required=True)
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print("APK file not found")
        exit(1)
    if not args.input.endswith(".apk") and not args.input.endswith(".xapk"):
        print("File is not an APK")
        exit(1)

    # Defaults
    package_version = ""
    package_name = ""
    version_code = ""
    min_sdk_version = ""
    target_sdk_version = ""
    app_name = ""
    architectures = ""
    densities = ""
    apk_type = ""

    if args.input.endswith(".apk"):
        package_version = get_apk_version(args.input)
        package_name = get_apk_package_name(args.input)
        version_code = get_apk_version_code(args.input)
        min_sdk_version = get_apk_min_sdk_version(args.input)
        target_sdk_version = get_apk_target_sdk_version(args.input)
        app_name = get_apk_app_name(args.input)
        architectures = get_apk_architectures(args.input)
        densities = get_apk_densities(args.input)
        apk_type = "APK"
    elif args.input.endswith(".xapk"):
        package_version = get_xapk_version(args.input)
        package_name = get_xapk_package_name(args.input)
        version_code = get_xapk_version_code(args.input)
        min_sdk_version = get_xapk_min_sdk_version(args.input)
        target_sdk_version = get_xapk_target_sdk_version(args.input)
        app_name = get_xapx_app_name(args.input)
        apk_type = "XAPK"

    assert package_version != "", "Unable to determine package version"
    assert package_name != "", "Unable to determine package name"
    assert apk_type != "", "Unable to determine apk type"
    print(f"Package Version: {package_version}")
    print(f"Package Name: {package_name}")
    print(f"Version Code: {version_code}")
    print(f"Min SDK Version: {min_sdk_version}")
    print(f"Target SDK Version: {target_sdk_version}")
    print(f"App Name: {app_name}")
    print(f"Architectures: {architectures}")
    print(f"Densities: {densities}")
    print(f"Apk Type: {apk_type}")
    if 'GITHUB_OUTPUT' in os.environ:
        print("Added to GITHUB_OUTPUT")
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            print(f'apk_version={package_version}', file=fh)
            print(f'apk_package_name={package_name}', file=fh)
            print(f'apk_version_code={version_code}', file=fh)
            print(f'apk_min_sdk_version={min_sdk_version}', file=fh)
            print(f'apk_target_sdk_version={target_sdk_version}', file=fh)
            print(f'apk_app_name={app_name}', file=fh)
            print(f'apk_architectures={architectures}', file=fh)
            print(f'apk_densities={densities}', file=fh)
            print(f'apk_type={apk_type}', file=fh)
    else:
        print("Not added to GITHUB_OUTPUT")
