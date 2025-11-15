import snowflake.connector
import os
from typing import Optional

def create_snowflake_connection(
    warehouse: Optional[str] = None,
    database: Optional[str] = None,
    schema: Optional[str] = None
):
    """
    Create a connection to Snowflake using account credentials.

    Args:
        warehouse: Optional warehouse name to use
        database: Optional database name to use
        schema: Optional schema name to use

    Returns:
        snowflake.connector.connection.SnowflakeConnection
    """
    # Get password from environment variable for security
    password = os.getenv('SNOWFLAKE_PASSWORD')

    if not password:
        raise ValueError(
            "SNOWFLAKE_PASSWORD environment variable not set. "
            "Please set it with: export SNOWFLAKE_PASSWORD='your_password'"
        )

    connection_params = {
        'user': 'EDUPAZOGLE',
        'password': password,
        'account': 'XOJYPFW-MW99895',
        'role': 'ACCOUNTADMIN',
    }

    # Add optional parameters if provided
    if warehouse:
        connection_params['warehouse'] = warehouse
    if database:
        connection_params['database'] = database
    if schema:
        connection_params['schema'] = schema

    try:
        conn = snowflake.connector.connect(**connection_params)
        print("Successfully connected to Snowflake!")
        print(f"Account: XOJYPFW-MW99895")
        print(f"User: EDUPAZOGLE")
        print(f"Role: ACCOUNTADMIN")
        return conn
    except Exception as e:
        print(f"Error connecting to Snowflake: {e}")
        raise


def test_connection():
    """Test the Snowflake connection with a simple query."""
    conn = create_snowflake_connection()

    try:
        cursor = conn.cursor()

        # Test query to show current context
        cursor.execute("SELECT CURRENT_VERSION(), CURRENT_USER(), CURRENT_ROLE()")
        result = cursor.fetchone()

        print("\nConnection Test Results:")
        print(f"Snowflake Version: {result[0]}")
        print(f"Current User: {result[1]}")
        print(f"Current Role: {result[2]}")

        cursor.close()
    finally:
        conn.close()
        print("\nConnection closed.")


if __name__ == "__main__":
    test_connection()
