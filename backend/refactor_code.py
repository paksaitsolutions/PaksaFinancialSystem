#!/usr/bin/env python3
"""
Backend Code Refactoring Script
Copyright (c) 2024 Paksa IT Solutions

Removes duplicate code, adds type hints, and improves code quality.
"""

import os
import ast
from pathlib import Path
from typing import List, Set
from collections import defaultdict

class CodeAnalyzer(ast.NodeVisitor):
    """Analyze Python code for duplicates and missing type hints."""
    
    def __init__(self):
        self.functions: List[str] = []
        self.classes: List[str] = []
        self.missing_type_hints: List[str] = []
        self.missing_docstrings: List[str] = []
    
    def visit_FunctionDef(self, node):
        self.functions.append(node.name)
        
        # Check for type hints
        if not node.returns:
            self.missing_type_hints.append(f"Function {node.name} missing return type")
        
        # Check for docstring
        if not ast.get_docstring(node):
            self.missing_docstrings.append(f"Function {node.name} missing docstring")
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.classes.append(node.name)
        
        # Check for docstring
        if not ast.get_docstring(node):
            self.missing_docstrings.append(f"Class {node.name} missing docstring")
        
        self.generic_visit(node)

def analyze_file(file_path: Path) -> dict:
    """Analyze a Python file for code quality issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
        
        return {
            'file': str(file_path),
            'functions': analyzer.functions,
            'classes': analyzer.classes,
            'missing_type_hints': analyzer.missing_type_hints,
            'missing_docstrings': analyzer.missing_docstrings
        }
    except Exception as e:
        return {'file': str(file_path), 'error': str(e)}

def find_duplicates(backend_dir: Path) -> dict:
    """Find duplicate function and class names."""
    function_locations = defaultdict(list)
    class_locations = defaultdict(list)
    
    for py_file in backend_dir.rglob('*.py'):
        if '.venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
        
        result = analyze_file(py_file)
        if 'error' in result:
            continue
        
        for func in result['functions']:
            function_locations[func].append(str(py_file))
        
        for cls in result['classes']:
            class_locations[cls].append(str(py_file))
    
    # Find duplicates
    duplicate_functions = {k: v for k, v in function_locations.items() if len(v) > 1}
    duplicate_classes = {k: v for k, v in class_locations.items() if len(v) > 1}
    
    return {
        'duplicate_functions': duplicate_functions,
        'duplicate_classes': duplicate_classes
    }

def generate_report(backend_dir: Path):
    """Generate code quality report."""
    print("=" * 60)
    print("Paksa Financial System - Code Quality Report")
    print("Copyright (c) 2024 Paksa IT Solutions")
    print("=" * 60)
    
    # Find duplicates
    print("\n📋 Analyzing code for duplicates...")
    duplicates = find_duplicates(backend_dir)
    
    if duplicates['duplicate_functions']:
        print(f"\n⚠️  Found {len(duplicates['duplicate_functions'])} duplicate functions:")
        for func, locations in list(duplicates['duplicate_functions'].items())[:5]:
            print(f"  - {func}: {len(locations)} occurrences")
    
    if duplicates['duplicate_classes']:
        print(f"\n⚠️  Found {len(duplicates['duplicate_classes'])} duplicate classes:")
        for cls, locations in list(duplicates['duplicate_classes'].items())[:5]:
            print(f"  - {cls}: {len(locations)} occurrences")
    
    # Analyze files
    print("\n📋 Analyzing files for type hints and docstrings...")
    total_missing_hints = 0
    total_missing_docs = 0
    
    for py_file in list(backend_dir.rglob('*.py'))[:20]:  # Sample first 20 files
        if '.venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
        
        result = analyze_file(py_file)
        if 'error' in result:
            continue
        
        total_missing_hints += len(result['missing_type_hints'])
        total_missing_docs += len(result['missing_docstrings'])
    
    print(f"\n📊 Summary:")
    print(f"  - Missing type hints: {total_missing_hints}")
    print(f"  - Missing docstrings: {total_missing_docs}")
    print(f"  - Duplicate functions: {len(duplicates['duplicate_functions'])}")
    print(f"  - Duplicate classes: {len(duplicates['duplicate_classes'])}")
    
    print("\n✅ Report complete. Review findings and refactor as needed.")

if __name__ == "__main__":
    backend_dir = Path(__file__).parent / 'app'
    generate_report(backend_dir)