import pytest
from unittest.mock import Mock, patch
from app.services.subscription_service import SubscriptionService


class TestSubscriptionService:
    """Test subscription service functionality."""
    
    def test_create_subscription_new(self, mock_db_connection):
        """Test creating a new subscription."""
        with patch('app.services.subscription_service.DatabaseManager') as mock_db_manager:
            # Mock table creation
            mock_db_manager.create_table_if_not_exists.return_value = None
            # Mock check query returns no existing subscription
            mock_db_manager.execute_query.return_value = ([], [])
            # Mock insert
            mock_db_manager.execute_insert.return_value = None
            
            result = SubscriptionService.create_subscription(
                "user@example.com",
                "daily",
                "09:00",
                "PDF",
                mock_db_connection
            )
            
            assert result == "Subscription created successfully."
            
            # Verify table creation was called
            mock_db_manager.create_table_if_not_exists.assert_called_once()
            
            # Verify check query was called
            mock_db_manager.execute_query.assert_called_once()
            
            # Verify insert was called
            mock_db_manager.execute_insert.assert_called_once()
    
    def test_create_subscription_existing(self, mock_db_connection):
        """Test creating a subscription that already exists."""
        with patch('app.services.subscription_service.DatabaseManager') as mock_db_manager:
            # Mock table creation
            mock_db_manager.create_table_if_not_exists.return_value = None
            # Mock check query returns existing subscription
            mock_db_manager.execute_query.return_value = ([(1,)], ['id'])
            
            result = SubscriptionService.create_subscription(
                "user@example.com",
                "daily",
                "09:00",
                "PDF",
                mock_db_connection
            )
            
            assert result == "Subscription already exists."
            
            # Verify table creation was called
            mock_db_manager.create_table_if_not_exists.assert_called_once()
            
            # Verify check query was called
            mock_db_manager.execute_query.assert_called_once()
            
            # Verify insert was NOT called
            mock_db_manager.execute_insert.assert_not_called()
    
    def test_subscription_table_creation(self, mock_db_connection):
        """Test that subscription table is created with correct schema."""
        with patch('app.services.subscription_service.DatabaseManager') as mock_db_manager:
            mock_db_manager.create_table_if_not_exists.return_value = None
            mock_db_manager.execute_query.return_value = ([], [])
            mock_db_manager.execute_insert.return_value = None
            
            SubscriptionService.create_subscription(
                "user@example.com",
                "weekly",
                "10:30",
                "Excel",
                mock_db_connection
            )
            
            # Check that table creation was called with correct SQL
            create_call = mock_db_manager.create_table_if_not_exists.call_args
            create_query = create_call[0][1]
            
            assert "CREATE TABLE IF NOT EXISTS subscriptions" in create_query
            assert "id SERIAL PRIMARY KEY" in create_query
            assert "email TEXT NOT NULL" in create_query
            assert "repeat_frequency TEXT NOT NULL" in create_query
            assert "scheduled_time TEXT NOT NULL" in create_query
            assert "report_format TEXT NOT NULL" in create_query
    
    def test_subscription_duplicate_check(self, mock_db_connection):
        """Test that duplicate subscription check uses correct parameters."""
        with patch('app.services.subscription_service.DatabaseManager') as mock_db_manager:
            mock_db_manager.create_table_if_not_exists.return_value = None
            mock_db_manager.execute_query.return_value = ([], [])
            mock_db_manager.execute_insert.return_value = None
            
            email = "test@example.com"
            frequency = "monthly"
            time = "14:00"
            format_type = "CSV"
            
            SubscriptionService.create_subscription(
                email, frequency, time, format_type, mock_db_connection
            )
            
            # Check that query was called with correct parameters
            query_call = mock_db_manager.execute_query.call_args
            query_sql, query_params = query_call[0][1], query_call[0][2]
            
            assert "SELECT 1 FROM subscriptions" in query_sql
            assert "WHERE email = %s AND repeat_frequency = %s" in query_sql
            assert query_params == (email, frequency, time, format_type)
    
    def test_subscription_insert_parameters(self, mock_db_connection):
        """Test that subscription insert uses correct parameters."""
        with patch('app.services.subscription_service.DatabaseManager') as mock_db_manager:
            mock_db_manager.create_table_if_not_exists.return_value = None
            mock_db_manager.execute_query.return_value = ([], [])
            mock_db_manager.execute_insert.return_value = None
            
            email = "insert@example.com"
            frequency = "yearly"
            time = "08:15"
            format_type = "JSON"
            
            SubscriptionService.create_subscription(
                email, frequency, time, format_type, mock_db_connection
            )
            
            # Check that insert was called with correct parameters
            insert_call = mock_db_manager.execute_insert.call_args
            insert_sql, insert_params = insert_call[0][1], insert_call[0][2]
            
            assert "INSERT INTO subscriptions" in insert_sql
            assert "(email, repeat_frequency, scheduled_time, report_format)" in insert_sql
            assert "VALUES (%s, %s, %s, %s)" in insert_sql
            assert insert_params == (email, frequency, time, format_type)
    
    def test_subscription_frequency_options(self, mock_db_connection):
        """Test subscription creation with different frequency options."""
        frequencies = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        
        with patch('app.services.subscription_service.DatabaseManager') as mock_db_manager:
            mock_db_manager.create_table_if_not_exists.return_value = None
            mock_db_manager.execute_query.return_value = ([], [])
            mock_db_manager.execute_insert.return_value = None
            
            for frequency in frequencies:
                result = SubscriptionService.create_subscription(
                    "user@example.com",
                    frequency,
                    "12:00",
                    "PDF",
                    mock_db_connection
                )
                
                assert result == "Subscription created successfully."
    
    def test_subscription_format_options(self, mock_db_connection):
        """Test subscription creation with different format options."""
        formats = ["PDF", "Excel", "CSV", "JSON"]
        
        with patch('app.services.subscription_service.DatabaseManager') as mock_db_manager:
            mock_db_manager.create_table_if_not_exists.return_value = None
            mock_db_manager.execute_query.return_value = ([], [])
            mock_db_manager.execute_insert.return_value = None
            
            for format_type in formats:
                result = SubscriptionService.create_subscription(
                    "user@example.com",
                    "daily",
                    "12:00",
                    format_type,
                    mock_db_connection
                )
                
                assert result == "Subscription created successfully."
