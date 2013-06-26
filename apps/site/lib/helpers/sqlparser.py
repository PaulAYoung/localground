#!/usr/bin/env python
from django.conf import settings
from localground.apps.site.lib import sqlparse
from localground.apps.site.lib.sqlparse import tokens as T
from localground.apps.site.lib.sqlparse.sql import Where, Comparison, Identifier
from datetime import datetime

class FieldTypes(object):
    STRING = 'string'
    DATE = 'date'
    INTEGER = 'integer'
    TAG = 'tag'
    LIST = 'list'
    FLOAT = 'float'
    
class QueryField(object):
    def __init__(self, col_name, id=None, title=None, data_type=None, operator='=',
                    django_col_name=None):
        self.id = id
        self.col_name = col_name
        self.title = title
        self.data_type = data_type
        self.operator = operator
        self.django_col_name = col_name
        if self.django_col_name is None:
            self.django_col_name = col_name   
            
        
    def __repr__(self):
        return str(self.to_dict())
        
    def to_dict(self):
        return {
            'col_name': self.col_name,
            'id': self.id,
            'title': self.title
        }

class WhereCondition(QueryField):
    
    def __init__(self, col_name, id=None, title=None, data_type=FieldTypes.STRING,
                                    operator='=', django_col_name=None,
                                    conjunction='AND', val=None):
        
        super(WhereCondition, self).__init__(col_name, id=id, title=title,
                                data_type=FieldTypes.STRING, operator=operator)
        self.conjunction = conjunction
        self.value_original = self.value = val
        self.parse_value(val)
        
    def __repr__(self):
        return str(self.to_dict(debug=True))
        
    def to_dict(self, debug=False):
        d = {
            'col_name': self.col_name,
            'data_type': self.data_type,
            'operator': self.operator,
            'conjunction': self.conjunction,
            'value': self.value
        }
        if debug:
            d.update({
                'id': self.id,
                'title': self.title,
                'expression': self.get_expression(),
                'django_operator': self.get_django_operator()
            })
        return d
    
    def update(self, query_field):
        self.id = query_field.id
        self.title = query_field.title
    
    def get_django_operator(self):
        sql_lookup = {
            '=': '__exact',
            '>': '__gt',
            '>=': '__gte',
            '<': '__lt',
            '<=': '__lte',
            'LIKE': '__icontains',
            'IN': '__in'
        }
        #not real sql operators, but help with the sql-to-django mapping:
        nonsql_lookup = {
            'STARTS': '__istartswith',
            'ENDS': '__iendswith'
        }
        lookup = {}
        lookup.update(sql_lookup)
        lookup.update(nonsql_lookup)
        return lookup[self.operator]
        
    def get_expression(self, cls=None):
        if cls is not None:
            #one last check to make sure the field being queried is valid:
            legitimate_field = cls.get_field_by_name(self.col_name, self.operator)
            if legitimate_field is None:
                raise Exception('The column name "%s" is invalid' % self.col_name)
        col_name = '%s%s' % (legitimate_field.django_col_name, self.get_django_operator())
        if col_name.find('tags') != -1:
            return {'tags__regex': r'^(%s)' % '|'.join(['.*%s.*' % v for v in self.value]) }
        return { col_name: self.value}
    
    def parse_value(self, val):
        '''
        Based on the value of each query parameter, this method will detect
        and convert the parameter according to the appropriate data type.
        '''
        if val is None: return
        if isinstance(val, list):
            self.parse_list(val)
            return
        
        val = val.strip()
        if val[0] == '\'' and val[-1] == '\'':
            self.value = val[1:-1]
            self.data_type = FieldTypes.STRING
            if self.operator == 'LIKE':
                self.parse_like_clause()
            else:
                self.parse_date()
        else:
            self.parse_numeric(val)
        self.value_original = self.value
        return self.value
    
    def parse_list(self, val):
        '''
        converts the value to a list of values
        '''
        val = [self.parse_value(v) for v in val]
        self.value = val
        self.value_original = ', '.join([str(v) for v in val])
        self.data_type = FieldTypes.LIST
        
    def parse_like_clause(self):
        '''
        make the "like" operator django-compatible
        '''
        if self.value[0] == '%' and self.value[-1] == '%':
            self.value = self.value[1:-1]
        elif self.value[0] == '%':
            self.value = self.value[1:]
            self.operator = 'ENDS'
        elif self.value[-1] == '%':
            self.value = self.value[:-1]
            self.operator = 'STARTS'
        else:
            self.operator = '='
            
    def parse_date(self):
        '''
        Parses the value as a date, if applicable
        '''
        for format in settings.DATE_INPUT_FORMATS + settings.DATETIME_INPUT_FORMATS:
            try:
                self.value = datetime.strptime(self.value, format)
                self.data_type = FieldTypes.DATE
                break
            except: pass
            
    def parse_numeric(self, val):
        if val.find('.') != -1:
            try:
                self.value = float(val)
                self.data_type = FieldTypes.FLOAT
            except: pass
        else:
            try:
                self.value = int(val)
                self.data_type = FieldTypes.INTEGER
            except: pass
    
class OrderingCondition(QueryField):
    
    def __init__(self, col_name, id=None, title=None, data_type=FieldTypes.STRING,
                                    direction='asc'):
        
        super(WhereCondition, self).__init__(col_name, id=id, title=title,
                                data_type=FieldTypes.STRING, operator=None,
                                 django_col_name=None)

class QueryParser(object):
    error = False
    
    def __init__(self, query_text, debug=True):
        self.query_text = query_text
        self.where_conditions = []
        if debug:
            self.parse()
        else:
            try:
                self.parse()
            except:
                self.error = True
                self.error_message = 'Invalid query "%s"' % self.query_text
        
    def get_condition(self, col_name, operator):
        for c in self.where_conditions:
            if c.col_name.lower() == col_name.lower() and \
                c.operator.lower() == operator.lower():
                return c
        return None
        
    def __repr__(self):
        return 'Filter Text: %s\n%s' % (self.query_text, self.to_dict_list(debug=True))
        
    def __str__(self):
        return 'Filter Text: %s\n%s' % (self.query_text, self.to_dict_list(debug=True))
        
    def to_dict_list(self, debug=False):
        return [c.to_dict(debug=True) for c in self.where_conditions]
        
    def remove_whitespaces(self, tokens):
        stripped = []
        for t in tokens:
            if t.ttype != T.Whitespace: stripped.append(t)
        return stripped
    
    def parse(self):
        self.query_text = sqlparse.format(self.query_text, reindent=False, keyword_case='upper')
        statement = sqlparse.parse(self.query_text)[0]
        where_clause = None
        for i, t in enumerate(statement.tokens):
            if isinstance(t, Where):
                where_clause =  t
            #break
            
        tokens = self.remove_whitespaces(where_clause.tokens)
        tokens.pop(0)
        for i in range(0, len(tokens)):
            t = tokens[i]
            #parse equalities and inequalities:
            if isinstance(t, Comparison):
                children = [str(c) for c in self.remove_whitespaces(t.tokens)]
                wc = WhereCondition(children[0], operator=children[1], val=children[2])
                if len(self.where_conditions) > 0: wc.conjunction = str(tokens[i-1])
                self.where_conditions.append(wc)
                
            elif t.ttype == T.Keyword:
                #parse "in" clauses:
                if str(t) == 'IN':
                    lst = str(self.remove_whitespaces(tokens[i+1].tokens)[1]).split(',')
                    wc = WhereCondition(str(tokens[i-1]), operator='IN', val=lst)
                    if len(self.where_conditions) > 0: wc.conjunction = str(tokens[i-2])
                    self.where_conditions.append(wc)
                    
                #parse "like" clauses:
                elif str(t) == 'LIKE':
                    wc = WhereCondition(str(tokens[i-1]), operator='LIKE', val=str(tokens[i+1]))
                    if len(self.where_conditions) > 0: wc.conjunction = str(tokens[i-2])
                    self.where_conditions.append(wc)
             
    def extend_query(self, q):
        from django.db.models import Q
        args = Q(**self.where_conditions[0].get_expression(q.model))
        if len(self.where_conditions) > 1:
            for i in range(1, len(self.where_conditions)):
                c = self.where_conditions[i]
                if c.conjunction == 'AND':
                    args = args & Q(**c.get_expression(q.model))
                else: #OR condition:
                    args = args | Q(**c.get_expression(q.model))
        
        q = q.filter(args)
        return q
        
        