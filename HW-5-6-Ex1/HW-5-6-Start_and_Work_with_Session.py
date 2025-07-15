# HW-5-6-Start_and_Work_with_Session.py
#PowerShell comand: docker exec -it postgres_db psql -U postgres -c "CREATE DATABASE book_publisher;" 

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from Models_from_book_publishers_scheme import create_tables, Publisher, Book, Shop, Stock, Sale

# Подключение к PostgreSQL через DSN (исправлено: postgresql, не postgressql)
DSN = 'postgresql://postgres:postgres@localhost:5432/book_publisher'
engine = sqlalchemy.create_engine(DSN)

# Создание таблиц (однократно)
create_tables(engine)

# Настройка сессии
Session = sessionmaker(bind=engine)
session = Session()

#  Пример добавления издателя
publisher = Publisher(name='O’Reilly Media')
session.add(publisher)
session.commit()

#  Пример запроса всех издателей
for pub in session.query(Publisher).all():
    print(pub.id, pub.name)

# Завершение
session.close()