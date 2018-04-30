import os
import sys
from sqlalchemy import create_engine, inspect, MetaData
import pdb

''' To drop database in PostgreSQL
irreversible, database cannot be in use by anyone.
psql
\list
DROP DATABASE IF EXISTS name;
'''

# Create engine and establish connection

engine = create_engine(
    'postgresql://sms:sms-admin-Password@localhost:5432/sms-admin')

# inspect - Get Database information

inspector = inspect(engine)
print('Tables', inspector.get_table_names())
print ('SMS - Columns', inspector.get_columns('sms'))
# other tables ...

''' Reflection - Loading Table from Existing database_setup
Creating MetaData instance'''

metadata = MetaData()
# reflect db schema to MetaData
metadata.reflect(bind=engine)
print (metadata.tables)

# bind in order to Drop
metadata._bind_to(engine)
metadata.drop_all()
engine.dispose()
