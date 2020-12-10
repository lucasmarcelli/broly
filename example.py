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
