from datetime import datetime
class Col:
    def __init__(self, col_type, default_value=None, nullable=True, primary_key=False, unique=None, on_update=None):
        self.col_type = col_type
        self.default_value = default_value
        self.nullable = False if primary_key else nullable
        self.primary_key = primary_key
        self.value = self.set_value(default_value)
        self.unique = unique if unique is not None else self.primary_key
        self.on_update = on_update

    def get_col_type(self):
        return self.col_type

    def get_default_value(self):
        return self.default_value

    def is_nullable(self):
        return self.nullable

    def is_unique(self):
        return self.unique
    
    def is_primary_key(self):
        return self.primary_key

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value

    def validate(self, key):
        if self.get_value() is None and not self.is_nullable() and self.get_default_value() is None:
            raise Exception(f'Can\'t set non nullable value to none for {str(key)}')
    
    def get_def_statement(self, name):
        val = f'{self.__get_initial_def(name)}'.strip()
        val = f'{val} {self.get_extras_for_def()}'.strip()
        return f'{val} {self.__get_contraints()}'.strip()

    def get_extras_for_def(self):
        return ''

    def __repr__(self):
        return str(self.value)

    def __get_initial_def(self, name):
        val = f'{name} {self.get_col_type()} {"" if self.is_nullable() else "NOT NULL"}'.strip()
        d = '' if self.default_value is None else f'DEFAULT {self.get_default_value()}'
        return f'{val} {d}'.strip()

    def __get_contraints(self):
        pk = 'PRIMARY KEY' if self.is_primary_key() else ''
        unique = 'UNIQUE' if self.is_unique() else ''
        on_update = f'ON UPDATE {self.on_update}' if self.on_update is not None else ''
        val = f'{pk} {unique}'.strip()
        return f'{val} {on_update}'.strip()

class NumericColumnType(Col):
    def __init__(self, col_type=None, auto_increment=False, default_value=None, nullable=True, primary_key=False, unique=None, unsigned=False, on_update=None):
        self.auto_increment = auto_increment
        self.unsigned = unsigned
        super().__init__(col_type=col_type, default_value=default_value, nullable=nullable, primary_key=primary_key, unique=unique, on_update=on_update)
    
    def get_extras_for_def(self):
        ai = 'AUTO_INCREMENT' if self.auto_increment else ''
        unsigned = 'UNSIGNED' if self.unsigned else ''
        return f'{ai} {unsigned}'.strip()

class Decimal(NumericColumnType):

    col_type = 'DECIMAL'

    def __init__(self, precision=10, digits=0, default_value=None, nullable=True, primary_key=False, unique=None, on_update=None):
        self.precision = precision
        self.digits = digits
        super().__init__(col_type=Decimal.col_type, nullable=nullable, primary_key=primary_key, unique=unique, default_value=default_value, on_update=on_update)
    
    def get_aws_value_type(self):
        return 'doubleValue'

    def get_col_type(self):
        return f'DECIMAL({self.precision},{self.digits})'.strip()

class IntColumn(NumericColumnType):

    col_type = 'INT'
    
    def __init__(self, default_value=None, nullable=True, primary_key=False, auto_increment=False, unique=None, on_update=None):
        super().__init__(col_type=IntColumn.col_type, auto_increment=auto_increment, default_value=default_value, nullable=nullable, primary_key=primary_key, unique=unique, on_update=on_update)
    
    def get_aws_value_type(self):
        return 'longValue'


class SmallInt(NumericColumnType):
    col_type = 'SMALLINT'

    def __init__(self, default_value=None, nullable=True, primary_key=False, auto_increment=False, unique=None, on_update=None):
        super().__init__(col_type=SmallInt.col_type, auto_increment=auto_increment, default_value=default_value, nullable=nullable, primary_key=primary_key, unique=unique, on_update=on_update)
    
    def get_aws_value_type(self):
        return 'longValue'

class Bool(Col):

    col_type = 'BOOLEAN'

    def __init__(self, default_value=None, nullable=True, on_update=None):
        super().__init__(col_type=Bool.col_type, default_value=default_value, nullable=nullable, on_update=on_update)

    def get_aws_value_type(self):
        return 'booleanValue'

    def set_value(self, val):
        if val is None:
            super().set_value(None)
        else:
            super().set_value(bool(val))

class VarChar(Col):

    col_type = 'VARCHAR'

    def __init__(self, size=100, default_value=None, nullable=True, primary_key=False, unique=None, on_update=None):
        self.size = size 
        super().__init__(col_type=VarChar.col_type, default_value=default_value, nullable=nullable, primary_key=primary_key, unique=unique, on_update=on_update)

    def get_size(self):
        return self.size

    def get_col_type(self):
        return f'VARCHAR({str(self.size)})'

    def get_aws_value_type(self):
        return 'stringValue'

class DateTime(Col):

    col_type = 'DATETIME(6)'

    def __init__(self, default_value=None, nullable=True, primary_key=False, unique=None, on_update=None):
        super().__init__(col_type=DateTime.col_type, default_value=default_value, nullable=nullable, primary_key=primary_key, unique=unique, on_update=on_update)
    
    # Always just get the max precision
    def get_col_type(self):
        return f'DATETIME(6)'

    def get_aws_value_type(self):
        return 'stringValue'
    
    def set_value(self, val):
        if val is None or 'CURRENT_TIMESTAMP' in val:
            super().set_value(None)
        else:
            super().set_value(datetime.strptime(val, "%Y-%m-%d %H:%M:%S.%f"))

class JsonColumn(Col):

    col_type = 'JSON'

    def __init__(self, default_value=None, nullable=True, unique=None, on_update=None):
        super().__init__(col_type=JsonColumn.col_type, default_value=default_value, nullable=nullable, unique=unique, on_update=on_update)

    def get_col_type(self):
        return 'JSON'

    def get_aws_value_type(self):
        return 'stringValue'
    

