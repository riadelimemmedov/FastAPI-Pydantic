FastAPI and Pydantic
    ## Command List
    - alembic init migrations => Initialize Alembic
    - alembic revision --autogenerate -m  => "To create a new migrations file for migrate to model to Postgress database"
    - alembic upgrade head => To apply the migrations and update your database schema
    - alembic upgrade <revision_id> && alembic upgrade head =>  Switch to forward or next migrations number in alembic you should do it
    - alembic downgrade <revision_id> && alembic downgrade base => Switch to back or earlier migrations number in alembic you should do it