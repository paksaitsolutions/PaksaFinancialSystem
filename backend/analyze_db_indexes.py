import os
import re
from pathlib import Path

def analyze_models():
    """Analyze SQLAlchemy models for missing indexes"""
    models_path = Path("app/models")
    
    results = {
        "foreign_keys_without_index": [],
        "date_fields_without_index": [],
        "status_fields_without_index": [],
        "models_analyzed": 0
    }
    
    for model_file in models_path.glob("*.py"):
        if model_file.name.startswith("__"):
            continue
            
        try:
            content = model_file.read_text(encoding='utf-8')
            results["models_analyzed"] += 1
            
            # Find all Column definitions
            columns = re.findall(r'(\w+)\s*=\s*Column\((.*?)\)', content, re.DOTALL)
            
            for col_name, col_def in columns:
                # Check for foreign keys without index
                if 'ForeignKey' in col_def and 'index=True' not in col_def:
                    results["foreign_keys_without_index"].append({
                        "file": model_file.name,
                        "column": col_name
                    })
                
                # Check for date fields without index
                if any(dt in col_def for dt in ['DateTime', 'Date']) and 'index=True' not in col_def:
                    if any(name in col_name.lower() for name in ['date', 'created', 'updated', 'modified']):
                        results["date_fields_without_index"].append({
                            "file": model_file.name,
                            "column": col_name
                        })
                
                # Check for status fields without index
                if 'status' in col_name.lower() and 'index=True' not in col_def:
                    results["status_fields_without_index"].append({
                        "file": model_file.name,
                        "column": col_name
                    })
                    
        except Exception as e:
            pass
    
    return results

if __name__ == "__main__":
    print("Analyzing database models for optimization opportunities...\n")
    results = analyze_models()
    
    print(f"Models analyzed: {results['models_analyzed']}\n")
    
    print(f"1. FOREIGN KEYS WITHOUT INDEX: {len(results['foreign_keys_without_index'])}")
    for item in results['foreign_keys_without_index'][:20]:
        print(f"   - {item['file']}: {item['column']}")
    if len(results['foreign_keys_without_index']) > 20:
        print(f"   ... and {len(results['foreign_keys_without_index']) - 20} more")
    
    print(f"\n2. DATE FIELDS WITHOUT INDEX: {len(results['date_fields_without_index'])}")
    for item in results['date_fields_without_index'][:20]:
        print(f"   - {item['file']}: {item['column']}")
    if len(results['date_fields_without_index']) > 20:
        print(f"   ... and {len(results['date_fields_without_index']) - 20} more")
    
    print(f"\n3. STATUS FIELDS WITHOUT INDEX: {len(results['status_fields_without_index'])}")
    for item in results['status_fields_without_index'][:20]:
        print(f"   - {item['file']}: {item['column']}")
    if len(results['status_fields_without_index']) > 20:
        print(f"   ... and {len(results['status_fields_without_index']) - 20} more")
    
    print(f"\n\nTOTAL MISSING INDEXES: {len(results['foreign_keys_without_index']) + len(results['date_fields_without_index']) + len(results['status_fields_without_index'])}")
