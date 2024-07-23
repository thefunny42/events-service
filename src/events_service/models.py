import sqlalchemy
from sqlalchemy import orm


class Base(
    orm.DeclarativeBase,
    orm.MappedAsDataclass,
):
    pass


class Activity(Base):
    __tablename__ = "activity"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, init=False)
    name: orm.Mapped[str] = orm.mapped_column()
    events: orm.Mapped[list["Events"] | None] = orm.relationship(
        back_populates="activity", passive_deletes=True, lazy="selectin"
    )


class Events(Base):
    __tablename__ = "events"
    __table_args__ = (sqlalchemy.UniqueConstraint("activity_id"),)

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, init=False)
    activity_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.ForeignKey("activity.id", ondelete="CASCADE")
    )
    activity: orm.Mapped[Activity] = orm.relationship(
        back_populates="events", single_parent=True, lazy="joined"
    )
