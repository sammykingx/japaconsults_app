from models.db_engine import engine
import sqlalchemy


def recon_2_db(dbapi_connection, connection_record):
    print(dbapi_connection, connection_record)
    print("recon avoiy to work")
    if dbapi_connection.closed:
        try:
            new_connection = dbapi_connection.connect()
            connection_record.connection = new_connection

        except Exception as err:
            print(f"Reconnection failed: {err}")


sqlalchemy.event.listen(engine, "handle_error", handle_db_disconnection)
