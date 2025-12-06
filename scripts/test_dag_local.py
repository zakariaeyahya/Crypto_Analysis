"""
Quick local test script for DAG validation
Run this before building Docker image to catch errors early
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("=" * 70)
    print("LOCAL DAG VALIDATION TEST")
    print("=" * 70)
    
    # Test 1: Syntax check
    print("\n[1/4] Testing Python syntax...")
    dag_file = project_root / "airflow" / "dags" / "complete_crypto_pipeline_unified.py"
    
    try:
        with open(dag_file, 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, str(dag_file), 'exec')
        print("  ✓ Syntax is valid")
    except SyntaxError as e:
        print(f"  ✗ Syntax error: {e}")
        return False
    
    # Test 2: Import test
    print("\n[2/4] Testing imports...")
    try:
        # Test if we can import Airflow (might not be installed locally)
        try:
            from airflow import DAG
            from airflow.operators.python import PythonOperator
            print("  ✓ Airflow imports available")
        except ImportError:
            print("  ⚠ Airflow not installed locally (this is OK, will work in Docker)")
        
        # Test project imports
        sys.path.insert(0, str(project_root))
        from extraction.models.config import RedditConfig
        from extraction.services.reddit_extractor import RedditExtractor
        print("  ✓ Project modules importable")
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        print("  ⚠ Some imports may not be available locally but will work in Docker")
    
    # Test 3: Function definitions
    print("\n[3/4] Testing function definitions...")
    try:
        # Read the file and check function definitions exist
        with open(dag_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_functions = [
            'def extract_reddit_data',
            'def clean_reddit_data',
            'def analyze_sentiment'
        ]
        
        for func in required_functions:
            if func in content:
                print(f"  ✓ {func} found")
            else:
                print(f"  ✗ {func} missing")
                return False
        
    except Exception as e:
        print(f"  ✗ Error checking functions: {e}")
        return False
    
    # Test 4: DAG definition
    print("\n[4/4] Testing DAG definition...")
    try:
        with open(dag_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'dag = DAG(' in content or 'with DAG(' in content:
            print("  ✓ DAG definition found")
        else:
            print("  ✗ DAG definition not found")
            return False
        
        if 'extract_task' in content and 'clean_task' in content and 'sentiment_task' in content:
            print("  ✓ Task definitions found")
        else:
            print("  ✗ Task definitions missing")
            return False
        
        if 'extract_task >> clean_task >> sentiment_task' in content:
            print("  ✓ Task dependencies defined")
        else:
            print("  ⚠ Task dependencies might be missing")
        
    except Exception as e:
        print(f"  ✗ Error checking DAG definition: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✓ BASIC VALIDATION PASSED")
    print("=" * 70)
    print("\nNote: For full validation, run:")
    print("  python tests/test_dag_validation.py")
    print("\nOr test in Airflow UI after Docker build.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

