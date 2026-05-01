import pandas as pd
from sqlalchemy import create_engine

# 1. Define your connection parameters
# Format: postgresql://username:password@host:port/database_name
DB_USER = 'postgres'
DB_PASSWORD = 'u9expected'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'dbms-project'

# 2. Create the connection engine
connection_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(connection_string)

try:
    # 3. Pull data from the View we created earlier
    # Change from ML_Ready_Data to ml_ready_data
    query = "SELECT * FROM ml_ready_data"
    df = pd.read_sql(query, engine)
    
    print("Connection Successful!")
    print(df.head()) # Verify the data
    
except Exception as e:
    print(f"Error: {e}")
engine = create_engine(connection_string)
df = pd.read_sql("SELECT * FROM ml_ready_data", engine)