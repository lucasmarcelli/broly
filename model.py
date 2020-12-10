import json
import boto3
from copy import deepcopy
from column import Col
from pypika import MySQLQuery as Query, Table

class Model:

    client = boto3('rds-client')

    def __init__(self, *args, **kwargs):
        self.database = self.__get_database_name()
        self.secret_arn = self.__get_secret_arn()
        self.resource_arn = self.__get_resource_arn()
        self.table_name = self.__get_table_name()
        self.columns = self.__filter_columns()
        self.primary_key = [key for key in self.get_columns() if getattr(self,key).is_primary_key()][0]
        self.instance_cols = {}
        for col in self.columns:
            self.instance_cols[col] = deepcopy(getattr(self,col))
            value = getattr(self, col).get_default_value()
            if col in kwargs:
               value = kwargs[col]
            self.instance_cols[col].set_value(value)
            
    def __repr__(self):
        return self.as_json()
    
    def __dict__(self):
        _dict = {}
        for col in self.get_columns():
            _dict[col] = self.instance_cols[col].get_value()
        return _dict

    def create_table(self):
        pass
    
    def get_columns(self):
        return self.columns
    
    def get_values(self):
        return [self.instance_cols[col].get_value() for col in self.get_columns()]
    
    def get_table_name(self):
        return self.table_name

    def create(self):
        self.__validate_columns()
        table = Table(self.get_table_name())
        q = Query.into(table)
        q = self.__build_insert_query(q)
        return client.execute_statement(
            continueAfterTimeout=True,
            database=self.database,
            resourceArn=self.resource_arn,
            secretArn=self.secret_arn,
            sql=q.get_sql()
        )

    def save(self, where=None):
        if where is None:
            where = self.primary_key
        self.__validate_columns()
        table = Table(self.get_table_name())
        q = Query.update(table)
        q = self.__build_update_query(q)
        q = self.__build_where_clause(q, where, self.instance_cols[where].get_value())
        return client.execute_statement(
            continueAfterTimeout=True,
            database=self.database,
            resourceArn=self.resource_arn,
            secretArn=self.secret_arn,
            sql=q.get_sql()
        )

    def as_json(self):
       return json.dumps(self.__dict__())

    def set_value(self, col, val):
        self[col].set_value(val)

    def get_by_id(self, id=None):
        if id is None:
            id = self.instance_cols['id'].get_value()
        if id is None:
            raise Exception("You need to pass an id or have one in the object")
        table = Table(self.get_table_name())
        q = Query.from_(table)
        q = self.__build_get_query(q)
        q = self.__build_where_clause(q, 'id', id)

        # TODO: Parse the weird way the data API responds into 
        # an instance
        return client.execute_statement(
            continueAfterTimeout=True,
            database=self.database,
            resourceArn=self.resource_arn,
            secretArn=self.secret_arn,
            sql=q.get_sql()
        )

    def __build_get_query(self, q):
        cols = tuple(self.get_columns())
        return q.select(cols)

    def __validate_columns(self):
        for col in self.get_columns():
            self.instance_cols[col].validate(col)

    def __build_insert_query(self, q):
        cols = tuple(self.get_columns())
        vals = tuple(self.get_values())
        return q.columns(cols).insert(vals)
    
    def __build_update_query(self, q):
        for col in self.get_columns():
            if col != self.primary_key:
                q = q.set(table[col],self.instance_cols[col].get_value())
        return q

    def __build_where_clause(self, q, col, val):
        table = Table(self.get_table_name())
        return q.where(table[col]==val)
    
    def __get_table_name(self):
        if('table_name' not in dir(self)):
            raise Exception("You must provide a table_name")
        return getattr(self, 'table_name')

    def __get_database_name(self):
        if('database' not in dir(self)):
            raise Exception("You must provide a database")
        return getattr(self, 'database')

    def __get_secret_arn(self):
        if('secret_arn' not in dir(self)):
            raise Exception("You must provide a secret_arn")
        return getattr(self, 'secret_arn')

    def __get_resource_arn(self):
        if('resource_arn' not in dir(self)):
            raise Exception("You must provide a resource_arn")
        return getattr(self, 'resource_arn')

    def __filter_columns(self):
        return [key for key in dir(self) if key[0] != "_" and isinstance(getattr(self, key), Col)]

