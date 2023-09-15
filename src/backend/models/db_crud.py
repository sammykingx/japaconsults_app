"""This modules contains all the CRUD actions needed to manipulate data
    on the db
"""

from fastapi import HTTPException
from typing import Dict, List
from sqlalchemy.orm import Session


def get_all(session: Session, table):
    """Get all data from a table in database

    @session: the request session object
    @table: the db table to query
    """

    data = None
    try:
        data = session.query(table).all()

    except Exception as err:
        raise HTTPException(status_code=500, details=err)

    return data

def get_by(session: Session, table, **kwargs):
    """Get specific data from a table in db based on **kwargs specified

    @session: the request session object
    @table: the table to query
    @**kwargs: the filter based criteria
    """

    data = None
    try:
        data = session.query(table).filter_by(**kwargs).all()

    except (DataError, NoResultFound) as err:
        raise HTTPException(status_code=404, detail=err)

    return data


def save(session: Session, db_table, record):
    """saves a record to a db table

    @session: the request session object
    @table: the table to query
    @record: the data to save to table
    """

    data = db_table(**record.dict())
    try:
        session.add(data)
        session.commit()
        session.refresh(data)

    except Exception as err:
        raise HTTPException(status_code=500, detail=err)

#
#def update(session: Session, db_table, **kwargs):
#    """upates a record in db table
#
#    @session: the request session object
#    @table: the table to query
#    @record: the data to update in table
#    """
#
#    session.query(db_table).filter_by(**kwargs)
#    to be continued later
