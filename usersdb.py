from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, LargeBinary, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.context import CryptContext
from schemas import User, UserDB, UserAlreadyExistsError, IncorrectPasswordError, UserNotFoundError
from fastapi import UploadFile
from typing import List
import io
import zipfile


crypt_context = CryptContext(schemes=["bcrypt"])
engine = create_engine("sqlite:///InstaShare.db", echo=True)
Base = declarative_base()

# Mapping User
class UsersTable(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    fullname = Column(String)
    email = Column(String)
    disabled = Column(Boolean)
    password = Column(String)
    files = relationship("FilesTable",
                         back_populates="user")
    zipfiles = relationship("ZipFilesTable",
                            back_populates="user")


# Mapping File
class FilesTable(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    content = Column(String)
    size = Column(Integer)
    user = relationship("UsersTable", back_populates="files")


class ZipFilesTable(Base):
    __tablename__ = "zipfiles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    data = Column(LargeBinary)
    user = relationship("UsersTable", back_populates="zipfiles")


Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)


# -----------------------------------Users-----------------------------------
# Add a user
def add_user(user: UserDB):
    result = session.query(UsersTable).filter(UsersTable.username == user.username).first()
    if result:
        raise UserAlreadyExistsError()
    session.add(UsersTable(username=user.username,
                           fullname=user.fullname,
                           email=user.email,
                           disabled=user.disabled,
                           password=crypt_context.hash(user.password)))
    session.commit()


# Get a user
# Get user
def get_auth_user(username: str, password: str):
    result = session.query(UsersTable).filter(UsersTable.username==username).first()
    if not result:
        raise UserNotFoundError()
    if not crypt_context.verify(password, result.password):
        raise IncorrectPasswordError()
    return User(username=result.username,
                fullname=result.fullname,
                email=result.email,
                disabled=result.disabled)


# Get auth user
def get_user(username: str):
    result = session.query(UsersTable).filter(UsersTable.username==username).first()
    return User(username=result.username,
                fullname=result.fullname,
                email=result.email,
                disabled=result.disabled)


# Get all users
def get_users():
    result = session.query(UsersTable).all()
    return [UserDB(username=user.username,
                   fullname=user.fullname,
                   email=user.email,
                   disabled=user.disabled,
                   password=user.password) for user in result]


# -----------------------------------Files-----------------------------------
def get_user_id(username: str):
    return session.query(UsersTable).filter(UsersTable.username==username).first().id


# Add files (current user)
def add_files(files: List[UploadFile], user: User):
    user_id = get_user_id(user.username)
    for file in files:
        file_bytes = io.BytesIO()
        with zipfile.ZipFile(file_bytes, 'w', zipfile.ZIP_DEFLATED, False) as zf:
            zf.writestr(file.filename, file.file.read())
        session.add(ZipFilesTable(userid=user_id,
                                  filename=file.filename.split(".")[0] + ".zip",
                                  data=file_bytes.getvalue()))
        file.file.seek(0)
        session.add(FilesTable(userid=user_id,
                               filename=file.filename,
                               content=file.file.read(),
                               size=file.file.tell()))
    session.commit()


# Get files (current user)
def get_files(user: User):
    user_id = get_user_id(user.username)
    result = session.query(FilesTable).join(UsersTable).filter(FilesTable.userid==user_id).all()
    return [{"id": file.id,
             "filename": file.filename,
             "size": str(file.size)+" bytes"} for file in result]


# Get all files
def get_all_files():
    result = session.query(FilesTable).all()
    return [{"id": file.id,
             "filename": file.filename,
             "size": str(file.size)+" bytes"} for file in result]


def get_all_zipfiles():
    result = session.query(ZipFilesTable).all()
    return [{"id": file.id,
             "filename": file.filename,
             "data": str(file.data)} for file in result]


def get_zipfile(id: int, user: User):
    user_id = get_user_id(user.username)
    result = session.query(ZipFilesTable).join(UsersTable).filter(and_(ZipFilesTable.userid == user_id,
                                                                       ZipFilesTable.id == id)).first()
    if not result:
        raise FileNotFoundError
    return result.filename, result.data


def modify_filename(id: int, new_filename: str, user: User):
    user_id = get_user_id(user.username)
    validation = session.query(FilesTable).filter(and_(FilesTable.userid == user_id,
                                                       FilesTable.id == id)).first()
    if not validation:
        raise FileNotFoundError
    # Modifying the txt
    session.query(FilesTable).filter(and_(FilesTable.userid == user_id,
                                          FilesTable.id == id)).update({FilesTable.filename: new_filename+".txt"},
                                                                                        synchronize_session=False)
    # Modifying the zip
    old_data = session.query(ZipFilesTable).filter(and_(ZipFilesTable.userid == user_id,
                                                        ZipFilesTable.id == id)).first().data
    bytes = io.BytesIO(old_data)
    with zipfile.ZipFile(bytes, "r") as zf:
        file_content = zf.read(zf.namelist()[0])
    bytes = io.BytesIO()
    with zipfile.ZipFile(bytes, 'w', zipfile.ZIP_DEFLATED, False) as zf:
        zf.writestr(new_filename+".txt", file_content)
    session.query(ZipFilesTable).filter(and_(ZipFilesTable.userid == user_id,
                                             ZipFilesTable.id == id)).update({ZipFilesTable.filename: new_filename.split(".")[0] + ".zip",
                                                                              ZipFilesTable.data: bytes.getvalue()}, synchronize_session=False)
    session.commit()