import pytest
from unittest.mock import Mock, patch
from app.services.data_service import DataService


class TestDataService:
    """Test data service functionality."""
    
    def test_get_sales_data_no_persona(self, mock_db_connection, sample_sales_data):
        """Test getting sales data without persona filtering."""
        with patch('app.services.data_service.DatabaseManager.execute_query') as mock_query:
            mock_query.return_value = (
                [('2023-01-01', 'Test Product', 'Electronics', 'Test Store', 'New York', 'John Doe', 10, 1000.0, 300.0)],
                ['date', 'product_name', 'category', 'store_name', 'city', 'customer_name', 'units_sold', 'revenue', 'profit']
            )
            
            result = DataService.get_sales_data(None, mock_db_connection)
            
            assert len(result) == 1
            assert result[0]['product_name'] == 'Test Product'
            assert result[0]['city'] == 'New York'
            # Verify no WHERE clause in query
            query_call = mock_query.call_args[0][1]
            assert "WHERE" not in query_call
    
    def test_get_sales_data_srini_persona(self, mock_db_connection):
        """Test getting sales data with Srini persona filtering."""
        with patch('app.services.data_service.DatabaseManager.execute_query') as mock_query:
            mock_query.return_value = ([], [])
            
            DataService.get_sales_data("Srini", mock_db_connection)
            
            # Verify query contains Srini's filter
            query_call = mock_query.call_args[0][1]
            assert "WHERE s.city = 'New York'" in query_call
    
    def test_get_sales_data_venkat_persona(self, mock_db_connection):
        """Test getting sales data with Venkat persona filtering."""
        with patch('app.services.data_service.DatabaseManager.execute_query') as mock_query:
            mock_query.return_value = ([], [])
            
            DataService.get_sales_data("Venkat", mock_db_connection)
            
            # Verify query contains Venkat's filter
            query_call = mock_query.call_args[0][1]
            assert "WHERE s.city = 'San Francisco'" in query_call
    
    def test_get_pp_data_no_persona(self, mock_db_connection):
        """Test getting PP data without persona filtering."""
        with patch('app.services.data_service.DatabaseManager.execute_query') as mock_query:
            mock_query.return_value = ([], [])
            
            DataService.get_pp_data(None, mock_db_connection)
            
            query_call = mock_query.call_args[0][1]
            assert "WHERE" not in query_call.replace("WHERE s.state", "X")  # Remove the comment WHERE
    
    def test_get_pp_data_srini_persona(self, mock_db_connection):
        """Test getting PP data with Srini persona filtering."""
        with patch('app.services.data_service.DatabaseManager.execute_query') as mock_query:
            mock_query.return_value = ([], [])
            
            DataService.get_pp_data("Srini", mock_db_connection)
            
            query_call = mock_query.call_args[0][1]
            assert "WHERE s.state = 'California'" in query_call
    
    def test_get_pp_data_venkat_persona(self, mock_db_connection):
        """Test getting PP data with Venkat persona filtering."""
        with patch('app.services.data_service.DatabaseManager.execute_query') as mock_query:
            mock_query.return_value = ([], [])
            
            DataService.get_pp_data("Venkat", mock_db_connection)
            
            query_call = mock_query.call_args[0][1]
            assert "WHERE s.state = 'Nevada'" in query_call
    
    def test_get_products(self, mock_db_connection):
        """Test getting products data."""
        with patch('app.services.data_service.DatabaseManager.execute_query') as mock_query:
            mock_query.return_value = (
                [(1, 'Test Product', 'Electronics', 'TestBrand')],
                ['product_id', 'product_name', 'category', 'brand']
            )
            
            result = DataService.get_products(mock_db_connection)
            
            assert len(result) == 1
            assert result[0]['product_name'] == 'Test Product'
            assert result[0]['category'] == 'Electronics'
            
            # Verify correct query
            query_call = mock_query.call_args[0][1]
            assert "SELECT product_id, product_name, category, brand FROM dim_product" in query_call
    
    def test_get_stores(self, mock_db_connection):
        """Test getting stores data."""
        with patch('app.services.data_service.DatabaseManager.execute_query') as mock_query:
            mock_query.return_value = (
                [(1, 'Test Store', 'New York', 'NY')],
                ['store_id', 'store_name', 'city', 'state']
            )
            
            result = DataService.get_stores(mock_db_connection)
            
            assert len(result) == 1
            assert result[0]['store_name'] == 'Test Store'
            assert result[0]['city'] == 'New York'
            
            # Verify correct query
            query_call = mock_query.call_args[0][1]
            assert "SELECT store_id, store_name, city, state FROM dim_store" in query_call
    
    def test_get_pp_products(self, mock_db_connection):
        """Test getting PP products data."""
        with patch('app.services.data_service.DatabaseManager.execute_query') as mock_query:
            mock_query.return_value = (
                [('SKU123', 'PP Product', 'Category', 'Large')],
                ['product_id', 'product_name', 'Category', 'brand']
            )
            
            result = DataService.get_pp_products(mock_db_connection)
            
            assert len(result) == 1
            assert result[0]['product_id'] == 'SKU123'
            assert result[0]['product_name'] == 'PP Product'
            
            # Verify correct query
            query_call = mock_query.call_args[0][1]
            assert "SELECT SKU AS product_id, Name AS product_name" in query_call
    
    def test_get_pp_stores(self, mock_db_connection):
        """Test getting PP stores data."""
        with patch('app.services.data_service.DatabaseManager.execute_query') as mock_query:
            mock_query.return_value = (
                [(1, 1, 'Test City', 'Test State')],
                ['store_id', 'store_name', 'city', 'state']
            )
            
            result = DataService.get_pp_stores(mock_db_connection)
            
            assert len(result) == 1
            assert result[0]['store_id'] == 1
            assert result[0]['city'] == 'Test City'
            
            # Verify correct query
            query_call = mock_query.call_args[0][1]
            assert "SELECT id AS store_id, id AS store_name" in query_call
    
    def test_data_serialization(self, mock_db_connection):
        """Test that data is properly serialized to JSON."""
        with patch('app.services.data_service.DatabaseManager.execute_query') as mock_query:
            # Test with datetime and decimal values
            from datetime import datetime
            from decimal import Decimal
            
            mock_query.return_value = (
                [(datetime(2023, 1, 1), Decimal('1000.50'))],
                ['date', 'amount']
            )
            
            result = DataService.get_products(mock_db_connection)
            
            # Should not raise serialization errors
            assert len(result) == 1
            # Data should be JSON serializable
            import json
            json.dumps(result)  # This should not raise an exception
