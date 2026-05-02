import ast
import requests
import sys
import re

# Extract imports from Python file
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


# Check if package exists on PyPI
def check_pypi(package):
    url = f"https://pypi.org/pypi/{package}/json"
    response = requests.get(url)
    return response.status_code == 200


def main():
    file_to_check = "app.py"
    packages = extract_imports(file_to_check)

    print(f"Checking dependencies: {packages}")

    failed = False

    for pkg in packages:
        if pkg in ["sys", "os"]:
            continue

        if is_suspicious(pkg):
            print(f"Suspicious package name detected: {pkg}")

        exists = check_pypi(pkg)

        if not exists:
            print(f"HALLUCINATION DETECTED: '{pkg}' NOT found on PyPI")
            failed = True
        else:
            print(f"{pkg} exists")

    if failed:
        print("\n Pipeline FAILED due to hallucinated dependencies")
        sys.exit(1)
    else:
        print("\n All dependencies are valid")


def is_suspicious(pkg):
    patterns = [
        r"ultimate",
        r"secure",
        r"pro",
        r"ai",
        r"nextgen",
        r"v\d+"
    ]

    for p in patterns:
        if re.search(p, pkg.lower()):
            return True
    return False


if __name__ == "__main__":
    main()