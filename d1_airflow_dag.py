import subprocess
import time
from datetime import datetime

class AirflowDAGSimulator:
    def __init__(self, dag_name):
        self.dag_name = dag_name
        self.tasks = []
        self.start_time = None
        self.end_time = None

    def add_task(self, task_id, description, command):
        self.tasks.append({
            'id': task_id,
            'description': description,
            'command': command
        })

    def run(self):
        print("\n" + "="*80)
        print(f"AIRFLOW DAG SIMULATION: {self.dag_name}")
        print("="*80)
        self.start_time = datetime.now()
        print(f"Simulation start time: {self.start_time}\n")

        results = []
        for idx, task in enumerate(self.tasks, 1):
            print("-"*80)
            print(f"[{idx}/{len(self.tasks)}] Running: {task['id']}")
            print(f"Description: {task['description']}")
            print("-"*80)
            
            task_start = time.time()
            try:
                result = subprocess.run(task['command'], shell=True, capture_output=True, text=True, timeout=30)
                task_duration = time.time() - task_start
                
                if result.stdout:
                    print(result.stdout)
                
                if result.returncode == 0:
                    print(f"\n✓ SUCCESS ({task_duration:.2f} seconds)\n")
                    results.append({'task': task['id'], 'status': 'PASSED', 'duration': task_duration})
                else:
                    print(f"\n✗ FAILED ({task_duration:.2f} seconds)")
                    if result.stderr:
                        print(f"Error: {result.stderr}\n")
                    results.append({'task': task['id'], 'status': 'FAILED', 'duration': task_duration})
            except subprocess.TimeoutExpired:
                print(f"\n✗ TIMEOUT (>30 seconds)\n")
                results.append({'task': task['id'], 'status': 'TIMEOUT', 'duration': 30})
            except Exception as e:
                print(f"\n✗ ERROR: {str(e)}\n")
                results.append({'task': task['id'], 'status': 'ERROR', 'duration': 0})

        self.end_time = datetime.now()
        self.print_summary(results)

    def print_summary(self, results):
        print("\n" + "="*80)
        print("DAG EXECUTION SUMMARY")
        print("="*80 + "\n")
        
        print("Task Results:")
        for idx, result in enumerate(results, 1):
            status_icon = "✓" if result['status'] == 'PASSED' else "✗"
            print(f"  [{idx}/{len(results)}] {status_icon} {result['status']:6s}  {result['task']:30s} ({result['duration']:.2f}s)")
        
        passed = sum(1 for r in results if r['status'] == 'PASSED')
        failed = sum(1 for r in results if r['status'] != 'PASSED')
        total_duration = sum(r['duration'] for r in results)
        
        print("\n" + "-"*80)
        print(f"Total Tasks: {len(results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total Duration: {total_duration:.2f} seconds")
        print("-"*80 + "\n")
        
        if failed == 0:
            print("✓✓✓ DAG EXECUTION: SUCCESS ✓✓✓\n")
        else:
            print(f"✗✗✗ DAG EXECUTION: FAILED ✗✗✗\n")
            print(f"{failed} task(s) failed. Check output above for details.\n")

if __name__ == "__main__":
    dag = AirflowDAGSimulator("quickcart_daily_pipeline")
    
    dag.add_task(
        "ingest_raw_data",
        "Load CSV files into SQLite",
        "cd /Users/mpe/Desktop/'Mini Project' && python3 c1_data_ingestion.py > /dev/null 2>&1"
    )
    
    dag.add_task(
        "clean_data",
        "Clean and standardize data",
        "cd /Users/mpe/Desktop/'Mini Project' && python3 c2_data_cleaning.py > /dev/null 2>&1"
    )
    
    dag.add_task(
        "run_dbt_transformations",
        "Run dbt models (staging → intermediate → mart)",
        "cd /Users/mpe/Desktop/'Mini Project' && dbt run > /dev/null 2>&1"
    )
    
    dag.add_task(
        "validate_data_quality",
        "Validate transformed data quality",
        "cd /Users/mpe/Desktop/'Mini Project' && python3 test_dbt_models.py > /dev/null 2>&1"
    )
    
    dag.add_task(
        "export_results",
        "Export results to Parquet",
        "cd /Users/mpe/Desktop/'Mini Project' && python3 c5_export_optimization.py > /dev/null 2>&1"
    )
    
    dag.run()
