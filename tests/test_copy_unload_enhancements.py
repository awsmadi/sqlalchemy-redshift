"""Tests for PR 8: COPY/UNLOAD Command Enhancements."""
import pytest
import sqlalchemy as sa
from sqlalchemy_redshift.commands import UnloadFromSelect, CopyCommand
from rs_sqla_test_utils.utils import clean, compile_query, make_mock_engine


engine = make_mock_engine('redshift+psycopg2')
dialect = engine.dialect

table = sa.Table(
    't1', sa.MetaData(),
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.Unicode),
    sa.Column('region', sa.String(50)),
)


def test_unload_iam_role_default():
    """UNLOAD should support IAM_ROLE DEFAULT."""
    unload = UnloadFromSelect(
        select=sa.select(sa.func.count(table.c.id)),
        unload_location='s3://bucket/key',
        iam_role='default',
    )
    compiled = clean(compile_query(unload, dialect))
    assert 'IAM_ROLE DEFAULT' in compiled
    assert 'CREDENTIALS' not in compiled


def test_copy_iam_role_default():
    """COPY should support IAM_ROLE DEFAULT."""
    copy = CopyCommand(
        table,
        data_location='s3://bucket/data/',
        iam_role='default',
    )
    compiled = clean(compile_query(copy, dialect))
    assert 'IAM_ROLE DEFAULT' in compiled
    assert 'CREDENTIALS' not in compiled


def test_unload_partition_by():
    """UNLOAD should support PARTITION BY clause."""
    unload = UnloadFromSelect(
        select=sa.select(table.c.id, table.c.name, table.c.region),
        unload_location='s3://bucket/key',
        iam_role='default',
        partition_by=['region'],
    )
    compiled = clean(compile_query(unload, dialect))
    assert 'PARTITION BY (region)' in compiled


def test_unload_partition_by_multiple():
    """UNLOAD should support multiple PARTITION BY columns."""
    unload = UnloadFromSelect(
        select=sa.select(table.c.id, table.c.name, table.c.region),
        unload_location='s3://bucket/key',
        iam_role='default',
        partition_by=['name', 'region'],
    )
    compiled = clean(compile_query(unload, dialect))
    assert 'PARTITION BY (name, region)' in compiled


def test_copy_iam_role_arn_direct():
    """COPY with iam_role should use IAM_ROLE 'arn' instead of WITH CREDENTIALS AS."""
    arn = 'arn:aws:iam::123456789012:role/MyRedshiftRole'
    copy = CopyCommand(
        table,
        data_location='s3://bucket/data/',
        iam_role=arn,
    )
    compiled = clean(compile_query(copy, dialect))
    assert f"IAM_ROLE '{arn}'" in compiled
    assert 'WITH CREDENTIALS AS' not in compiled


def test_unload_iam_role_arn_direct():
    """UNLOAD with iam_role should use IAM_ROLE 'arn'."""
    arn = 'arn:aws:iam::123456789012:role/MyRedshiftRole'
    unload = UnloadFromSelect(
        select=sa.select(sa.func.count(table.c.id)),
        unload_location='s3://bucket/key',
        iam_role=arn,
    )
    compiled = clean(compile_query(unload, dialect))
    assert f"IAM_ROLE '{arn}'" in compiled
    assert 'CREDENTIALS' not in compiled


def test_iam_role_and_credentials_mutually_exclusive():
    """Cannot specify both iam_role and access_key credentials."""
    with pytest.raises(TypeError):
        CopyCommand(
            table,
            data_location='s3://bucket/data/',
            iam_role='default',
            access_key_id='AKIAIOSFODNN7EXAMPLE',
            secret_access_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        )
