# HW-5-6-Start_and_Work_with_Session.py
#PowerShell comand: docker exec -it postgres_db psql -U postgres -c "CREATE DATABASE book_publisher;" 

#Задание 2

# Используя SQLAlchemy, составить запрос выборки магазинов, продающих целевого издателя.

# Напишите Python скрипт, который:

#     Подключается к БД любого типа на ваш выбор.
#     Импортирует необходимые модели данных.
#     Выводит издателя (publisher), имя или идентификатор которого принимается через input.


import sqlalchemy
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from Models_from_book_publishers_scheme import create_tables, Publisher, Book, Shop, Stock, Sale

# Подключение к PostgreSQL через DSN (исправлено: postgresql, не postgressql)
DSN = 'postgresql://postgres:postgres@localhost:5432/book_publisher'
engine = sqlalchemy.create_engine(DSN)

# Создание таблиц (однократно)
create_tables(engine)

# Настройка сессии
Session = sessionmaker(bind=engine)
session = Session()

# === Повторно запускаемая вставка данных ===
def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        params = {**kwargs}
        if defaults:
            params.update(defaults)
        instance = model(**params)
        session.add(instance)
        return instance

def fill_data(session):

    # === 4 Издателя ===
    publisher_names = ['O’Reilly Media', 
                   'Manning Publications', 
                   'No Starch Press', 
                   'Packt Publishing',]
    publishers = [get_or_create(session, Publisher, name=name) for name in publisher_names]


    # === 24 Книги (по 6 на издателя) ===
    book_data = [
            ('Learning Python', 0),
            ('Fluent Python', 0),
            ('Python Cookbook', 0),
            ('Programming Python', 0),
            ('Python in a Nutshell', 0),
            ('Head First Python', 0),

            ('Grokking Algorithms', 1),
            ('Grokking Deep Learning', 1),
            ('Spring in Action', 1),
            ('Kotlin in Action', 1),
            ('Clojure for the Brave', 1),
            ('Elixir in Action', 1),

            ('Automate the Boring Stuff', 2),
            ('Black Hat Python', 2),
            ('Hacking: The Art of Exploitation', 2),
            ('Linux Basics for Hackers', 2),
            ('Serious Python', 2),
            ('Python Crash Course', 2),

            ('Python Data Science Handbook', 3),
            ('Machine Learning with Python', 3),
            ('Deep Learning with PyTorch', 3),
            ('Natural Language Processing', 3),
            ('Data Analysis with Pandas', 3),
            ('Flask Web Development', 3),
        ]

    books = []
    for title, pub_index in book_data:
        publisher = publishers[pub_index]
        book = session.query(Book).filter_by(title=title).first()
        if not book:
                book = Book(title=title, publisher=publisher)
                session.add(book)
        books.append(book)

    # === 6 Магазинов ===
    shop_names = [
        'Labirint',
        'Bukvoed',
        'Chitai-Gorod',
        'Dom Knigi',
        'Read.ru',
        'Book24',
    ]
    shops = [get_or_create(session, Shop, name=name) for name in shop_names]
    session.commit()  # Чтобы id у магазинов появились

    # === Остатки (Stock): Книги не во всех магазинах, выборочно ===
    # Чтобы книги из издателей были не везде и продажи были только в некоторых магазинах

    # Для удобства словарь с книгами по издателям
    books_by_publisher = {
        0: books[0:6],   # O’Reilly
        1: books[6:12],  # Manning
        2: books[12:18], # No Starch
        3: books[18:24], # Packt
    }

    stocks = []

    # O’Reilly — книги в Labirint и Chitai-Gorod
    for book in books_by_publisher[0]:
        for shop_name in ['Labirint', 'Chitai-Gorod']:
            shop = next(s for s in shops if s.name == shop_name)
            if not session.query(Stock).filter_by(id_book=book.id, id_shop=shop.id).first():
                stock = Stock(book=book, shop=shop, count=5)
                session.add(stock)
                stocks.append(stock)

    # Manning — книги в Bukvoed (есть на складе, но продаж нет)
    for book in books_by_publisher[1]:
        shop = next(s for s in shops if s.name == 'Bukvoed')
        if not session.query(Stock).filter_by(id_book=book.id, id_shop=shop.id).first():
            stock = Stock(book=book, shop=shop, count=7)
            session.add(stock)
            stocks.append(stock)

    # No Starch — книги в Read.ru с продажами
    for book in books_by_publisher[2]:
        shop = next(s for s in shops if s.name == 'Read.ru')
        if not session.query(Stock).filter_by(id_book=book.id, id_shop=shop.id).first():
            stock = Stock(book=book, shop=shop, count=4)
            session.add(stock)
            stocks.append(stock)

    # Packt — книги в Dom Knigi и Book24, продажи только в Dom Knigi
    for book in books_by_publisher[3]:
        for shop_name in ['Dom Knigi', 'Book24']:
            shop = next(s for s in shops if s.name == shop_name)
            if not session.query(Stock).filter_by(id_book=book.id, id_shop=shop.id).first():
                stock = Stock(book=book, shop=shop, count=6 if shop_name == 'Dom Knigi' else 2)
                session.add(stock)
                stocks.append(stock)

    session.commit()  # Сохраним остатки, чтобы получить id

    # === Продажи (Sale): Только там, где реально есть продажи ===
    sales_data = []
    # Для O'Reilly — продается в Labirint (первый склад с O'Reilly)
    o_reilly_stocks = session.query(Stock).join(Book).filter(Book.id_publisher == publishers[0].id,
                                                           Stock.id_shop == next(s.id for s in shops if s.name == 'Labirint')).all()
    if o_reilly_stocks:
        sales_data.append((800.0, datetime(2025, 7, 10), o_reilly_stocks[0], 2))

    # No Starch — продажи в Read.ru
    no_starch_stocks = session.query(Stock).join(Book).filter(Book.id_publisher == publishers[2].id,
                                                              Stock.id_shop == next(s.id for s in shops if s.name == 'Read.ru')).all()
    if no_starch_stocks:
        sales_data.append((620.0, datetime(2025, 7, 14), no_starch_stocks[0], 1))

    # Packt — продажи в Dom Knigi
    packt_stocks = session.query(Stock).join(Book).filter(Book.id_publisher == publishers[3].id,
                                                          Stock.id_shop == next(s.id for s in shops if s.name == 'Dom Knigi')).all()
    if packt_stocks:
        sales_data.append((1100.0, datetime(2025, 7, 15), packt_stocks[0], 1))

    # Добавим продажи в БД, если их ещё нет
    for price, date_sale, stock, count in sales_data:
        existing = session.query(Sale).filter_by(price=price, date_sale=date_sale, id_stock=stock.id, count=count).first()
        if not existing:
            sale = Sale(price=price, date_sale=date_sale, stock=stock, count=count)
            session.add(sale)

    session.commit()
# ------ Запуск функции ---
fill_data(session)

# Пример запроса всех издателей
for pub in session.query(Publisher).all():
    print(pub.id, pub.name)

# ======================================== ЗАДАНИЕ 2: Функция для поиска магазинов по издателю
def find_shops_by_publisher(session):
    user_input = input("Введите имя или ID издателя: ").strip()

    if user_input.isdigit():
        publisher_filter = Publisher.id == int(user_input)
    else:
        publisher_filter = Publisher.name.ilike(f"%{user_input}%")

    query = (
        session.query(Shop.name)
        .join(Stock, Stock.id_shop == Shop.id)
        .join(Sale, Sale.id_stock == Stock.id)
        .join(Book, Book.id == Stock.id_book)
        .join(Publisher, Publisher.id == Book.id_publisher)
        .filter(publisher_filter)
        .distinct()
        .order_by(Shop.name)
    )

    results = query.all()

    if results:
        print("Магазины, продающие книги этого издателя:")
        for shop_name, in results:
            print(f"— {shop_name}")
    else:
        print("Нет магазинов, продающих книги этого издателя.")

# --- Запрос по издателю ---
find_shops_by_publisher(session)

# Завершение
session.close()