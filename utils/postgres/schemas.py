from sqlalchemy import (
    Column,
    String,
    PrimaryKeyConstraint,
    UniqueConstraint,
    ForeignKeyConstraint,
    DateTime,
)
# from sqlalchemy.orm import relationship
from .base import DatabaseBase

class TagsDb(DatabaseBase):
    __tablename__ = 'tags'

    id = Column(String, index=True)
    name = Column(String, index=True)

    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )

class NodesDb(DatabaseBase):
    __tablename__ = 'nodes'

    id = Column(String, index=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

    # tags = relationship("TagsDb", secondary='nodes_tags')

    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('text'),
    )

class NodesTagsDb(DatabaseBase):
    __tablename__ = 'nodes_tags'

    tag_id = Column(String, nullable=False)
    node_id = Column(String, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('tag_id', 'node_id'),
        ForeignKeyConstraint(['tag_id'], ['tags.id']),
        ForeignKeyConstraint(['node_id'], ['nodes.id']),
    )

# class EdgesDb(DatabaseBase):
#     __tablename__ = 'edges'

#     node_1 = Column(String, nullable=False)
#     node_2 = Column(String, nullable=False)

#     __table_args__ = (
#         UniqueConstraint('node_1', 'node_2'),
#         ForeignKeyConstraint(['node_1'], ['nodes.id']),
#         ForeignKeyConstraint(['node_2'], ['nodes.id']),
#     )
