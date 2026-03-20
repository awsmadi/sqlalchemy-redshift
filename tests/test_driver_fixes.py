"""Tests for PR 10: Driver/Connection Fixes."""
import os
import sqlalchemy as sa
from sqlalchemy_redshift.dialect import (
    Psycopg2RedshiftDialectMixin,
)


def test_ssl_cert_path_exists():
    """The bundled SSL cert file should exist and be readable."""
    from importlib.resources import files as _resource_files
    cert_path = str(_resource_files('sqlalchemy_redshift').joinpath('redshift-ca-bundle.crt'))
    assert os.path.exists(cert_path), f'SSL cert not found at {cert_path}'
    assert os.path.getsize(cert_path) > 0, 'SSL cert file is empty'


def test_connection_string_psycopg2():
    """redshift+psycopg2 connection string should parse correctly."""
    url = sa.engine.url.make_url('redshift+psycopg2://user:pass@host:5439/db')
    assert url.drivername == 'redshift+psycopg2'
    assert url.host == 'host'
    assert url.port == 5439
    assert url.database == 'db'


def test_connection_string_redshift_connector():
    """redshift+redshift_connector should parse correctly."""
    url = sa.engine.url.make_url('redshift+redshift_connector://user:pass@host:5439/db')
    assert url.drivername == 'redshift+redshift_connector'


def test_connection_string_default():
    """redshift:// should default to psycopg2."""
    url = sa.engine.url.make_url('redshift://user:pass@host/db')
    assert url.drivername == 'redshift'


def test_importlib_resources_for_ssl():
    """SSL cert should use importlib.resources, not pkg_resources."""
    import inspect
    source = inspect.getsource(Psycopg2RedshiftDialectMixin.create_connect_args)
    assert 'pkg_resources' not in source
    assert '_resource_files' in source or 'importlib.resources' in source
