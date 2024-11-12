from sqlmodel import SQLModel, Field, create_engine, Session, Relationship, select

engine = create_engine('sqlite:///orm.db')

class Author(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)
    email: str = Field(max_length=50)

    books: list["Book"] = Relationship(back_populates="author")

class Book(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(max_length=100)
    content: str
    author_id: int = Field(foreign_key="author.id")

    author: Author = Relationship(back_populates="books")

SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    author1 = Author(name = 'Alice', email = 'alice@example.com')
    author2 = Author(name = 'Bob', email = 'bob@example.com')
    book1 = Book(title = 'Alice First Book', content = 'This is sample content', author = author1)
    book2 = Book(title = 'Bob First Book', content = 'This is sample content', author = author2)
    book3 = Book(title = 'Random Book3', content = 'This is sample content', author = author2)

    session.add_all([author1, author2, book1, book2, book3])
    session.commit()

with Session(engine) as session:
    statement = select(Book).where(Book.title == 'Alice First Book')
    results = session.exec(statement).first()
    if results:
        results.title = 'Alice 2nd Book'
        session.add(results)
        session.commit()
        session.refresh(results)
        print("Updated.")

