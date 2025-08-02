from app.db.database import DatabaseManager


class SubscriptionService:
    """Service for handling subscription operations."""
    
    @staticmethod
    def create_subscription(email: str, repeat_frequency: str, scheduled_time: str, report_format: str, db_conn) -> str:
        """Create a new subscription if it doesn't already exist."""
        
        # Ensure the subscriptions table exists
        create_table_query = """
            CREATE TABLE IF NOT EXISTS subscriptions (
                id SERIAL PRIMARY KEY,
                email TEXT NOT NULL,
                repeat_frequency TEXT NOT NULL,
                scheduled_time TEXT NOT NULL,
                report_format TEXT NOT NULL
            )
        """
        DatabaseManager.create_table_if_not_exists(db_conn, create_table_query)
        
        # Check if a matching subscription already exists
        check_query = """
            SELECT 1 FROM subscriptions
            WHERE email = %s AND repeat_frequency = %s AND scheduled_time = %s AND report_format = %s
        """
        rows, _ = DatabaseManager.execute_query(
            db_conn, check_query, 
            (email, repeat_frequency, scheduled_time, report_format)
        )
        
        if rows:
            return "Subscription already exists."
        
        # Insert new subscription
        insert_query = """
            INSERT INTO subscriptions (email, repeat_frequency, scheduled_time, report_format)
            VALUES (%s, %s, %s, %s)
        """
        DatabaseManager.execute_insert(
            db_conn, insert_query,
            (email, repeat_frequency, scheduled_time, report_format)
        )
        
        return "Subscription created successfully."
