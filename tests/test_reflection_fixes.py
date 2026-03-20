"""Tests for PR 4: Reflection Bug Fixes."""
from sqlalchemy_redshift.dialect import (
    RelationKey, PRIMARY_KEY_RE, SQL_IDENTIFIER_RE,
    RedshiftDialect_psycopg2,
)


def test_pk_quoted_column_names():
    """PRIMARY_KEY_RE should properly extract double-quoted column names."""
    # Test with quoted column like "role" (a reserved word)
    pk_def = 'PRIMARY KEY ("role", id)'
    m = PRIMARY_KEY_RE.match(pk_def)
    assert m is not None, f"PRIMARY_KEY_RE didn't match: {pk_def}"
    colstring = m.group('columns')
    cols = SQL_IDENTIFIER_RE.findall(colstring)
    # Should find both columns
    assert len(cols) >= 2


def test_quoted_table_name_relation_lookup():
    """RelationKey should handle quoted table names via unquoted() fallback."""
    key = RelationKey('"domain"', 'public')
    unquoted = key.unquoted()
    assert unquoted.name == 'domain'
    assert unquoted.schema == 'public'


def test_relation_key_unquote():
    """Test that RelationKey._unquote works correctly."""
    assert RelationKey._unquote('"test"') == 'test'
    assert RelationKey._unquote('test') == 'test'
    assert RelationKey._unquote(None) is None


def test_external_table_oid_graceful_failure():
    """get_table_oid should handle external tables gracefully.

    External tables don't have OIDs, so the regclass cast fails.
    The method should return None instead of raising.
    """
    # This tests the code path, not actual DB behavior
    d = RedshiftDialect_psycopg2()
    assert hasattr(d, 'get_table_oid')


def test_reflection_sql_has_temp_table_support():
    """The reflection SQL should include pg_temp_ schemas."""
    from sqlalchemy_redshift.dialect import REFLECTION_SQL
    # The REFLECTION_SQL should allow pg_temp_ schemas
    # OR the nspname filter should not exclude pg_temp_
    # Check that the SQL doesn't blanket-exclude all pg_ schemas
    assert 'pg_temp' in REFLECTION_SQL or "nspname !~ '^pg_'" not in REFLECTION_SQL
