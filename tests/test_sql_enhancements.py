"""Tests for PR 9: SQL Dialect Enhancements."""
import inspect

import sqlalchemy as sa
from sqlalchemy.schema import CreateTable

from sqlalchemy_redshift.dialect import (
    RedshiftDDLCompiler,
    REFLECTION_SQL,
)


def test_dialect_options_for_encode(stub_redshift_dialect):
    """redshift_encode='lzo' should work via dialect_options."""
    meta = sa.MetaData()
    t = sa.Table(
        't1',
        meta,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, redshift_encode='lzo'),
    )
    ddl = str(CreateTable(t).compile(dialect=stub_redshift_dialect))
    assert 'ENCODE lzo' in ddl


def test_dialect_options_for_distkey(stub_redshift_dialect):
    """redshift_distkey=True should work via dialect_options."""
    meta = sa.MetaData()
    t = sa.Table(
        't1',
        meta,
        sa.Column('id', sa.Integer, primary_key=True, redshift_distkey=True),
        sa.Column('name', sa.String),
    )
    ddl = str(CreateTable(t).compile(dialect=stub_redshift_dialect))
    assert 'DISTKEY' in ddl


def test_dialect_options_for_sortkey(stub_redshift_dialect):
    """redshift_sortkey=True should work via dialect_options."""
    meta = sa.MetaData()
    t = sa.Table(
        't1',
        meta,
        sa.Column('id', sa.Integer, primary_key=True, redshift_sortkey=True),
        sa.Column('name', sa.String),
    )
    ddl = str(CreateTable(t).compile(dialect=stub_redshift_dialect))
    assert 'SORTKEY' in ddl


def test_fetch_redshift_column_attributes_uses_dialect_options():
    """_fetch_redshift_column_attributes should use dialect_options['redshift']."""
    source = inspect.getsource(
        RedshiftDDLCompiler._fetch_redshift_column_attributes
    )
    # Verify that dialect_options['redshift'] is used
    assert "dialect_options['redshift']" in source
    # The old info dict fallback from SA <1.3.0 should not be present
    # (it was removed in PR 1 as part of dropping old SQLAlchemy support)
    assert 'hasattr(column, \'info\')' not in source


def test_reflection_sql_uses_format_params():
    """Internal reflection SQL should use format params, not string concatenation."""
    # The SQL should use {schema_clause} and {table_clause} format params
    assert '{schema_clause}' in REFLECTION_SQL
    assert '{table_clause}' in REFLECTION_SQL
    # Verify multiple occurrences (3 UNION clauses in the query)
    assert REFLECTION_SQL.count('{schema_clause}') >= 3
    assert REFLECTION_SQL.count('{table_clause}') >= 3


def test_dialect_options_for_identity(stub_redshift_dialect):
    """redshift_identity should work via dialect_options."""
    meta = sa.MetaData()
    t = sa.Table(
        't1',
        meta,
        sa.Column('id', sa.Integer, primary_key=True, redshift_identity=(100, 10)),
        sa.Column('name', sa.String),
    )
    ddl = str(CreateTable(t).compile(dialect=stub_redshift_dialect))
    assert 'IDENTITY(100,10)' in ddl


def test_dialect_options_combined(stub_redshift_dialect):
    """Multiple dialect_options should work together."""
    meta = sa.MetaData()
    t = sa.Table(
        't1',
        meta,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column(
            'name',
            sa.String,
            redshift_encode='lzo',
            redshift_distkey=True,
            redshift_sortkey=True,
        ),
    )
    ddl = str(CreateTable(t).compile(dialect=stub_redshift_dialect))
    assert 'ENCODE lzo' in ddl
    assert 'DISTKEY' in ddl
    assert 'SORTKEY' in ddl


def test_autoincrement_creates_identity(stub_redshift_dialect):
    """autoincrement=True should create IDENTITY(1,1)."""
    meta = sa.MetaData()
    t = sa.Table(
        't1',
        meta,
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String),
    )
    ddl = str(CreateTable(t).compile(dialect=stub_redshift_dialect))
    assert 'IDENTITY(1,1)' in ddl


def test_autoincrement_does_not_override_explicit_identity(stub_redshift_dialect):
    """autoincrement=True should not override explicit redshift_identity."""
    meta = sa.MetaData()
    t = sa.Table(
        't1',
        meta,
        sa.Column(
            'id',
            sa.Integer,
            primary_key=True,
            autoincrement=True,
            redshift_identity=(50, 5),
        ),
        sa.Column('name', sa.String),
    )
    ddl = str(CreateTable(t).compile(dialect=stub_redshift_dialect))
    # Should use the explicit identity, not the autoincrement default
    assert 'IDENTITY(50,5)' in ddl
    assert 'IDENTITY(1,1)' not in ddl
