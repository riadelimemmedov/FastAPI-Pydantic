#

# ?FastApi
from fastapi import FastAPI, Request
from pydantic import BaseModel, EmailStr, SecretStr, validator


# ?Third Party packages for FastApi
import databases  # Databases gives you simple asyncio support for a range of databases.
import sqlalchemy  # A powerful and popular Object-Relational Mapping (ORM) library that supports multiple database backends, including PostgreSQL, MySQL, SQLite, and more.
from sqlalchemy import select
from decouple import config
from email_validator import validate_email as validate_user_email, EmailNotValidError

from passlib.context import CryptContext

# ?Pyhon modules and Functions
import enum
from datetime import datetime
from typing import Optional


# Postgress Settings
POSTGRES_HOST = config("POSTGRES_HOST")
POSTGRES_DB = config("POSTGRES_DB")
POSTGRES_USER = config("POSTGRES_USER")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD")
POSTGRES_PORT = config("POSTGRES_PORT", 5432)


# Database Url
DATABASE_URL = "postgresql://{}:{}@{}:{}/{}".format(
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB
)
database = databases.Database(DATABASE_URL)


# Sqlalchemy and Tables
metadata = sqlalchemy.MetaData()

#############################################################################################################################################################################

# *Users
users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String(120), unique=True),
    sqlalchemy.Column("password", sqlalchemy.String(255)),
    sqlalchemy.Column("full_name", sqlalchemy.String(200)),
    sqlalchemy.Column("phone", sqlalchemy.String(13)),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
    ),
    sqlalchemy.Column(
        "last_modified_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
)


# ColorEnum
class ColorEnum(enum.Enum):
    pink = "pink"
    black = "black"
    white = "white"
    yellow = "yellow"


# SizeEnum
class SizeEnum(enum.Enum):
    xs = "xs"
    s = "s"
    m = "m"
    l = "l"
    xl = "xl"
    xxl = "xxl"


# *Clothes
clothes = sqlalchemy.Table(
    "clothes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(120)),
    sqlalchemy.Column("color", sqlalchemy.Enum(ColorEnum), nullable=False),
    sqlalchemy.Column("size", sqlalchemy.Enum(SizeEnum), nullable=False),
    sqlalchemy.Column("photo_url", sqlalchemy.String(255)),
    sqlalchemy.Column(
        "created_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
    ),
    sqlalchemy.Column(
        "last_modified_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
)


# Create FastApi Object,Passlib and Define Api Endpoint
app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

########################################################################################################################################################


# EmailField
class EmailField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_email

    @classmethod
    def validate_email(cls, email):
        try:
            validate_user_email(email)
            return email
        except EmailNotValidError:
            raise ValueError("Email is not valid")


# BaseUser
class BaseUser(BaseModel):
    email: EmailField
    full_name: Optional[str]

    @validator("full_name")
    def validate_full_name(cls, full_name):
        try:
            first_name, last_name = full_name.split()
            return full_name
        except Exception:
            raise ValueError("You should provide at least first_name and last_name")


# ?UserSignIn
class UserSignIn(BaseUser):
    password: str


# ?UserSignOut
class UserSignOut(BaseUser):
    phone: Optional[str]
    created_at: datetime
    last_modified_at: datetime


##############################################################################################################################################################


#!startup
# When open localhost,work this view automatically and close database connection
@app.on_event("startup")
async def startup():
    print("Connect database successfully")
    await database.connect()


#!shutdown
# When closed port,work this view automatically and close database connection
@app.on_event("shutdown")
async def shutdown():
    print("Disconnect database successfully")
    await database.disconnect()


#!create_user
@app.post("/register/user/", response_model=UserSignOut)
async def create_user(user: UserSignIn):
    user_values = user.dict()
    # user_values["password"] = user.password.get_secret_value()
    # Or
    user_values["password"] = pwd_context.hash(user.password)

    qs = users.insert().values(**user_values)
    created_user_id = await database.execute(qs)

    created_user = await database.fetch_one(
        users.select().where(users.c.id == created_user_id)
    )
    return created_user

    # return {"created_user_id": created_user_id}
