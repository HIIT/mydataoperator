# -*- coding: utf-8 -*-
__author__ = 'Aleksi Palomäki'
from json import loads, load
from inspect import currentframe
import logging
import requests
import traceback
from sqlalchemy import create_engine
from base import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from custom_errors import CustomError


# Private key
with open("operator_private_key.pem", "rb") as key_file:
    operator_rsa_private = serialization.load_pem_private_key(key_file.read(), None, default_backend())

#    operator_rsa_private = load_pem_x509_certificate(key_file.read(), default_backend())
# Public key
with open("operator_public_key.pem", "rb") as key_file:
    operator_rsa_public = serialization.load_pem_public_key(key_file.read(), default_backend())
#    operator_rsa_public = load_pem_x509_certificate(key_file.read(), default_backend())
with open("operator_public_key.pem", "r") as key_file:
    pub_key = "".join(key_file.readlines()[1:-1]).replace("\n", "")

# from conffi import src_ip, sink_ip

LOG_LEVEL = logging.DEBUG
debug_mode = False  # TODO: REMOVE BEFORE PRODUCTION


def error_handler(e, classname):
    log = logging.getLogger("DB_Handler")
    log.exception(e)
    msg = "class calling error_handler {} got {} ---- {}".format(classname, traceback.format_exc(), repr(e))
    log.error(msg)
    return msg


def get_config():
    conf = requests.get("http://127.0.0.1/config").text
    config = load(conf)
    return config


class DB_Handler:

    '''!
    @brief DB_Handler provides basic access to SQL database.'''

    def __init__(self, logger):
        with open("DO/GenericConfigFile.json", "r") as conf:
            self.config = load(conf)
            # self.config = get_config()

        self.info = logger.info
        self.warning = logger.warning
        self.debug = logger.debug
        self.error = logger.error
        self.engine = create_engine('mysql+mysqldb://root:XmNT86Pi@127.0.0.1/dataoperator',
                                    echo=False,
                                    pool_recycle=3600,
                                    isolation_level="READ COMMITTED")  # Create SQL alchemy engine
        #  self.engine = create_engine('sqlite:///test.db', echo=False, pool_recycle=3600,connect_args={'check_same_thread':True}) # Create SQLite alchemy engine on FILE
        #  self.engine = create_engine('sqlite://', echo=False,pool_recycle=3600) # Create SQLite alchemy engine on RAM
        if debug_mode:
            Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)                   # Create all Base objects
        Session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(Session_factory)          # Create a Session

        self.session = self.Session()                           # Shortcut to Session() for .add and such

    def reset_database(self):
        self.session.commit()
        Base.metadata.drop_all(self.engine)
        self.session.commit()
        self.session.close()

    def delete_table(self, resource):
        '''!
        @brief Delete row from table that matches given value.'''
        try:
            self.session.query(resource).delete()  # Delete content of given Table
            # Commit
            self.session.commit()
        except Exception as e:
            self.error("We encountered error '{}' in function '{}' on DB_Handler class."
                       .format(repr(e), currentframe().f_code.co_name))
            # Something went wrong with transaction above so we want to rollback.
            self.session.rollback()
            self.error("Changes to the DataBase were rollback()'ed, will now raise CustomError")
            # We rise CustomError's since they are modifiable by us and since they are based on HTTPException we can
            # forward them straight to the Flask API and have its error handler do its magic.
            raise CustomError("We encountered error: {}".format(error_handler(e, self.__class__.__name__)), code=500)

    def add(self, resource):
        '''!
        @brief Add value, the value given is a resource object defined in resource.py'''
        try:
            self.debug("We entered function '{}' on DB_Handler class with parameter:\n{}"
                       .format(currentframe().f_code.co_name, resource.tojson))
            # Add resource object
            self.session.add(resource)
            # Commit changes to database
            self.session.commit()
            # Return the id given to row.
            return resource.id
        except Exception as e:
            self.error("We encountered error '{}' in function '{}' on DB_Handler class."
                       .format(repr(e), currentframe().f_code.co_name))
            # Something went wrong with transaction above so we want to rollback.
            self.session.rollback()
            self.error("Changes to the DataBase were rollback()'ed, will now raise CustomError")
            # We rise CustomError's since they are modifiable by us and since they are based on HTTPException we can
            # forward them straight to the Flask API and have its error handler do its magic.
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def get_table(self, resource):
        '''!
        @brief Return row matching query for given value in given table.'''
        try:
            query = self.session.query(resource).all()
            self.session.commit()
            return query
        except Exception as e:
            self.error("We encountered error '{}' in function '{}' on DB_Handler class."
                       .format(repr(e), currentframe().f_code.co_name))
            # Something went wrong with transaction above so we want to rollback.
            self.session.rollback()
            self.error("Changes to the DataBase were rollback()'ed, will now raise CustomError")
            # We rise CustomError's since they are modifiable by us and since they are based on HTTPException we can
            # forward them straight to the Flask API and have its error handler do its magic.
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def get_raw(self, sql):  # DEPRICIATED, we should only use sqlalchemy native stuff
        return self.engine.execute(sql)

    def modify(self, object, info):
        self.debug("Entered function '{}' in class DB_Handler with parameter:\n {}, {}"
                   .format(currentframe().f_code.co_name, info, object))
        info = loads(info)
        # Check for None
        if object is None:
            return {"Status": False, "Error": "404", "Error_long": Exception("Object not found.")}  # TODO: Redo this!
        # For each key in the dictionary we use to update values, we log and use setattr to the modified object
        # SQLAlchemy updates these changes to the Resource Object to the database.
        for key in info.keys():
            value = info[key]
            try:
                self.info("Updating '{}' in table '{}' with primary_key '{}':\n Old value: {}\n New value: {}"
                          .format(key, object.__tablename__, object.id, getattr(object, key), value))
                setattr(object, key, value)
            except Exception as e:
                # Verbose error messages are nice.
                self.error("Failed Updating '{}' in table '{}' with primary_key '{}':\n Old value: {}\n New value: {}\n"
                           "with error:{}".format(key,
                                                  object.__tablename__,
                                                  object.id,
                                                  getattr(object, key),
                                                  value,
                                                  repr(e)))
                raise CustomError("We encountered error: {}"
                                  .format(error_handler(e, self.__class__.__name__)), code=500)
        return {"status": True, "Error": None}

'''
Tasks to do:
Check the endpoints for DataSink and Source to deliver consent receipt, Docs say its in /api/v1.0/token on Sink but
Source has /api/v0.1/auth
'''
