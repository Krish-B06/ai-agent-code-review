import os
import ast

def find_python_files(directory="src"):
    """Recursively find all Python files in a directory."""
    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
    return py_files

def get_exposed_definitions(filepath):
    """Parse a file to find defined classes and functions."""
    definitions = {"classes": set(), "functions": set()}
    try:
        with open(filepath, "r") as f:
            tree = ast.parse(f.read(), filename=filepath)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                definitions["classes"].add(node.name)
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                definitions["functions"].add(node.name)
    except Exception as e:
        print(f"Warning: Failed to parse definitions for {filepath}: {e}")
    return definitions

def find_relevant_callers(modified_files, search_directory="src"):
    """
    Scans the repository to identify which files import or use
    the classes/methods defined in the modified files.
    """
    all_repo_files = find_python_files(search_directory)
    if os.path.exists("tests"):
        all_repo_files.extend(find_python_files("tests"))
        
    callers_context = ""
    
    modified_defs = {"classes": set(), "functions": set()}
    for file in modified_files:
        if file.endswith(".py") and os.path.exists(file):
            defs = get_exposed_definitions(file)
            modified_defs["classes"].update(defs["classes"])
            modified_defs["functions"].update(defs["functions"])

    if not modified_defs["classes"] and not modified_defs["functions"]:
        return ""

    print(f"🔍 System definitions identified in modified files: {dict(modified_defs)}")

    for filepath in all_repo_files:
        if filepath in modified_files:
            continue
            
        try:
            with open(filepath, "r") as f:
                content = f.read()
                
            referenced_terms = []
            for class_name in modified_defs["classes"]:
                if class_name in content:
                    referenced_terms.append(class_name)
            for func_name in modified_defs["functions"]:
                if func_name in content:
                    referenced_terms.append(func_name)
                    
            if referenced_terms:
                print(f"📌 Found relevant caller: '{filepath}' references {referenced_terms}")
                callers_context += f"\n\n=== Surrounding Context: Caller File: {filepath} ===\n"
                callers_context += content
        except Exception as e:
            print(f"Warning: Failed to scan {filepath} for references: {e}")
            
    return callers_context
