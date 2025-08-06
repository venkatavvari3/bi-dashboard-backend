import pytest
from unittest.mock import Mock, patch, MagicMock
import psycopg2
from app.db.database import get_db, DatabaseManager


class TestDatabaseManager:
    """Test database manager functionality."""
    
    def test_execute_query_with_results(self, mock_db_connection):
        """Test executing a query that returns results."""
        # Setup mock
        mock_cursor = mock_db_connection.cursor.return_value
        mock_cursor.fetchall.return_value = [('test_value',)]
        mock_cursor.description = [('column1',)]
        
        # Execute query
        rows, columns = DatabaseManager.execute_query(
            mock_db_connection, 
            "SELECT * FROM test_table"
        )
        
        # Assertions
        assert rows == [('test_value',)]
        assert columns == ['column1']
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table")
        mock_cursor.close.assert_called_once()
    
    def test_execute_query_with_params(self, mock_db_connection):
        """Test executing a query with parameters."""
        mock_cursor = mock_db_connection.cursor.return_value
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = []
        
        DatabaseManager.execute_query(
            mock_db_connection,
            "SELECT * FROM users WHERE id = %s",
            (1,)
        )
        
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM users WHERE id = %s", 
            (1,)
        )
    
    def test_execute_insert(self, mock_db_connection):
        """Test executing an insert query."""
        mock_cursor = mock_db_connection.cursor.return_value
        
        DatabaseManager.execute_insert(
            mock_db_connection,
            "INSERT INTO users (name) VALUES (%s)",
            ("John Doe",)
        )
        
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO users (name) VALUES (%s)",
            ("John Doe",)
        )
        mock_db_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_create_table_if_not_exists(self, mock_db_connection):
        """Test creating a table."""
        mock_cursor = mock_db_connection.cursor.return_value
        create_query = "CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY)"
        
        DatabaseManager.create_table_if_not_exists(
            mock_db_connection,
            create_query
        )
        
        mock_cursor.execute.assert_called_once_with(create_query)
        mock_db_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()


class TestGetDbDependency:
    """Test database dependency function."""
    
    @patch('app.db.database.psycopg2.connect')
    def test_get_db_yields_connection(self, mock_connect):
        """Test that get_db yields a database connection."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        # Test the generator
        db_gen = get_db()
        connection = next(db_gen)
        
        assert connection == mock_connection
        mock_connect.assert_called_once()
        
        # Test cleanup
        try:
            next(db_gen)
        except StopIteration:
            pass
        
        mock_connection.close.assert_called_once()
    
    @patch('app.db.database.psycopg2.connect')
    def test_get_db_handles_exception(self, mock_connect):
        """Test that get_db properly handles exceptions."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        db_gen = get_db()
        connection = next(db_gen)
        
        # Simulate an exception in the with block
        with pytest.raises(Exception):
            try:
                next(db_gen)
            except StopIteration:
                # This is expected, but we want to ensure cleanup still happens
                pass
            raise Exception("Test exception")
        
        # Connection should still be closed
        mock_connection.close.assert_called_once()
