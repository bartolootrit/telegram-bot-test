from .model import *
import random

class DB:
    """no SQL injection from a user input"""

    @classmethod
    def categories(cls):
        return Category.select().where(Category.is_active == 1).naive()

    @classmethod
    def dishes_by_category(cls, category_id):
        return (Dish.select(Dish, Category)
                .join(Category)
                .where((Category.is_active == 1) & (Dish.is_active == 1) & (Category.id == category_id))
                .order_by(Dish.name))

    @classmethod
    def dish(cls, id):
        return Dish.select() \
            .join(Category) \
            .where((Category.is_active == 1) & (Dish.is_active == 1) & (Dish.id == id)).get()

    @classmethod
    def dishes(cls, id_list):
        #ids could be non-unique
        for dish_id in id_list:
            yield cls.dish(dish_id)

    @classmethod
    def add_order(cls, telegram_id, employee_name, dish_id_list):
        em = cls.get_or_add_employee(telegram_id, employee_name)
        with BaseModel.db.transaction():
            em_order = EmployeeOrder.create(employee_id = em.id)
            data = ({'employee_order': em_order.id,
                     'dish': dish.id,
                     'dish_price': dish.price,
                     'dish_quantity': quantity}
                    for quantity, dish in cls._dishes_with_quantity(dish_id_list))

            EmployeeOrderDish.insert_many(data).execute()

    @classmethod
    def get_or_add_employee(cls, telegram_id, employee_name):
        em = None
        try:
            em = Employee.get(Employee.id == telegram_id)
        except:
            em = Employee.create(id = telegram_id, name = employee_name, is_active = 1)
        if em.is_active == 0:
            em.is_active = 1
            em.save()
        return em

    @classmethod
    def orders(cls, telegram_id):
        return Employee.select(Dish.name,
                               EmployeeOrder.id,
                               EmployeeOrder.order_date,
                               EmployeeOrderDish.dish_price,
                               EmployeeOrderDish.dish_quantity)\
            .join(EmployeeOrder) \
            .join(EmployeeOrderDish) \
            .join(Dish) \
            .join(Category)\
            .where(Employee.id == telegram_id & Employee.is_active == 1)\
            .order_by(EmployeeOrder.order_date, Category.id)

    @classmethod
    def gen_prices(cls):
        Dish.update(price = random.randint(1, 500)).where(Dish.is_active == 1).execute()

    @classmethod
    def populate_if_empty(cls):
        try:
            cat = Category.get()
        except:
            BaseModel.db.create_tables([Category, Dish, Employee, EmployeeOrder, EmployeeOrderDish], True)
            cls._create_category_with_dishes('Soups', {'Borsch': 100, 'Pea soup': 90, 'Bean soup': 120})
            cls._create_category_with_dishes('Main courses', {'Pilaff': 300, 'Chuchvara': 150, 'Guksu': 160})
            cls._create_category_with_dishes('Desserts', {'Baklava': 90, 'Сhak-chak': 100, 'Sherbet': 50})

    @classmethod
    def _dishes_with_quantity(cls, id_list):
        """
        Returns:
             tuple(quantity, dish_obj)
        """
        id_list.sort()
        prev_id = id_list[0]
        prev_quantity = 0
        for id in id_list:
            if prev_id != id:
                yield (prev_quantity, cls.dish(prev_id))
                prev_quantity = 0
                prev_id = id
            prev_quantity += 1
        yield (prev_quantity, cls.dish(prev_id))

    @staticmethod
    def _create_category_with_dishes(category_name, dishes):
        cat = Category.create(name=category_name)
        cat.save()
        data = ({'category': cat, 'name': name, 'price': price} for name, price in dishes.items())
        Dish.insert_many(data).execute()