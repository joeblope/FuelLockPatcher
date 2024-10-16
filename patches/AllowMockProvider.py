import os
import re
def apply(path: str):
    assert os.path.exists(path), "File not found"
    assert path.endswith(".smali"), "File is not a Smali file"

    # Read the file
    with open(path, "r") as file:
        content = file.read()
    output = []
    replace_result = False
    for line in content.split("\n"):
        if "isFromMockProvider" in line and "invoke-virtual" in line:
            output.append(line)
            replace_result = True
        elif "isFromMockProvider" in line and "invoke-static" in line:
            output.append(line)
            replace_result = True
        elif "isFromMockProvider" in line and "invoke-direct" in line:
            output.append(line)
            replace_result = True
        elif replace_result and "move-result" in line:
            if " # patched" in line:
                output.append(line)
                replace_result = False
                continue

            output.append(line+" # patched")

            #find out the register number
            register = line.split("move-result ")[1]

            # overwrite the register with 0
            output.append(f"const/4 {register}, 0x0 # patch")

            replace_result = False
        else:
            output.append(line)
    # Write
    with open(path+"", "w") as file:
        file.write("\n".join(output))
