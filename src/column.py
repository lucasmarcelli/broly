class Col:
    def __init__(self, col_type, default_value, nullable, primary_key):
        self.col_type = col_type
        self.default_value = default_value
        self.nullable = nullable
        self.primary_key = primary_key
        self.value = default_value

    def get_col_type(self):
        return self.col_type

    def get_default_value(self):
        return self.default_value

    def is_nullable(self):
        return self.nullable
    
    def is_primary_key(self):
        return self.primary_key

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value

    def validate(self, key):
        if self.get_value() is None and not self.is_nullable() and self.get_default_value() is None:
            raise Exception("Can't set non nullable value to none for " + str(key))
    
    def get_def_statement(self, name):
        val = f'{self.__get_initial_def(name)}'.strip()
        val = f'{val} {self.get_extras_for_def()}'.strip()
        return f'{val} {self.__get_pk_and_default_def()}'.strip()

    def get_extras_for_def(self):
        return ''

    def __repr__(self):
        return str(self.value)

    def __get_initial_def(self, name):
        return f'{name} {self.get_col_type()} {"NOT NULL" if self.is_nullable() else ""}'.strip()

    def __get_pk_and_default_def(self):
        pk = 'PRIMARY KEY' if self.is_primary_key() else ''
        d = '' if self.default_value is None else f'DEFAULT {self.get_default_value()}'
        return  f'{pk} {d}'.strip()


class IntColumn(Col):

    col_type = "INT"
    
    def __init__(self, default_value=None, nullable=True, primary_key=False, auto_increment=False):
        self.auto_increment = auto_increment
        super().__init__(IntColumn.col_type, default_value, nullable, primary_key)
    
    def get_aws_value_type(self):
        return "longValue"

    def get_extras_for_def(self):
        ai = 'AUTO_INCREMENT' if self.auto_increment else ''
        return f'{ai}'.strip()

class SmallInt(Col):
    col_type = "SMALLINT"

    def __init__(self, default_value=None, nullable=True, primary_key=False, auto_increment=False):
        self.auto_increment = auto_increment
        super().__init__(SmallInt.col_type, default_value, nullable, primary_key)
    
    def get_aws_value_type(self):
        return "longValue"
    
    def get_extras_for_def(self):
        ai = 'AUTO_INCREMENT' if self.auto_increment else ''
        return f'{ai}'.strip()


class VarChar(Col):

    col_type = "VARCHAR"

    def __init__(self, size=100, default_value=None, nullable=True, primary_key=False):
        self.size = size 
        super().__init__(VarChar.col_type, default_value, nullable, primary_key)

    def get_size(self):
        return self.size

    def get_col_type(self):
        return "VARCHAR("+str(self.size)+")"

    def get_aws_value_type(self):
        return "stringValue"