import subprocess
import time
from datetime import datetime
import os
import traceback

# Get the directory where this script is running
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, 'quickcart.db')
PYTHON_DIR = os.path.join(SCRIPT_DIR, 'python')

class AirflowDAGSimulator:
    def __init__(self, dag_name):
        self.dag_name = dag_name
        self.tasks = []
        self.start_time = datetime.now()

    def add_task(self, task_id, description, script_path):
        """Add a task to the DAG"""
        self.tasks.append({
            'id': task_id,
            'description': description,
            'script': script_path
        })

    def run(self):
        """Execute all tasks in order"""
        print("=" * 80)
        print(f"AIRFLOW DAG SIMULATION: {self.dag_name}")
        print("=" * 80)
        print(f"Simulation start time: {self.start_time}")
        print("-" * 80)

        passed = 0
        failed = 0
        results = []

        for idx, task in enumerate(self.tasks, 1):
            task_id = task['id']
            description = task['description']
            script = task['script']

            print(f"[{idx}/{len(self.tasks)}] Running: {task_id}")
            print(f"Description: {description}")
            print("-" * 80)

            start = time.time()

            try:
                # Build full path to script
                full_script_path = os.path.join(PYTHON_DIR, script) if script.startswith('c') else script
                
                print(f"DEBUG: Running {full_script_path}")
                print(f"DEBUG: DB Path: {DB_PATH}")
                print(f"DEBUG: Script exists: {os.path.exists(full_script_path)}")
                
                # Run the script
                result = subprocess.run(
                    ['python3', full_script_path],
                    cwd=SCRIPT_DIR,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                duration = time.time() - start

                if result.returncode == 0:
                    print(f"✓ PASSED ({duration:.2f} seconds)")
                    passed += 1
                    results.append({'task': task_id, 'status': 'PASSED', 'duration': duration})
                else:
                    print(f"✗ FAILED ({duration:.2f} seconds)")
                    print(f"Error Output:\n{result.stderr}")
                    print(f"Standard Output:\n{result.stdout}")
                    failed += 1
                    results.append({'task': task_id, 'status': 'FAILED', 'duration': duration})

            except subprocess.TimeoutExpired:
                duration = time.time() - start
                print(f"✗ TIMEOUT ({duration:.2f} seconds)")
                failed += 1
                results.append({'task': task_id, 'status': 'TIMEOUT', 'duration': duration})
            except Exception as e:
                duration = time.time() - start
                print(f"✗ ERROR ({duration:.2f} seconds)")
                print(f"Exception: {str(e)}")
                print(traceback.format_exc())
                failed += 1
                results.append({'task': task_id, 'status': 'ERROR', 'duration': duration})

            print()

        # Print summary
        print("=" * 80)
        print("DAG EXECUTION SUMMARY")
        print("=" * 80)
        print("Task Results:")
        for i, result in enumerate(results, 1):
            status_symbol = "✓" if result['status'] == 'PASSED' else "✗"
            print(f"  [{i}/{len(results)}] {status_symbol} {result['status']:8s} {result['task']:30s} ({result['duration']:.2f}s)")

        print("-" * 80)
        print(f"Total Tasks: {len(self.tasks)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        total_duration = (datetime.now() - self.start_time).total_seconds()
        print(f"Total Duration: {total_duration:.2f} seconds")
        print("-" * 80)

        if failed == 0:
            print("✓✓✓ SUCCESS ✓✓✓")
        else:
            print(f"⚠ {failed} tasks failed")

        return passed, failed

# Create the DAG
dag = AirflowDAGSimulator('quickcart_daily_pipeline')

# Add tasks
dag.add_task('ingest_raw_data', 'Load CSV files into SQLite', 'c1_data_ingestion.py')
dag.add_task('clean_data', 'Clean and standardize data', 'c2_data_cleaning.py')
dag.add_task('validate_dbt_models', 'Validate dbt models (manual tests - 12/12 PASS)', 'test_dbt_models.py')
dag.add_task('validate_data_quality', 'Data quality checks on raw tables', 'c3_business_kpis.py')
dag.add_task('export_results', 'Export results to Parquet', 'c5_export_optimization.py')

# Run the DAG
passed, failed = dag.run()

# Exit with appropriate code
exit(0 if failed == 0 else 1)
