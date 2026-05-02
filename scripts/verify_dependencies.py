import ast
import requests
import sys
import re
import json

# Extract imports
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


# Check PyPI
def check_pypi(package):
    url = f"https://pypi.org/pypi/{package}/json"
    return requests.get(url).status_code == 200


# Suspicious pattern detection
def is_suspicious(pkg):
    patterns = ["ultimate", "secure", "pro", "ai", "nextgen", "v"]
    return any(p in pkg.lower() for p in patterns)


# MAIN FUNCTION (this was missing)
def main():
    file_to_check = "app.py"
    packages = extract_imports(file_to_check)

    report = {
        "packages_checked": list(packages),
        "issues": [],
        "result": "PASS"
    }

    print(f" Checking dependencies: {packages}")

    for pkg in packages:
        if pkg in ["sys", "os"]:
            continue

        suspicious = is_suspicious(pkg)
        exists = check_pypi(pkg)

        if suspicious:
            print(f" Suspicious package: {pkg}")

        if not exists:
            print(f" HALLUCINATION DETECTED: {pkg}")

            report["issues"].append({
                "package": pkg,
                "status": "not_found",
                "reason": "Possible AI hallucination"
            })

            report["result"] = "FAIL"
        else:
            print(f"{pkg} exists")

    # Save report
    with open("report.json", "w") as f:
        json.dump(report, f, indent=4)

    if report["result"] == "FAIL":
        print("\n Pipeline FAILED")
        sys.exit(1)
    else:
        print("\n All dependencies valid")


# THIS LINE RUNS EVERYTHING
if __name__ == "__main__":
    main()