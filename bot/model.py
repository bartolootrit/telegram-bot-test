import datetime
from peewee import *
from .config import Config

class UnknownField(object):
    def __init__(self, *_, **__): pass

class C:
    def f(self):
        return 1

class A(Model):
    class Meta:
        data = C()

class BaseModel(Model):
    class Meta:
        database = SqliteDatabase(Config.db_path())
    db = Meta.database#It's a workaround, because BaseModel.Meta.database isn't compiling

class Category(BaseModel):
    is_active = IntegerField(default=1)
    name = TextField()

    class Meta:
        db_table = 'category'

class Dish(BaseModel):
    category = ForeignKeyField(db_column='category_id', rel_model=Category, to_field='id')
    is_active = IntegerField(default=1)
    name = TextField()
    price = FloatField()

    class Meta:
        db_table = 'dish'

class Employee(BaseModel):
    id = IntegerField(primary_key=True)
    is_active = IntegerField(default=1)
    name = TextField()
    class Meta:
        db_table = 'employee'

class EmployeeOrder(BaseModel):
    employee = ForeignKeyField(db_column='employee_id', rel_model=Employee, to_field='id')
    order_date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = 'employee_order'

class EmployeeOrderDish(BaseModel):
    dish = ForeignKeyField(db_column='dish_id', rel_model=Dish, to_field='id')
    dish_price = FloatField()
    dish_quantity = IntegerField(default=1)
    employee_order = ForeignKeyField(db_column='employee_order_id', rel_model=EmployeeOrder, to_field='id')

    class Meta:
        db_table = 'employee_order_dish'
        indexes = (
            (('employee_order', 'dish'), True),
        )
        primary_key = CompositeKey('dish', 'employee_order')


class SqliteSequence(BaseModel):
    name = UnknownField(null=True)  # 
    seq = UnknownField(null=True)  # 

    class Meta:
        db_table = 'sqlite_sequence'
        primary_key = False

