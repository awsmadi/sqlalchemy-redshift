"""Tests for PR 7: DDL Compiler Fixes."""
import sqlalchemy as sa
from sqlalchemy.schema import CreateTable
from rs_sqla_test_utils.utils import make_mock_engine


engine = make_mock_engine('redshift+psycopg2')
dialect = engine.dialect


def test_fk_no_on_delete_cascade():
    """FK DDL should not include ON DELETE CASCADE."""
    meta = sa.MetaData()
    sa.Table(
        'parent', meta,
        sa.Column('id', sa.Integer, primary_key=True),
    )
    child = sa.Table(
        'child', meta,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('parent_id', sa.Integer,
                  sa.ForeignKey('parent.id', ondelete='CASCADE')),
    )
    ddl = str(CreateTable(child).compile(dialect=dialect))
    assert 'ON DELETE' not in ddl
    assert 'FOREIGN KEY' in ddl


def test_fk_no_on_update():
    """FK DDL should not include ON UPDATE."""
    meta = sa.MetaData()
    sa.Table(
        'parent', meta,
        sa.Column('id', sa.Integer, primary_key=True),
    )
    child = sa.Table(
        'child', meta,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('parent_id', sa.Integer,
                  sa.ForeignKey('parent.id', onupdate='SET NULL')),
    )
    ddl = str(CreateTable(child).compile(dialect=dialect))
    assert 'ON UPDATE' not in ddl


def test_no_sequence_support():
    """Dialect should report no sequence support."""
    assert dialect.supports_sequences is False


def test_autoincrement_identity():
    """autoincrement=True should generate IDENTITY(1,1) DDL."""
    meta = sa.MetaData()
    t = sa.Table(
        't1', meta,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String),
    )
    ddl = str(CreateTable(t).compile(dialect=dialect))
    assert 'IDENTITY(1,1)' in ddl or 'IDENTITY (1,1)' in ddl


def test_cte_follows_insert_true():
    """cte_follows_insert should be True for Redshift."""
    assert dialect.cte_follows_insert is True


def test_insert_no_returning():
    """INSERT should not have RETURNING clause."""
    meta = sa.MetaData()
    t = sa.Table(
        't1', meta,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String),
    )
    stmt = t.insert().values(name='test')
    compiled = str(stmt.compile(dialect=dialect))
    assert 'RETURNING' not in compiled


def test_implicit_returning_false():
    """Dialect should have implicit_returning = False."""
    assert dialect.implicit_returning is False
