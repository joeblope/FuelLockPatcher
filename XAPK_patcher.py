import argparse
import time
import zipfile
import json
import xml.etree.ElementTree as ET
import subprocess
from typing import List, Tuple
import yaml
import os
import patches.AllowMockProvider
import shutil

KEYSTORE_PASSWORD = os.environ.get("KEYSTORE_PASSWORD","12345678")
KEYSTORE_NAME = os.environ.get("KEYSTORE_NAME","keystore.jks")

def copy_dir_no_overwrite(src, dst) -> Tuple[List, List]:
    conflicts = []
    added_files = []
    for root, dirs, files in os.walk(src):
        # Create destination directories if they don't exist
        rel_path = os.path.relpath(root, src)
        dest_dir = os.path.join(dst, rel_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # Copy files, but don't overwrite existing ones
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dest_dir, file)
            if not os.path.exists(dst_file):
                shutil.copy2(src_file, dst_file)
                added_files.append(dst_file)
            else:
                conflicts.append(dst_file)
    return conflicts, added_files

def extract_zip(xapk_path: str, out_dir: str = "decompressed"):
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    with zipfile.ZipFile(xapk_path, 'r') as zip_ref:
        zip_ref.extractall(out_dir)

jdk_bin_path = os.environ.get("JAVA_BIN", "jdk-22.0.2\\bin\\java.exe")
keytool_bin_path = os.environ.get("KEYTOOL_BIN","jdk-22.0.2\\bin\\keytool.exe")
apktool_path = "apktool_2.10.0.jar"
apksigner_path = os.environ.get("APKSIGNER_BIN","build-tools\\35.0.0\\apksigner.bat")
zipalign_path = os.environ.get("ZIPALIGN_BIN","build-tools\\35.0.0\\zipalign.exe")

use_aapt2 = True
copy_originial = False
no_src = False
resm = "keep"

assert os.path.exists(jdk_bin_path), "Java not found"
assert os.path.exists(keytool_bin_path), "Keytool not found"
assert os.path.exists(apktool_path), "APKTool not found"
assert os.path.exists(apksigner_path), "APKSigner not found"

def decompile(filepath: str,output_path: str = "decompiled", no_src: bool = no_src, resm: str = resm):
    assert os.path.exists(filepath), "File not found"
    assert filepath.endswith(".apk"), "File is not an APK"

    command = [jdk_bin_path, "-jar", apktool_path, "-f", "d", filepath, "-o", output_path]

    if no_src:
        command.append("--no-src")

    if resm != "remove":
        command.append(f"--resource-mode")
        command.append(resm)

    # Decompile the APK
    subprocess.run(command)

    # Return the decompiled path
    return output_path

def applyPatches(path: str = "decompiled"):
    assert os.path.exists(path), "Path not found"
    smali_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".smali"):
                smali_files.append(os.path.join(root, file))

    for smali_file in smali_files:
        with open(smali_file, "rb") as file:
            content = file.read()
        if b"isFromMockProvider" in content:
            print(f"Applying patch to {smali_file}")
            patches.AllowMockProvider.apply(smali_file)

def recompile(path: str = "decompiled", use_aapt2: bool = use_aapt2, copy_original: bool = copy_originial):
    assert os.path.exists(path), "Path not found"
    command = [jdk_bin_path, "-jar", apktool_path, "b", path]
    if use_aapt2:
        command.append("--use-aapt2")
    if copy_original:
        command.append("--copy-original")
    subprocess.run(command)


def genKeystore():
    #DONT USE
    # password and cert details need to be passed in
    # Generate a keystore
    subprocess.run([keytool_bin_path, "-genkey", "-v", "-keystore", KEYSTORE_NAME, "-keyalg", "RSA", "-keysize", "2048", "-validity", "10000", "-alias", "key"])


def sign(path: str,output_path: str = "signed.apk"):
    assert os.path.exists(path), "File not found"
    assert path.endswith(".apk"), "File is not an APK"

    # Sign the APK
    subprocess.run([apksigner_path, "sign", "--ks", KEYSTORE_NAME, "--ks-pass", f"pass:{KEYSTORE_PASSWORD}", "--out", output_path, path])

    return output_path

def verify(path: str):
    assert os.path.exists(path), "File not found"
    assert path.endswith(".apk"), "File is not an APK"

    # Verify the APK
    subprocess.run([apksigner_path, "verify", path])

def align(path: str,output_path: str = "aligned.apk"):
    assert os.path.exists(path), "File not found"
    assert path.endswith(".apk"), "File is not an APK"

    # Align the APK
    subprocess.run([zipalign_path, "-f", "-v", "4", path, output_path])
    return output_path

def patch_apk(apk_path: str, out_path: str = "modded.apk"):
    assert os.path.exists(apk_path), "File not found"
    assert apk_path.endswith(".apk"), "File is not an APK"

    decompile_dir = "decompiled"
    if os.path.exists(decompile_dir):
        shutil.rmtree(decompile_dir)

    decompile(apk_path, decompile_dir, no_src=False)
    applyPatches(decompile_dir)
    recompile(decompile_dir)
    aligned = align(os.path.join(f"{decompile_dir}/dist", os.path.basename(apk_path)))
    signed = sign(aligned, os.path.basename(apk_path))
    verify(signed)

    if signed != out_path:
        if os.path.exists(out_path):
            os.remove(out_path)
        os.rename(signed, out_path)

def decompile_xapk(xapk_path: str, out_dir: str = "decompiled"):
    assert os.path.exists(xapk_path), "File not found"
    assert xapk_path.endswith(".xapk"), "File is not an XAPK"
    decompressed_dir = "decompressed"
    extract_zip(xapk_path, decompressed_dir)

    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    # Decompile the apks
    for file in os.listdir(decompressed_dir):
        if file.endswith(".apk") and file:
            name = ".".join(file.split('.')[:-1])
            decompile(os.path.join(decompressed_dir,file), os.path.join(out_dir,name), no_src=True)

def patch_xapk(xapk_path: str, out_path: str = "modded.apk"):
    assert os.path.exists(xapk_path), "File not found"
    assert xapk_path.endswith(".xapk"), "File is not an XAPK"
    decompile_dir = "decompiled"

    decompile_xapk(xapk_path, decompile_dir)

    assert os.path.exists("decompressed/manifest.json"), "Manifest not found"
    with open("decompressed/manifest.json", "r") as file:
        manifest = json.load(file)
    assert "package_name" in manifest, "Package name not found"
    package_name = manifest["package_name"]

    conflicts = []
    added_files = []
    # Copy all the files from the other apks to the base apk
    for file in os.listdir(decompile_dir):
        if file == package_name or not os.path.isdir(os.path.join(decompile_dir,file)):
            continue
        print(f"Copying files from {file} to {package_name}")
        conf, added = copy_dir_no_overwrite(os.path.join(decompile_dir,file), os.path.join(decompile_dir,package_name))
        conflicts.extend(conf)
        added_files.extend(added)
    print(f"Conflicts: {conflicts}")
    print(f"Added files: {added_files}")


    # Modify the apktool.yml file and add all other apks doNotCompress
    with open(os.path.join(decompile_dir,package_name,"apktool.yml"), "r") as file:
        yml = yaml.load(file, Loader=yaml.FullLoader)

    do_not_compress = yml.get("doNotCompress", [])
    for file in os.listdir(decompile_dir):
        if file == package_name or not os.path.isdir(os.path.join(decompile_dir,file)):
            continue
        with open(os.path.join(decompile_dir,file,"apktool.yml"), "r") as file:
            yml_file = yaml.load(file, Loader=yaml.FullLoader)
        file_do_not_compress = yml_file.get("doNotCompress", [])
        for f in file_do_not_compress:
            if f not in do_not_compress:
                do_not_compress.append(f)
    print(f"doNotCompress: {do_not_compress}")
    yml["doNotCompress"] = do_not_compress
    with open(os.path.join(decompile_dir,package_name,"apktool.yml"), "w") as file:
        yaml.dump(yml, file)

    # Combine all values in the apks
    for file in os.listdir(decompile_dir):
        if file == package_name or not os.path.isdir(os.path.join(decompile_dir,file)):
            continue
        if not os.path.exists(os.path.join(decompile_dir,file,"res","values")):
            print(f"Values not found in {file}")
            continue
        for values_file in os.listdir(os.path.join(decompile_dir,file,"res","values")):
            if not values_file.endswith(".xml"):
                continue

            src_values = ET.parse(os.path.join(decompile_dir,package_name,"res","values",values_file))
            src_values_root = src_values.getroot()

            dest_values = ET.parse(os.path.join(decompile_dir,file,"res","values",values_file))
            dest_values_root = dest_values.getroot()

            for child in list(dest_values_root):
                existing = [src_value for src_value in list(src_values_root) if
                            src_value.attrib['name'] == child.attrib['name'] and src_value.attrib['type'] ==
                            child.attrib['type']]
                if len(existing) > 0:
                    existing = [x.attrib for x in existing if x.attrib['id'] != child.attrib['id']]
                    if len(existing) > 0:
                        print(f"Value {child.attrib['name']} already exists in {package_name}")
                        print(f"Existing values:{existing}")
                        print(f"New value:{child.attrib}")
                else:
                    src_values_root.append(child)

            src_values.write(os.path.join(decompile_dir,package_name,"res","values",values_file), encoding='utf-8',
                             xml_declaration=True)

    # Recompile the APK with keep original
    recompile(path=os.path.join(decompile_dir,package_name), copy_original=True)
    aligned = align(os.path.join(decompile_dir, package_name, "dist", f"{package_name}.apk"),
                    f"{package_name}.apk")
    signed = sign(aligned, f"{package_name}.apk")
    verify(signed)

    # Because we've added new value strings, we need to decode the manifest again
    # Decompile base apk
    decompile(signed, os.path.join(decompile_dir,package_name), no_src=False)

    # Remove all split related attributes from the manifest
    assert os.path.exists(os.path.join(decompile_dir,package_name,"AndroidManifest.xml")), "Manifest not found"
    # Parse the AndroidManifest.xml file
    tree = ET.parse(os.path.join(decompile_dir,package_name,"AndroidManifest.xml"))
    root = tree.getroot()

    # Register the namespaces in the document to preserve them
    namespaces = {
        node[0]: node[1] for _, node in ET.iterparse(
            os.path.join(decompile_dir,package_name,"AndroidManifest.xml"), events=['start-ns']
        )
    }
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)

    # Process the XML, removing "isSplitRequired"
    children = list(root)
    children.append(root)
    while len(children) > 0:
        child = children.pop(0)
        print(child.attrib)

        to_remove = []
        for attribute in child.attrib:
            if "isSplitRequired" in attribute:
                to_remove.append(attribute)
            elif "requiredSplitTypes" in attribute:
                to_remove.append(attribute)
            elif "splitTypes" in attribute:
                to_remove.append(attribute)
        for attribute in to_remove:
            del child.attrib[attribute]
        children.extend(list(child))

    # Write the modified XML back to file, preserving namespaces
    tree.write(os.path.join(decompile_dir,package_name,"AndroidManifest.xml"), encoding='utf-8', xml_declaration=True)

    # Apply patches
    applyPatches(os.path.join(decompile_dir,package_name))

    # Recompile the APK without keep original
    recompile(path=os.path.join(decompile_dir,package_name), copy_original=False)
    aligned = align(os.path.join("decompiled", package_name, "dist", f"{package_name}.apk"),
                    f"{package_name}.apk")
    signed = sign(aligned, f"{package_name}.apk")
    verify(signed)
    if signed != out_path:
        if os.path.exists(out_path):
            os.remove(out_path)
        os.rename(signed, out_path)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Patches an apk to remove mock location checks')
    parser.add_argument('--input', '-i', type=str, help='The path to the APK file',
                        required=True)
    parser.add_argument('--output', '-o', type=str, help='Output path of patched APK file',
                        required=True)
    args = parser.parse_args()

    # Get the version of the APK
    if not os.path.exists(args.input):
        print("APK file not found")
        exit(1)
    if not args.input.endswith(".apk") and not args.input.endswith(".xapk"):
        print("File is not an APK")
        exit(1)

    source = args.input
    filename = ".".join(os.path.basename(source).split('.')[:-1])
    output = args.output

    start = time.time()
    if source.endswith(".xapk"):
        patch_xapk(source, output)
    elif source.endswith(".apk"):
        patch_apk(source, output)
    else:
        print("Invalid file type")
        exit(1)

    print(f"Time taken: {time.time()-start}")

