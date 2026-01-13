import sqlite3
import os

class SQLiteHelper:
    def __init__(self, db_path=None):
        # Default to a path likely used in your project if none provided
        self.db_path = db_path or os.getenv("DATABASE_PATH", "food_trucks.db")

    def execute_query(self, query, params=()):
        """Execute a query and return all results (SELECT)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Returns results as dictionaries
                cursor = conn.cursor()
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def verify_truck_exists(self, applicant_name):
        """Helper specifically for your food truck tests."""
        query = "SELECT * FROM food_trucks WHERE applicant = ?"
        results = self.execute_query(query, (applicant_name,))
        return len(results) > 0