from typing import List, Dict, Any, Optional
from fastapi.encoders import jsonable_encoder
from app.db.database import DatabaseManager


class DataService:
    """Service for handling data operations and queries."""
    
    @staticmethod
    def get_sales_data(persona: Optional[str], db_conn) -> List[Dict[str, Any]]:
        """Get sales data with persona-based filtering."""
        persona_filter = ""
        if persona == "Srini":
            persona_filter = "WHERE s.city = 'New York'"
        elif persona == "Venkat":
            persona_filter = "WHERE s.city = 'San Francisco'"
        
        query = f"""
            SELECT
                d.date,
                p.product_name,
                p.category,
                s.store_name,
                s.city,
                c.customer_name,
                SUM(f.units_sold) AS units_sold,
                SUM(f.revenue) AS revenue,
                SUM(f.profit) AS profit
            FROM fact_sales f
            JOIN dim_date d ON f.date_id = d.date_id
            JOIN dim_product p ON f.product_id = p.product_id
            JOIN dim_customer c ON f.customer_id = c.customer_id
            JOIN dim_store s ON f.store_id = s.store_id
            {persona_filter}
            GROUP BY d.date, p.product_name, p.category, s.store_name, s.city, c.customer_name
            ORDER BY d.date DESC, p.product_name
            LIMIT 100
        """
        
        rows, columns = DatabaseManager.execute_query(db_conn, query)
        data = [dict(zip(columns, row)) for row in rows]
        return jsonable_encoder(data)
    
    @staticmethod
    def get_pp_data(persona: Optional[str], db_conn) -> List[Dict[str, Any]]:
        """Get PP data with persona-based filtering."""
        persona_filter = ""
        if persona == "Srini":
            persona_filter = "WHERE s.state = 'California'"
        elif persona == "Venkat":
            persona_filter = "WHERE s.state = 'Nevada'"
        
        query = f"""
            SELECT
                o.orderDate AS date,
                p.SKU AS product_id,
                p.Name AS product_name,
                p.Category AS category,
                s.id AS store_name,
                s.city,
                o.customerId AS customer_name,
                COUNT(oi.SKU) AS units_sold,
                SUM(p.Price) AS revenue,
                SUM(p.Price * 0.3) AS profit  -- Assuming 30% profit margin
            FROM orders o
            JOIN order_items oi ON o.id = oi.orderID
            JOIN products p ON oi.SKU = p.SKU
            JOIN stores s ON o.storeId = s.id
            JOIN customers c ON o.customerId = c.id  -- Optional if you want to enrich customer info
            {persona_filter} -- Optional filter placeholder
            GROUP BY o.orderDate, p.SKU, p.Name, p.Category, s.id, s.city, o.customerId
            ORDER BY o.orderDate DESC, p.Name
            LIMIT 100;
        """
        
        rows, columns = DatabaseManager.execute_query(db_conn, query)
        data = [dict(zip(columns, row)) for row in rows]
        return jsonable_encoder(data)
    
    @staticmethod
    def get_products(db_conn) -> List[Dict[str, Any]]:
        """Get all products."""
        query = "SELECT product_id, product_name, category, brand FROM dim_product ORDER BY product_name"
        rows, columns = DatabaseManager.execute_query(db_conn, query)
        data = [dict(zip(columns, row)) for row in rows]
        return jsonable_encoder(data)
    
    @staticmethod
    def get_stores(db_conn) -> List[Dict[str, Any]]:
        """Get all stores."""
        query = "SELECT store_id, store_name, city, state FROM dim_store ORDER BY store_name"
        rows, columns = DatabaseManager.execute_query(db_conn, query)
        data = [dict(zip(columns, row)) for row in rows]
        return jsonable_encoder(data)
    
    @staticmethod
    def get_pp_products(db_conn) -> List[Dict[str, Any]]:
        """Get PP products."""
        query = "SELECT SKU AS product_id, Name AS product_name, Category, Size as brand FROM products ORDER BY Name"
        rows, columns = DatabaseManager.execute_query(db_conn, query)
        data = [dict(zip(columns, row)) for row in rows]
        return jsonable_encoder(data)
    
    @staticmethod
    def get_pp_stores(db_conn) -> List[Dict[str, Any]]:
        """Get PP stores."""
        query = "SELECT id AS store_id, id AS store_name, city, state FROM stores ORDER BY id"
        rows, columns = DatabaseManager.execute_query(db_conn, query)
        data = [dict(zip(columns, row)) for row in rows]
        return jsonable_encoder(data)
