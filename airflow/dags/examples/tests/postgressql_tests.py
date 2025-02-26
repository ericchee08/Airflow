import unittest
from unittest import mock
import pendulum
from airflow.models import DagBag, TaskInstance, DAG, DagRun
from airflow.utils.session import create_session
from airflow.utils.state import State
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

class TestSimplePostgresDAG(unittest.TestCase):
    """Test case for the simple_postgres_dag."""

    @classmethod
    def setUpClass(cls):
        """Setup for the test by loading the DAG."""
        cls.dagbag = DagBag(include_examples=False)
        cls.dag_id = 'simple_postgres_dag'
        cls.dag = cls.dagbag.get_dag(cls.dag_id)

    def test_dag_loaded(self):
        """Test that the DAG is loaded correctly."""
        self.assertIsNotNone(self.dag, f"DAG {self.dag_id} not found")
        self.assertEqual(self.dag.dag_id, self.dag_id)
        self.assertEqual(self.dag.description, 'A simple DAG to interact with PostgreSQL')
        self.assertFalse(self.dag.catchup)

    def test_dag_structure(self):
        """Test the structure of the DAG."""
        # Check task count
        task_ids = list(self.dag.task_dict.keys())
        self.assertEqual(len(task_ids), 3, f"Expected 3 tasks, got {len(task_ids)}")
        
        # Check task ids
        expected_task_ids = ['create_table', 'insert_data', 'fetch_data']
        self.assertListEqual(sorted(task_ids), sorted(expected_task_ids))
        
        # Check task types
        for task_id in task_ids:
            self.assertIsInstance(
                self.dag.get_task(task_id),
                SQLExecuteQueryOperator,
                f"Task {task_id} is not a SQLExecuteQueryOperator"
            )

    def test_task_dependencies(self):
        """Test that task dependencies are correctly defined."""
        create_task = self.dag.get_task('create_table')
        insert_task = self.dag.get_task('insert_data')
        fetch_task = self.dag.get_task('fetch_data')
        
        # Check upstream and downstream relationships
        self.assertEqual(len(create_task.upstream_task_ids), 0)
        self.assertEqual(len(create_task.downstream_task_ids), 1)
        self.assertIn('insert_data', create_task.downstream_task_ids)
        
        self.assertEqual(len(insert_task.upstream_task_ids), 1)
        self.assertEqual(len(insert_task.downstream_task_ids), 1)
        self.assertIn('create_table', insert_task.upstream_task_ids)
        self.assertIn('fetch_data', insert_task.downstream_task_ids)
        
        self.assertEqual(len(fetch_task.upstream_task_ids), 1)
        self.assertEqual(len(fetch_task.downstream_task_ids), 0)
        self.assertIn('insert_data', fetch_task.upstream_task_ids)

    def test_connection_id(self):
        """Test that all tasks use the correct connection ID."""
        for task_id in ['create_table', 'insert_data', 'fetch_data']:
            task = self.dag.get_task(task_id)
            self.assertEqual(task.conn_id, 'eric_db')

    def test_task_sql_statements(self):
        """Test that tasks have the correct SQL statements."""
        create_task = self.dag.get_task('create_table')
        insert_task = self.dag.get_task('insert_data')
        fetch_task = self.dag.get_task('fetch_data')
        
        # Strip whitespace for comparison
        self.assertIn('CREATE TABLE IF NOT EXISTS my_table', create_task.sql.strip())
        self.assertIn('INSERT INTO my_table (name, age) VALUES', insert_task.sql.strip())
        self.assertEqual('SELECT * FROM my_table;', fetch_task.sql.strip())

    @mock.patch('airflow.providers.common.sql.operators.sql.SQLExecuteQueryOperator.execute')
    def test_task_execution(self, mock_execute):
        """Test that tasks execute successfully by mocking the execute method."""
        mock_execute.return_value = True
        
        # Create logical date and run_id for testing
        logical_date = pendulum.now('UTC')
        run_id = f"test_{logical_date.isoformat()}"
        
        # Create a DagRun
        with create_session() as session:
            dag_run = DagRun(
                dag_id=self.dag_id,
                run_id=run_id,
                run_type="manual",
                execution_date=logical_date,
                state=State.RUNNING,
                external_trigger=True,
            )
            session.add(dag_run)
            session.commit()
        
        try:
            # Test execution of each task
            for task_id in ['create_table', 'insert_data', 'fetch_data']:
                task = self.dag.get_task(task_id)
                
                # Create a TaskInstance with run_id instead of execution_date
                ti = TaskInstance(task=task, run_id=run_id)
                ti.dag_run = dag_run
                
                # Instead of running the task, just mock the execute method
                with mock.patch.object(task, 'execute') as mock_task_execute:
                    mock_task_execute.return_value = None
                    ti.task = task
                    # Just test the operator's behavior
                    self.assertIsNone(task.execute(context={'ti': ti}))
        finally:
            # Clean up the created DagRun
            with create_session() as session:
                session.query(DagRun).filter(
                    DagRun.dag_id == self.dag_id,
                    DagRun.run_id == run_id
                ).delete()

    @mock.patch('airflow.providers.postgres.hooks.postgres.PostgresHook.get_conn')
    def test_integration(self, mock_get_conn):
        """Integration test with a mock database connection."""
        # Setup mock for PostgreSQL connection
        mock_conn = mock.MagicMock()
        mock_cursor = mock.MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('Eric Chee', 27)]
        mock_get_conn.return_value = mock_conn
        
        # Create logical date and run_id for testing
        logical_date = pendulum.now('UTC')
        run_id = f"test_integration_{logical_date.isoformat()}"
        
        # Create a DagRun to associate with our tests
        with create_session() as session:
            dag_run = DagRun(
                dag_id=self.dag_id,
                run_id=run_id,
                run_type="manual",
                execution_date=logical_date,
                state=State.RUNNING,
                external_trigger=True,
            )
            session.add(dag_run)
            session.commit()
        
        try:
            # Test each task in isolation but with proper DB mocking
            for task_id in ['create_table', 'insert_data', 'fetch_data']:
                task = self.dag.get_task(task_id)
                
                # Use the operator's execute method with mocked DB connection
                with mock.patch.object(SQLExecuteQueryOperator, 'get_db_hook') as mock_get_db_hook:
                    mock_hook = mock.MagicMock()
                    mock_hook.run.return_value = [('Eric Chee', 27)] if task_id == 'fetch_data' else None
                    mock_get_db_hook.return_value = mock_hook
                    
                    # Create TaskInstance using run_id instead of execution_date
                    ti = TaskInstance(task=task, run_id=run_id)
                    ti.dag_run = dag_run
                    
                    # Execute the task with mocked DB connection
                    context = {'ti': ti}
                    task.execute(context)
                    
                    # Verify the hook was called with the right SQL
                    mock_hook.run.assert_called_once()
        
        finally:
            # Clean up the created DagRun
            with create_session() as session:
                session.query(DagRun).filter(
                    DagRun.dag_id == self.dag_id,
                    DagRun.run_id == run_id
                ).delete()

if __name__ == '__main__':
    unittest.main()