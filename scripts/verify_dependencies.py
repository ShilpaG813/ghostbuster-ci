import ast
import requests
import sys
import re
import json

# -------------------------------
# Extract imported packages
# -------------------------------
def extract_imports(file_path):
    with open(file_path, "r") as f:
        tree = ast.parse(f.read())

    packages = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                packages.add(n.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                packages.add(node.module.split('.')[0])

    return packages


# -------------------------------
# Extract imported functions
# -------------------------------
def extract_functions(file_path):
    with open(file_path, "r") as f:
        tree = ast.parse(f.read())

    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module
            for name in node.names:
                functions.append((module, name.name))

    return functions


# -------------------------------
# Check PyPI package existence
# -------------------------------
def check_pypi(package):
    url = f"https://pypi.org/pypi/{package}/json"
    return requests.get(url).status_code == 200


# -------------------------------
# Check if function exists in module
# -------------------------------
def function_exists(module, func):
    try:
        imported_module = __import__(module, fromlist=[func])
        return hasattr(imported_module, func)
    except:
        return False


# -------------------------------
# Detect suspicious names
# -------------------------------
def is_suspicious(pkg):
    patterns = ["ultimate", "secure", "pro", "ai", "nextgen", "v"]
    return any(p in pkg.lower() for p in patterns)


# -------------------------------
# MAIN FUNCTION
# -------------------------------
def main():
    file_to_check = "app.py"

    packages = extract_imports(file_to_check)
    functions = extract_functions(file_to_check)

    report = {
        "packages_checked": list(packages),
        "issues": [],
        "result": "PASS"
    }

    print(f"\n Checking dependencies: {packages}\n")

    # -------------------------------
    # Package Validation
    # -------------------------------
    for pkg in packages:
        if pkg in ["sys", "os"]:
            continue

        if is_suspicious(pkg):
            print(f" Suspicious package name: {pkg}")

        exists = check_pypi(pkg)

        if not exists:
            print(f" HALLUCINATION DETECTED: {pkg}")

            report["issues"].append({
                "type": "package",
                "name": pkg,
                "status": "not_found",
                "reason": "Possible AI hallucination"
            })

            report["result"] = "FAIL"
        else:
            print(f" {pkg} exists")

    # -------------------------------
    # Function Validation
    # -------------------------------
    print("\n Checking function imports...\n")

    for module, func in functions:
        if module:
            exists = function_exists(module, func)

            if not exists:
                print(f" FUNCTION HALLUCINATION: {func} not found in {module}")

                report["issues"].append({
                    "type": "function",
                    "module": module,
                    "function": func,
                    "status": "not_found",
                    "reason": "AI hallucinated function"
                })

                report["result"] = "FAIL"
            else:
                print(f" {func} exists in {module}")

    # -------------------------------
    # Save Report
    # -------------------------------
    with open("report.json", "w") as f:
        json.dump(report, f, indent=4)

    # -------------------------------
    # Final Result
    # -------------------------------
    if report["result"] == "FAIL":
        print("\n❌ Pipeline FAILED")
        sys.exit(1)
    else:
        print("\n All checks passed")


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    main()