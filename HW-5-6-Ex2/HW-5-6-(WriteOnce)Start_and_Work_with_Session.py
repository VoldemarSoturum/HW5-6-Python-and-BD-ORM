# HW-5-6-Start_and_Work_with_Session.py
# PowerShell command: docker exec -it postgres_db psql -U postgres -c "CREATE DATABASE book_publisher;"


#🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄
#!!!!!!!!!!!Для запуска единожды, второй раз будут дубликаты в БД!!!!!!!!!!!🗄🗄
#🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄🗄


# Задание 2
# Используя SQLAlchemy, составить запрос выборки магазинов, продающих целевого издателя.
# Напишите Python скрипт, который:
#     Подключается к БД любого типа на ваш выбор.
#     Импортирует необходимые модели данных.
#     Выводит издателя (publisher), имя или идентификатор которого принимается через input.

#Импорт необходимых библиотек и модулей
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from Models_from_book_publishers_scheme import create_tables, Publisher, Book, Shop, Stock, Sale
from datetime import datetime  # добавь для Sale

# Подключение к PostgreSQL
DSN = 'postgresql://postgres:postgres@localhost:5432/book_publisher'
engine = sqlalchemy.create_engine(DSN)

# Создание таблиц (однократно)
create_tables(engine)

# Настройка сессии
Session = sessionmaker(bind=engine)
session = Session()

# ------------------------------Наполнение БД данными

# Добавление издателей
publishers = [
    Publisher(name='O’Reilly Media'),
    Publisher(name='Manning Publications'),
    Publisher(name='No Starch Press'),
    Publisher(name='Packt Publishing')
]
session.add_all(publishers)
session.commit()

# === ВАЖНО!!!! Заново получить из базы с ID и связкой сессии ===
publishers = session.query(Publisher).order_by(Publisher.id).all()

# Добавление книг
books = [
    Book(title='Learning Python', publisher=publishers[0]),
    Book(title='Fluent Python', publisher=publishers[0]),
    Book(title='Python Cookbook', publisher=publishers[0]),
    Book(title='Programming Python', publisher=publishers[0]),
    Book(title='Python in a Nutshell', publisher=publishers[0]),
    Book(title='Head First Python', publisher=publishers[0]),

    Book(title='Grokking Algorithms', publisher=publishers[1]),
    Book(title='Grokking Deep Learning', publisher=publishers[1]),
    Book(title='Spring in Action', publisher=publishers[1]),
    Book(title='Kotlin in Action', publisher=publishers[1]),
    Book(title='Clojure for the Brave', publisher=publishers[1]),
    Book(title='Elixir in Action', publisher=publishers[1]),

    Book(title='Automate the Boring Stuff', publisher=publishers[2]),
    Book(title='Black Hat Python', publisher=publishers[2]),
    Book(title='Hacking: The Art of Exploitation', publisher=publishers[2]),
    Book(title='Linux Basics for Hackers', publisher=publishers[2]),
    Book(title='Serious Python', publisher=publishers[2]),
    Book(title='Python Crash Course', publisher=publishers[2]),

    Book(title='Python Data Science Handbook', publisher=publishers[3]),
    Book(title='Machine Learning with Python', publisher=publishers[3]),
    Book(title='Deep Learning with PyTorch', publisher=publishers[3]),
    Book(title='Natural Language Processing', publisher=publishers[3]),
    Book(title='Data Analysis with Pandas', publisher=publishers[3]),
    Book(title='Flask Web Development', publisher=publishers[3]),
]
session.add_all(books)
session.commit()
#=====================================================================================
# Добавление магазинов
shops = [
    Shop(name='Labirint'),        # 0
    Shop(name='Bukvoed'),         # 1
    Shop(name='Chitai-Gorod'),    # 2
    Shop(name='Read.ru'),         # 3
    Shop(name='Book24'),          # 4
    Shop(name='Dom Knigi'),       # 5
    Shop(name='Books & More'),    # 6
    Shop(name='Kniga.com'),       # 7
    Shop(name='MegaBooks'),       # 8
]
session.add_all(shops)
session.commit()

# Назначим ID издателей для читаемости
oreilly = publishers[0]
manning = publishers[1]
nostarch = publishers[2]
packt = publishers[3]

# Сопоставление издателя и магазинов, где продаются его книги
publisher_shop_map = {
    oreilly.id: [shops[0], shops[4]],            # Labirint, Book24
    manning.id: [shops[0], shops[1], shops[4]],   # Labirint, Bukvoed, Book24
    nostarch.id: [shops[2], shops[3]],            # Chitai-Gorod, Read.ru
    packt.id: [shops[3], shops[5]],               # Read.ru, Dom Knigi
}

# Добавление остатков только в нужные магазины
stocks = []
for book in books:
    publisher_id = book.publisher.id
    target_shops = publisher_shop_map.get(publisher_id, [])
    for i, shop in enumerate(target_shops):
        stocks.append(Stock(book=book, shop=shop, count=5 + i))
session.add_all(stocks)
session.commit()
# Получим корректные stock из базы
stocks = session.query(Stock).all()
#=====================================================================================

# Добавление продаж — по одному stock для каждого издателя
sales = []

# O'Reilly Media — 'Learning Python' в 'Labirint'
stock_oreilly = session.query(Stock).join(Book).join(Shop).filter(
    Book.title == 'Learning Python',
    Shop.name == 'Labirint'
).first()

# Manning Publications — 'Grokking Algorithms' в 'Bukvoed'
stock_manning = session.query(Stock).join(Book).join(Shop).filter(
    Book.title == 'Grokking Algorithms',
    Shop.name == 'Bukvoed'
).first()

# No Starch Press — 'Automate the Boring Stuff' в 'Chitai-Gorod'
stock_nostarch = session.query(Stock).join(Book).join(Shop).filter(
    Book.title == 'Automate the Boring Stuff',
    Shop.name == 'Chitai-Gorod'
).first()

# Packt Publishing — 'Python Data Science Handbook' в 'Dom Knigi'
stock_packt = session.query(Stock).join(Book).join(Shop).filter(
    Book.title == 'Python Data Science Handbook',
    Shop.name == 'Dom Knigi'
).first()

# Добавим продажи, если такие stock найдены
if stock_oreilly:
    sales.append(Sale(price=800.0, date_sale=datetime(2025, 7, 10), stock=stock_oreilly, count=2))
if stock_manning:
    sales.append(Sale(price=950.0, date_sale=datetime(2025, 7, 11), stock=stock_manning, count=1))
if stock_nostarch:
    sales.append(Sale(price=1020.0, date_sale=datetime(2025, 7, 12), stock=stock_nostarch, count=3))
if stock_packt:
    sales.append(Sale(price=770.0, date_sale=datetime(2025, 7, 13), stock=stock_packt, count=2))

session.add_all(sales)
session.commit()

# === Конец вставки ===

# Проверка: список издателей
for pub in session.query(Publisher).all():
    print(pub.id, pub.name)

# === Функция поиска магазинов по издателю (где были продажи) ===
def find_shops_by_publisher_with_sales(session):
    user_input = input("\nВведите имя или ID издателя для поиска магазинов с продажами: ").strip()

    if user_input.isdigit():
        publisher_filter = Publisher.id == int(user_input)
    else:
        publisher_filter = Publisher.name.ilike(f"%{user_input}%")

    query = (
        session.query(Shop.name)                               # Запрашиваем названия магазинов
        .join(Stock, Stock.id_shop == Shop.id)                # Присоединяем таблицу остатков (Stock) по id магазина
        .join(Sale, Sale.id_stock == Stock.id)                # Присоединяем таблицу продаж (Sale) по id остатка
        .join(Book, Book.id == Stock.id_book)                 # Присоединяем таблицу книг (Book) по id книги в остатках
        .join(Publisher, Publisher.id == Book.id_publisher)   # Присоединяем таблицу издателей (Publisher) по id издателя книги
        .filter(publisher_filter)                              # Фильтруем по условию: либо имя, либо ID издателя (publisher_filter — переданный пользователем)
        .distinct()                                           # Убираем дубликаты магазинов (если один магазин продавал несколько книг издателя)
        .order_by(Shop.name)                                  # Сортируем результат по названию магазина по алфавиту
            )

    results = query.all()

    if results:
        print("Магазины, где были ПРОДАЖИ книг этого издателя:")
        for shop_name, in results:
            print(f"— {shop_name}")
    else:
        print("Нет магазинов с продажами книг этого издателя.")

# === Вызов функции поиска ===
find_shops_by_publisher_with_sales(session)

# Завершение
session.close()