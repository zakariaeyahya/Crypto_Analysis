"""
Test script to validate DAG before building Docker image
Tests DAG parsing, task definitions, and basic execution
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_dag_import():
    """Test that DAG can be imported without errors"""
    try:
        from airflow import DAG
        from airflow.dags.complete_crypto_pipeline_unified import dag
        
        print("✓ DAG imported successfully")
        print(f"  DAG ID: {dag.dag_id}")
        print(f"  Tasks: {len(dag.tasks)}")
        return True
    except Exception as e:
        print(f"✗ DAG import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dag_structure():
    """Test DAG structure and task dependencies"""
    try:
        from airflow.dags.complete_crypto_pipeline_unified import dag
        
        # Check tasks exist
        task_ids = [task.task_id for task in dag.tasks]
        expected_tasks = ['extract_reddit', 'clean_data', 'analyze_sentiment']
        
        print("\n✓ DAG Structure:")
        print(f"  Tasks found: {task_ids}")
        
        for expected_task in expected_tasks:
            if expected_task in task_ids:
                print(f"  ✓ Task '{expected_task}' exists")
            else:
                print(f"  ✗ Task '{expected_task}' missing")
                return False
        
        # Check dependencies
        print("\n✓ Task Dependencies:")
        for task in dag.tasks:
            upstream = [t.task_id for t in task.upstream_task_ids]
            downstream = [t.task_id for t in task.downstream_task_ids]
            print(f"  {task.task_id}: upstream={upstream}, downstream={downstream}")
        
        return True
    except Exception as e:
        print(f"✗ DAG structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dag_parsing():
    """Test that DAG can be parsed by Airflow"""
    try:
        from airflow.models import DagBag
        
        dag_folder = project_root / "airflow" / "dags"
        dagbag = DagBag(dag_folder=str(dag_folder), include_examples=False)
        
        print("\n✓ DAG Parsing:")
        print(f"  DAGs found: {len(dagbag.dags)}")
        
        if 'complete_crypto_pipeline_unified' in dagbag.dags:
            print("  ✓ DAG 'complete_crypto_pipeline_unified' found")
            
            dag = dagbag.get_dag('complete_crypto_pipeline_unified')
            if dagbag.import_errors:
                print(f"  ✗ Import errors: {dagbag.import_errors}")
                return False
            else:
                print("  ✓ No import errors")
                return True
        else:
            print("  ✗ DAG 'complete_crypto_pipeline_unified' not found")
            return False
            
    except Exception as e:
        print(f"✗ DAG parsing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_function_imports():
    """Test that all functions can be imported"""
    try:
        from airflow.dags.complete_crypto_pipeline_unified import (
            extract_reddit_data,
            clean_reddit_data,
            analyze_sentiment
        )
        
        print("\n✓ Function Imports:")
        print("  ✓ extract_reddit_data imported")
        print("  ✓ clean_reddit_data imported")
        print("  ✓ analyze_sentiment imported")
        return True
    except Exception as e:
        print(f"✗ Function import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DAG VALIDATION TESTS")
    print("=" * 60)
    
    results = []
    
    results.append(("DAG Import", test_dag_import()))
    results.append(("Function Imports", test_function_imports()))
    results.append(("DAG Structure", test_dag_structure()))
    results.append(("DAG Parsing", test_dag_parsing()))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ All tests passed! DAG is ready for Docker build.")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. Please fix errors before building Docker image.")
        sys.exit(1)

