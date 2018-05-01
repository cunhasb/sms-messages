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
    'postgresql://sms-admin:sms-admin-Password@localhost:5432/sms')

# inspect - Get Database information

inspector = inspect(engine)
print('Tables', inspector.get_table_names())
# pdb.set_trace()
print ('User - Columns', inspector.get_columns('user'))
print ('User - Customers - Columns', inspector.get_columns('user_customer'))
print ('message - Columns', inspector.get_columns('message'))
# other tables ...

''' Reflection - Loading Table from Existing database_setup
Creating MetaData instance'''

metadata = MetaData()
# reflect db schema to MetaData
metadata.reflect(bind=engine)
print ('SMS - metadata tables', metadata.tables)

# bind in order to Drop
metadata._bind_to(engine)
metadata.drop_all()
engine.dispose()
