import json
import boto3
from goku.column import Col, DateTime
from copy import deepcopy
from pypika import MySQLQuery as Query, Table

client = boto3.client('rds-data', region_name='us-east-1')

class Model:

    created_at = DateTime(default_value='CURRENT_TIMESTAMP')
    updated_at = DateTime(default_value='CURRENT_TIMESTAMP', on_update='CURRENT_TIMESTAMP')

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

    def create_table(self):
        # Pypika's create table doesn't create valid MySQL for some reason so I'm doing a custom one
        column_defs = []
        for col in self.get_columns():
            column_defs.append(f'{self.instance_cols[col].get_def_statement(col)}')
        sql =  f'CREATE TABLE IF NOT EXISTS {self.get_table_name()} ({', '.join(column_defs)});'
        return self.__execute(sql)

    def create(self):
        self.__validate_columns()
        table = Table(self.get_table_name())
        q = Query.into(table)
        q = self.__build_insert_query(q)
        response = json.dumps(self.__execute(q.get_sql()))
        pk = self.instance_cols[self.primary_key].get_value()
        if pk is None:
            key = self.instance_cols[self.primary_key].get_aws_value_type()
            pk = response['generatedFields'][0][key]
        return self.get_by_pk(pk)
    
    def save(self, where=None, fields=None):
        if where is None:
            where = self.primary_key
        if fields is None:
            fields = self.get_columns()
        self.__validate_columns()
        table = Table(self.get_table_name())
        q = Query.update(table)
        q = self.__build_update_query(q, fields)
        q = self.__build_in_where_clause(q, where, [self.instance_cols[where].get_value()])
        response = self.__execute(q.get_sql())
        return self.get_by_pk()

    def as_json(self):
       return json.dumps(self.__dict__())

    def set_value(self, col, val):
        self.instance_cols[col].set_value(val)

    def get_by_pk(self, pks=None, fields=None):
        if pks is None:
            pks = self.instance_cols[self.primary_key].get_value()
        if pks is None:
            raise Exception('You need to pass value(s) or have one in the primary key of this object')
        return self.get_by_column(col=self.primary_key, vals=pks, fields=fields)
        
    def get_by_column(self, col=None, vals=None, fields=None):
        if fields is None:
            fields = self.get_columns()
        table = Table(self.get_table_name())
        q = Query.from_(table)
        q = self.__build_get_query(q, fields)
        q = self.__build_in_where_clause(q, col, vals)
        response = json.dumps(self.__execute(q.get_sql()))
        records = self.__parse_records(response['records'], fields)
        return records

    def get_by_pypika_query(self, q):
        response = json.dumps(self.__execute(q.get_sql()), with_meta=True)
        column_names = self.__parse_metadata(response['columnMetadata'])
        records = self.__parse_records(response['records'], column_names)
        return records

    def __parse_records(self, records=None, fields=None):
        parsed = []
        for record in records:
            parsed.append(self.__parse_record(record), fields)
        return parsed
        
    # Always return a new instance to avoid errors
    def __parse_record(self, record=None, fields=None):
        m = self.__class__()
        for i in range(0, len(record)):
            col = fields[i]
            if 'isNull' in record[i].keys():
                val = None
            else:
                val = record[i][self.instance_cols[col].get_aws_value_type()]
            m.set_value(col, val)
        return m
    
    def __parse_metadata(self, metadata):
        column_names = []
        for meta in metadata:
            if self.instance_cols[meta['name']] is not None:
                column_names.append(meta['name'])
        return column_names

    def __build_get_query(self, q, fields):
        cols = tuple(fields)
        return q.select(cols)

    def __validate_columns(self):
        for col in self.get_columns():
            self.instance_cols[col].validate(col)

    def __build_insert_query(self, q):
        cols = tuple(self.get_columns())
        vals = tuple(self.get_values())
        return q.columns(cols).insert(vals)
    
    def __build_update_query(self, q, fields):
        table = Table(self.get_table_name())
        for col in fields:
            if col != self.primary_key:
                q = q.set(table[col],self.instance_cols[col].get_value())
        return q

    def __build_in_where_clause(self, q, col, vals):
        table = Table(self.get_table_name())
        vals = tuple(vals)
        return q.where(table[col].isin(vals))
    
    def __get_table_name(self):
        if('table_name' not in dir(self)):
            raise Exception('You must provide a table_name')
        return getattr(self, 'table_name')

    def __get_database_name(self):
        if('database' not in dir(self)):
            raise Exception('You must provide a database')
        return getattr(self, 'database')

    def __get_secret_arn(self):
        if('secret_arn' not in dir(self)):
            raise Exception('You must provide a secret_arn')
        return getattr(self, 'secret_arn')

    def __get_resource_arn(self):
        if('resource_arn' not in dir(self)):
            raise Exception('You must provide a resource_arn')
        return getattr(self, 'resource_arn')

    def __filter_columns(self):
        return [key for key in dir(self) if key[0] != '_' and isinstance(getattr(self, key), Col)]
    
    def __execute(self, sql, with_meta=False):
        return client.execute_statement(
            continueAfterTimeout=True,
            database=self.database,
            resourceArn=self.resource_arn,
            secretArn=self.secret_arn,
            includeResultMetadata=with_meta,
            sql=sql
        )
        
        
