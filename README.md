# Broly

Small module for managing models with the AWS rds data-api from lambda. Should be set into a lambda layer.

Uses [pypika](https://github.com/kayak/pypika) to generate MySQL and boto3's rds-data client.


MVP Features:

- [x] Generic model class
- [x] Model manipulation
- [x] Insert
- [x] Update
- [x] Autoincrement option
- [x] Read by column and parse response
    - [x] Parsing datetimes
- [x] Table creation
- [x] Bulk get
- [x] Take pypika get queries to execute directly 
- [x] Main MySQL column classes
- [x] Wait for serverless wakeup, boto3 doesn't retry automatically if db is 'asleep'
- [x] Delete 
- [x] Order results for get queries
- [ ] Tests


## To add to lambda layer
```bash
mkdir python
pip3 install broly --target python/
zip -r python layer
```

Then just upload it to your lambda's layer.

## Usage
```python
from broly.model import Model
from broly.column import IntColumn, VarChar

class Example(Model):

    table_name = 'example'
    secret_arn = 'secret-arn'
    resource_arn = 'resource-arn'
    database = 'db-name'

    id = IntColumn(primary_key=True)
    name = VarChar(nullable=False)
    description = VarChar(size=1000)

e = Example(name="name")
e.set_value('description', 'desc')
print(e)
e = e.save()
print(e)
```