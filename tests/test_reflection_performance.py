"""Tests for PR 5: Reflection Performance — Scoped Queries and Caching."""
from sqlalchemy_redshift.dialect import REFLECTION_SQL


def test_reflection_sql_has_table_clause():
    """REFLECTION_SQL should have {table_clause} placeholder for scoping."""
    assert '{table_clause}' in REFLECTION_SQL


def test_reflection_sql_has_schema_clause():
    """REFLECTION_SQL should have {schema_clause} placeholder for scoping."""
    assert '{schema_clause}' in REFLECTION_SQL


def test_single_table_scoped_query():
    """When table_name is provided, the SQL should include a table filter."""
    # Format the SQL with a specific table
    sql = REFLECTION_SQL.format(
        schema_clause="AND schema = 'public'",
        table_clause="AND table_name = 'my_table'"
    )
    assert "my_table" in sql
    assert "AND table_name = 'my_table'" in sql


def test_all_tables_query():
    """When no table_name, the SQL should have empty table_clause."""
    sql = REFLECTION_SQL.format(
        schema_clause="AND schema = 'public'",
        table_clause=""
    )
    assert "AND table_name" not in sql
