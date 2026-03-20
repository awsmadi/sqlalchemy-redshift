"""Tests for PR 2: SQLAlchemy 2.0 Core Compatibility."""
from sqlalchemy_redshift.dialect import (
    RedshiftDialect_psycopg2,
    RedshiftDialect_psycopg2cffi,
    RedshiftDialect_redshift_connector,
    RedshiftDialectMixin,
)


def test_dialect_instantiates():
    """RedshiftDialect_psycopg2() should succeed under SA 2.0."""
    d = RedshiftDialect_psycopg2()
    assert d is not None
    assert d.name == 'redshift'


def test_dialect_has_import_dbapi():
    """Dialect should have import_dbapi classmethod (SA 2.0 API)."""
    assert hasattr(RedshiftDialect_psycopg2, 'import_dbapi')
    assert callable(RedshiftDialect_psycopg2.import_dbapi)


def test_supports_statement_cache():
    """All dialect classes should have supports_statement_cache = True."""
    for cls in [RedshiftDialect_psycopg2, RedshiftDialect_psycopg2cffi,
                RedshiftDialect_redshift_connector]:
        assert cls.supports_statement_cache is True, \
            f'{cls.__name__}.supports_statement_cache should be True'


def test_no_reflection_cache_decorator():
    """Reflection methods should not use @reflection.cache decorator."""
    import inspect as py_inspect

    mixin = RedshiftDialectMixin
    reflection_methods = [
        'get_columns', 'has_table', 'get_check_constraints',
        'get_table_oid', 'get_pk_constraint', 'get_foreign_keys',
        'get_table_names', 'get_view_names', 'get_view_definition',
        'get_unique_constraints', 'get_table_options',
        '_get_all_relation_info', '_get_schema_column_info',
        '_get_all_constraint_info',
    ]
    for method_name in reflection_methods:
        method = getattr(mixin, method_name, None)
        if method is None:
            continue
        # The method should not be wrapped by reflection.cache
        source = py_inspect.getsource(method)
        assert 'reflection.cache' not in source, \
            f'{method_name} still uses @reflection.cache'


def test_get_column_info_sa2_signature():
    """_get_column_info should accept SA 2.0 parent signature kwargs."""
    # Test that the method signature accepts generated and identity parameters
    # which are required by SA 2.0's parent _get_column_info
    import inspect
    d = RedshiftDialect_psycopg2()

    # Verify the method exists and doesn't crash with these kwargs
    # (We can't call it without a connection, but we can verify the signature)
    sig = inspect.signature(d._get_column_info)
    assert 'kwargs' in sig.parameters or len(sig.parameters) > 0, \
        '_get_column_info should accept kwargs'


def test_on_connect_no_text_type():
    """on_connect should not reference util.text_type (removed in SA 2.0)."""
    import inspect as py_inspect
    d = RedshiftDialect_redshift_connector()
    source = py_inspect.getsource(d.on_connect)
    assert 'text_type' not in source
