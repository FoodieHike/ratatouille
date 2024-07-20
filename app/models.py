from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Date, CheckConstraint, ForeignKey, Boolean


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    password: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    tg_id: Mapped[int] = mapped_column(
        Integer, unique=True, nullable=False
    )
    disabled: Mapped[bool] = mapped_column(Boolean)


class Campaign(Base):
    __tablename__ = 'campaigns'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    startdate: Mapped[Date] = mapped_column(Date)
    enddate: Mapped[Date] = mapped_column(Date)
    firstfood: Mapped[int] = mapped_column(Integer, nullable=False)
    lastfood: Mapped[int] = mapped_column(Integer, nullable=False)
    user_tg_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.tg_id', ondelete='SET NULL'), nullable=False
    )

    __table_args__ = (
        CheckConstraint('firstfood IN (1, 2, 3)', name='check_firstfood'),
        CheckConstraint('lastfood IN (1, 2, 3)', name='check_lastfood'),
    )


class People(Base):
    __tablename__ = 'people'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campaign_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('campaigns.id', ondelete='SET NULL'),
        nullable=False
    )
    fio: Mapped[str] = mapped_column(String(255), nullable=False)
    food_preferences: Mapped[str] = mapped_column(String(255))


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product: Mapped[str] = mapped_column(String(255), nullable=False)


class Menu(Base):
    __tablename__ = 'menu'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    feed_type: Mapped[str] = mapped_column(String(255))
    feed_name: Mapped[str] = mapped_column(String(255))
    product_name: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer)
    units: Mapped[str] = mapped_column(String(255))
    food_preferences: Mapped[str] = mapped_column(String(255))
    id_product: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'))
