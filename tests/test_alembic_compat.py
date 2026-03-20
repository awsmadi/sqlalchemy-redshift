"""Tests for PR 6: Alembic Compatibility."""
import sqlalchemy as sa
from rs_sqla_test_utils.utils import make_mock_engine


engine = make_mock_engine('redshift+psycopg2')
dialect = engine.dialect


def test_no_returning_in_insert():
    """Alembic INSERT should have no RETURNING clause."""
    meta = sa.MetaData()
    t = sa.Table(
        'alembic_version', meta,
        sa.Column('version_num', sa.String(32), nullable=False),
    )
    stmt = t.insert().values(version_num='abc123')
    compiled = str(stmt.compile(dialect=dialect))
    assert 'RETURNING' not in compiled.upper()


def test_insert_returning_false():
    """Dialect should have insert_returning = False."""
    assert dialect.insert_returning is False


def test_update_returning_false():
    """Dialect should have update_returning = False."""
    assert dialect.update_returning is False


def test_delete_returning_false():
    """Dialect should have delete_returning = False."""
    assert dialect.delete_returning is False


def test_implicit_returning_false():
    """Dialect should have implicit_returning = False."""
    assert dialect.implicit_returning is False


def test_redshift_impl_exists():
    """RedshiftImpl should be available for Alembic integration."""
    try:
        from sqlalchemy_redshift.dialect import RedshiftImpl
        assert RedshiftImpl.__dialect__ == 'redshift'
    except ImportError:
        # Alembic not installed, skip this test
        import pytest
        pytest.skip("Alembic not installed")
