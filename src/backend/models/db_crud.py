"""This modules contains all the CRUD actions needed to manipulate data
    on the db
"""

from fastapi import HTTPException, status
from typing import Dict, List
from sqlalchemy.orm import Session


QUERY_EXCEPTION = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="No results found"
)

DB_EXCEPTION = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="encountered some issues while processing request",
)


def get_all(session: Session, table):
    """Get all data from a table in database

    @session: the request session object
    @table: the db table to query
    """

    try:
        data = session.query(table).all()

    except Exception as err:
        print(f"err at get_all => {err}")
        raise DB_EXCEPTION

    return data


def get_by(session: Session, table, **kwargs):
    """Get specific data from a table in db based on **kwargs specified

    @session: the request session object
    @table: the table to query
    @**kwargs: the filter based criteria
    """

    try:
        data = session.query(table).filter_by(**kwargs).all()

    except Exception as err:
        print(f"err at get_by => {err}")
        raise DB_EXCEPTION

    return data


def get_specific_record(session: Session, table, **kwargs):
    """gets a specific record from the table

    parameters:
        @session: The db session
        @table: the database table to query
        @column: the specific column
    """
    try:
        record = session.query(table).filter_by(**kwargs).first()

    except Exception as err:
        print(f"err at get_spec => {err}")
        raise DB_EXCEPTION

    return record


def save(session: Session, db_table, record):
    """saves a record to a db table

    @session: the request session object
    @table: the table to query
    @record: the data to save to table
    """

    data = db_table(**record)
    try:
        session.add(data)
        session.commit()
        session.refresh(data)

    except Exception as err:
        print(f"error in save => {err}")
        # send yourself a mail here
        raise DB_EXCEPTION

    return data


def record_in_lifo(session: Session, db_table, column, **kwargs):
    """returns all record using last in first out

    @session: the request session object
    @db_table: the table to query
    @column: The db column to sort
    @kwargs: the argument filter
    """

    try:
        record = session.query(db_table).filter_by(**kwargs).order_by(column.desc())

    except Exception as err:
        raise DB_EXCEPTION

    return record


def all_record_in_lifo(session: Session, db_table, column):
    """returnss all records in lifo"""

    try:
        records = session.query(db_table).order_by(column.desc())

    except Exception as err:
        raise DB_EXCEPTION

    return records


def filter_record_in_lifo(session: Session, db_table, column, **kwargs):
    """filter record in lifo"""

    try:
        records = session.query(db_table).filter_by(**kwargs).order_by(column.desc())

    except Exception as err:
        raise DB_EXCEPTION

    return records


def delete(session: Session, db_table, **kwargs):
    """Deletes a record from the db table that matches the column id

    @col_id: the column ID in the table to delete, must be unique
    @session: the request session object
    @db_table: the database table to query
    """

    try:
        resp = session.query(db_table).filter_by(**kwargs).first()
    # session.delete(resp)
    # session.commit()

    except Exception as err:
        # send a mail with the exception message
        print(f"err at delete => {err}")
        raise DB_EXCEPTION

    if not resp:
        raise QUERY_EXCEPTION

    try:
        session.delete(resp)
        session.commit()

    except Exception as err:
        raise DB_EXCEPTION
