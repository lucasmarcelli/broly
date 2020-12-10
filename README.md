# Goku

Small module for managing models with the AWS rds data-api from lambda. Should be set into a lambda layer.

Uses [pypika](https://github.com/kayak/pypika) to generate MySQL and `boto3('rds-client')`


MVP Features:

- [x] Generic model class
- [x] Model manipulation
- [x] Insert
- [x] Update
- [ ] Autoincrement option
- [ ] Read by id and parse response
- [ ] Main MySQL column classes
- [ ] Table creation
- [ ] Tests


## Usage
```python
from model import Model
from column import IntColumn, VarChar

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
e.save()
