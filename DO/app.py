# -*- coding: utf-8 -*-
from functools import wraps
import json
import logging
import traceback
import time
from base64 import b64encode as encode_url
from flask import Flask, Response, session, abort, jsonify, g, request
from flask_restful import Resource, Api
from werkzeug.local import LocalProxy
import requests
from flask_cache import Cache
from flask_cors import CORS
from db_handler_High import High as Database
from Initdb import Test_editable
import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from custom_errors import CustomError

with open("DO/GenericConfigFile.json", "r") as conf:
    config = json.load(conf)


def get_config():
    conf = requests.get("http://127.0.0.1/config").text
    config = json.load(conf)
    return config


# config = get_config()  # Uncomment to fetch config from localhost.

# Private key
with open("operator_private_key.pem", "rb") as key_file:
    operator_rsa_private = serialization.load_pem_private_key(key_file.read(), None, default_backend())
# operator_rsa_private = load_pem_x509_certificate(key_file.read(), default_backend())

# Public key
with open("operator_public_key.pem", "rb") as key_file:
    operator_rsa_public = serialization.load_pem_public_key(key_file.read(), default_backend())
# operator_rsa_public = load_pem_x509_certificate(key_file.read(), default_backend())

virheet = {
    'MethodNotAllowed': {
        'msg': "You probably POSTed something to GET end point or GET something from POST endpoint.",
        'status': 405,
    },
    "NotFound": {
        'msg': "API endpoint not found.",
        'status': 404,
    },
    "BadRequest": {
        'msg': "Missing Content-Type, check your parameters.",
        'status': 400,
    },
    "NotImplemented": {
        'msg': "The method, endpoint or service you tried to use is not implemented yet.",
        'status': 501,
    },
}

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers='*')
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
debug_log_format = (
    '-' * 80 + '\n' +
    '%(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n' +
    '%(message)s\n' +
    '-' * 80
)
logConsoleHandle = logging.StreamHandler()
# fileHandler = logging.FileHandler("DO-log_"+str(time.time())+".log")
# fileHandler.setFormatter(logging.Formatter(debug_log_format))
logConsoleHandle.setFormatter(logging.Formatter(debug_log_format))
app.logger.addHandler(logConsoleHandle)
# app.logger.addHandler(fileHandler)
# app.logger.setLevel(logging.DEBUG)
app.secret_key = 'Nants ingonyama bagithi baba, Sithi uhhmm ingonyama, Ingonyama'
api = Api(app, errors=virheet, catch_all_404s=True)
# db = db_handler.High()
# tests = db_handler.Test_editable(db)
logger = app.logger
logger.setLevel(logging.DEBUG)
info = logger.info
error = logger.error
debug = logger.debug
warning = logger.warning
# tests = db_handler.Test_editable(db)
# api_path = "/api/v1.0/"
api_path = "/"
api_path_ui = api_path + "ui/"


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = Database(logger)
    return db


db = LocalProxy(get_db)


@app.before_request
def db_opener():
    db = LocalProxy(get_db)
    info("START OF REQUEST{}".format("#" * 90))


@app.teardown_request
def db_closer(exception):
    info("END OF REQUEST{}".format("#" * 90))
    db.session.commit()
    db.session.close()


def error_handler(e, classname):
    log = logging.getLogger("DB_Handler")
    log.exception(e)
    msg = "class calling error_handler {} got {} ---- {}".format(classname, traceback.format_exc(), repr(e))
    log.error(msg)
    return msg


def response(Object):
    '''
    Takes in dictionary or string, returns dictionary.
    '''
    t = time.time()
    debug("We got object:{}\nContaining: {}".format(type(Object), Object))
    try:
        if isinstance(Object, dict):
            js = jsonify(Object)
            debug("Creating response JSON took: {}".format(time.time() - t))
            return js
        if isinstance(Object, str):
            js = jsonify(json.loads(Object))
            debug("Creating response JSON took: {}".format(time.time() - t))
            return js
        if isinstance(Object, unicode):
            js = jsonify(json.loads(Object.decode()))
            debug("Creating response JSON took: {}".format(time.time() - t))
            return js
        else:
            debug("We are being misused, this is a lucky and desperate guess.")
            debug("Creating response JSON took: {}".format(time.time() - t))
            return jsonify(Object)
    except Exception as e:
        raise CustomError(description="Crash has occurred in response method of app.py with following error: {}".format(
            error_handler(e, "app.py response(Object)")), code=500)


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    #    js = json.dumps({"username": "admin", "password": "Hello"})
    #    db.register_userAccount(js)
    # js = json.dumps({"email":"aleksi.ajp@gmail.com", "firstName":"Aleksi", "lastName":"Palomaki", "gender":"male"})
    # db.add_user(js)
    #    db.modify_userAccount(json.dumps({"id":1, "password": "Hello"}))

    info("Checking username {}".format(username))
    user = db.get_userAccount_by_username(username)
    if user is None:
        app.logger.debug("Username not found.")
        return False
    correct = db.verify_pw(username, password)
    app.logger.debug("The username comparison of {} and {} resulted: {}"
                     .format(username, user.username, username == user.username))
    verified = username == user.username and correct
    if verified:
        session["username"] = username
        info("Correct credentials. Session username is now {}.".format(session["username"]))
        return verified
    warning("Invalid credentials.")
    return False


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


# @cache.cached(timeout=800)
def requires_auth(f):
    t = time.time()

    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    debug("Authentication took: {}s".format(time.time() - t))
    return decorated


def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


def get_public_key():
    return operator_rsa_public


def verify_rpt(encoded_rpt):
    encoded_rpt = encoded_rpt["rpt"]
    # testing = db.generate_rpt("http://test.fi/data/efghri123")
    # debug(testing)
    # encoded_rpt = testing
    info("Verifying RPT:" + encoded_rpt)
    try:
        decoded = jwt.decode(encoded_rpt, get_public_key(), algorithms=['RS256'])
        info("RPT decoded successfully.")
        try:
            check = db.get_resourceset_by_rs_id(encode_url(decoded["rs_id"]))
            info("RS_ID exists in our DB")
            debug("ResourceSet: \n {}".format(check))
        except Exception as e:
            info("RS_ID doesn't exist in our DB")
            pass
        debug("RPT: {}".format(decoded))

        return {"status": True}  # TODO: document
    except Exception as e:
        debug("Verifying of RPT failed with: {}".format(error_handler(e, "app.py verify_rpt(encoded_rpt)")))
        return {"status": False}


class RunningTest(Resource):
    def get(self):
        info("Test endpoint running fine.")
        info("This logger is {}".format(db))
        return "And we are online!"


class UserInformation(Resource):
    @requires_auth
    @cache.cached(timeout=800)
    def get(self):
        t = time.time()
        try:
            info("Fetching userInformation.")
            filtering = request.args.get("select")
            if filtering is not None:
                filtering = filtering.split(",")
                username = session["username"]
                resp = response(db.userInformation(username, filtering))
                debug("UserInformation took: {}s".format(time.time() - t))
                return resp
            raise CustomError(
                "An Error occurred in UserInformation."
                " Please check you typed the fields correctly and provided 'select?' query string.", code=400)
        except Exception as e:
            raise CustomError("An Error occurred in UserInformation."
                              " Error: {}".format(error_handler(e, self.__class__.__name__)),code=500)


class MyServices(Resource):
    @requires_auth
    def get(self):
        t = time.time()
        info("Fetching MyServices.")
        try:
            current = int(request.args.get("current"))
            count = current + int(request.args.get("count"))
            categories = request.args.get("categories").split(",")
            debug("Filering based on: {}, {}, {}".format(current, count, categories))
            resp = response(db.myServices(current, count, categories, session["username"]))
            debug("MyServices took: {}s".format(time.time() - t))
            return resp
        except Exception as e:
            error(error_handler(e, self.__class__.__name__))
            raise CustomError("An Error occurred, please check you provided required query fields."
                              " Error: {}".format(error_handler(e, self.__class__.__name__)), code=400)


class MyServices_Number(Resource):
    @requires_auth
    def get(self):
        try:
            status = request.args.get("status")
            if status.title() in ["All", "Disabled", "Active"]:
                return response(db.myServices_numberOfServices(status.title(), session["username"]))
        except Exception as e:
            raise CustomError(
                "An Error occurred, please check you typed the fields correctly and all required parameters."
                " Error: {}".format(error_handler(e, self.__class__.__name__)), code=400)


class Services(Resource):
    @requires_auth
    def get(self):
        t = time.time()
        info("Fetching Services.")
        try:
            current = int(request.args.get("current"))
            count = current + int(request.args.get("count"))
            categories = request.args.get("categories").split(",")
            labels = request.args.get("labels").split(",")
            debug("Filering based on: {}, {}, {}, {}".format(current, count, categories, labels))
            username = session["username"]
            resp = response(db.ui_Services(categories, labels, current, count, username))
            debug("Services took: {}s".format(time.time() - t))
            return resp
        except Exception as e:
            error(error_handler(e, self.__class__.__name__))
            raise CustomError(
                description="Services endpoint in app.py encountered an error."
                            " Make sure you supplied current, count, categories and labels parameters in query string."
                            " Error: {}".format(error_handler(e, self.__class__.__name__)), code=500)


class Service(Resource):
    @requires_auth
    def get(self, ide):
        t = time.time()
        info("Fetching a Service.")
        try:
            resp = response(db.ui_Services_id(ide, session["username"]))
            debug("Service took: {}s".format(time.time() - t))
            return resp
        except CustomError as e:
            raise e
        except Exception as e:
            error("Error occured: {}".format(error_handler(e, self.__class__.__name__)))
            raise CustomError(
                "An Error occurred, please check you typed the fields correctly and all required parameters. Error: {}".format(
                    error_handler(e, self.__class__.__name__)), code=400)


class Location_and_Nationality(Resource):
    def get(self, table_name):
        try:
            info("Fetching " + table_name)
            return response(db.ui_Locations_and_Nationalities(table_name))
        except CustomError as e:
            raise e
        except Exception as e:
            raise CustomError(description="Error occurred: {}".format(error_handler(e, self.__class__.__name__)))


class Location_and_Nationality_id(Resource):
    def get(self, table_name, ide):
        try:
            info("Fetching {} with id {}".format(table_name, ide))
            return response(db.ui_Locations_and_Nationalities_id(table_name, ide))
        except CustomError as e:
            raise e
        except Exception as e:
            raise CustomError(description="Error occurred: {}".format(error_handler(e, self.__class__.__name__)))


class Login(Resource):  # TODO: Move most of the logic to db_handler
    @requires_auth
    def post(self):
        try:
            info("Entered Login class post() function.")
            info("Will now try to authenticate with the service provided.")
            debug("We got data: {}".format(request.data))
            credentials = json.loads(request.data)
            service_id_none_check = credentials.get("service_id", None)
            if service_id_none_check is not None:  # Ensuring service_id is given and then turn it to int
                # Future notes, if and when we want to recognise services with uuid
                # Its easier to make up method to fetch id based on uuid and use it
                # here. Having int id's internally allows easy ordering of results.
                try:
                    service_id = int(service_id_none_check)
                except Exception as e:
                    raise CustomError(description="service_id not int."
                                      .format(error_handler(e, self.__class__.__name__)), code=400)
                debug("service_id = {}".format(service_id))
            else:
                error("No service_id provided, aborting.")
                raise CustomError(description="No service_id provided, aborting.", code=400)

            def get_service_address(service_id):
                service = db.get_service(service_id)
                return "http://{}:{}/".format(service.ip_address, service.port_api)

            service_url = get_service_address(service_id)
            debug("Got service_url: {}".format(service_url))
            credentials.pop("service_id", None)
            try:
                req = requests.post(service_url + "api/v0.1/auth", json=credentials, timeout=15).text
            except Exception as e:
                raise CustomError(description="Connecting to service failed: {}"
                                  .format(error_handler(e, self.__class__.__name__)),
                                  code=503)
            debug("We got reply: {}".format(req))
            ext_id_json = json.loads(req)  # fetch ext_id
            ext_id = ext_id_json.get("ext_id", None)
            if ext_id is None:
                error("No ext_id provided, aborting.")
                raise CustomError(description="No ext_id provided, probably incorrect credentials. Aborting.", code=403)
            userAccount = db.get_userAccount_by_username(session["username"])
            table = {"services_id": service_id,
                     "userAccounts_id": userAccount.id,
                     "ext_id": ext_id}
            db.add_ext_id(json.dumps(table))
            info("Fetching SCT from service {}".format(service_id))
            contract = requests.get(service_url + "api/v0.1/contract",
                                    headers={"Authorization": "bearer " + ext_id})
            debug("Got Following SCT:\n{}".format(contract.text))

            if db.SCT_correctly_formatted(contract.text) is False:
                error("SCT was not correctly formatted.")
                raise CustomError(description="SCT was not correctly formatted.", code=400)
            if contract.__bool__():
                info("Got contract successfully!")
                return response(contract.text)

            error("We didn't receive OK from service.")
            raise CustomError(description="The service responded something besides"
                                          " OK when requesting SCT, Output in logs "
                                          "and included here: {}".format(contract.text), code=520)
        except CustomError as e:
            raise e
        except Exception as e:
            raise CustomError(description="Error occurred: {}".format(error_handler(e, self.__class__.__name__)))


class VerifyRPT(Resource):
    def post(self):
        try:
            debug("Entered VerifyRPT function with value:\n " + request.data)
            return verify_rpt(json.loads(request.data))
        except CustomError as e:
            raise e
        except Exception as e:
            raise CustomError(description="Error occurred: {}".format(error_handler(e, self.__class__.__name__)))


class UiSCT(Resource):
    @requires_auth
    def post(self):
        try:
            info(request.data)
            contract = json.loads(request.data)
            debug(type(contract))
            debug(contract["intendet_use"])
            if isinstance(contract["intendet_use"], list):
                contract["intendet_use"] = ",".join(contract["intendet_use"])

            if db.ui_SCT_correctly_formatted(contract) is False:
                CustomError(description="Validating of SCT format failed. Check SCT format.", code=400)
            if db.signing_function(contract) is False:
                CustomError(description="Signing of SCT failed.", code=400)
            db.make_contract(session["username"], contract)
            return {"status": "success"}
        except CustomError as e:
            raise e
        except Exception as e:
            raise CustomError(description="Error occurred: {}".format(error_handler(e, self.__class__.__name__)))


class ResourceSets(Resource):
    @requires_auth
    def get(self):
        abort(501)
        return response(db.src_ResourceSets())

    @requires_auth
    def post(self):
        '''
        {
         "service_id": id,
         "categories": ["Food", "Fitness"]
        }
        '''
        try:
            js = request.json
            info("Adding new Resource set.")
            debug(request.json)
            # ext_id = request.headers.get("Authorization")
            # if ext_id is None:
            #    abort(400)
            # ext_id = ext_id.split(" ")[-1]
            js["username"] = session["username"]
            return response(db.CreateResourceSet(js))
        except CustomError as e:
            raise e
        except Exception as e:
            raise CustomError(description="Error occurred: {}".format(error_handler(e, self.__class__.__name__)))


class ResourceSet2(Resource):
    @requires_auth
    def get(self):
        abort(501)
        return response(db.src_ResourceSets())

    @requires_auth
    def post(self):
        '''
        {
         "service_id": id,
         "categories": ["Food", "Fitness"]
        }
        '''
        try:
            js = request.json
            info("Adding new Resource set.")
            debug(request.json)
            # ext_id = request.headers.get("Authorization")
            # if ext_id is None:
            #    abort(400)
            # ext_id = ext_id.split(" ")[-1]
            js["username"] = session["username"]
            return response(db.CreateResourceSet(js))
        except CustomError as e:
            raise e
        except Exception as e:
            raise CustomError(description="Error occurred: {}".format(error_handler(e, self.__class__.__name__)))


class ConsentView(Resource):
    @requires_auth
    def post(self):
        t = time.time()
        '''
         {
         "sink_id":"",
         "source_id":"",
         "consent_id":""
         }
        '''
        try:
            data = request.json
            sink_id = data["sink_id"]
            source_id = data["source_id"]
            consent_id = data.get("consent_id")
            resp = response(db.ui_ConsentView(session["username"], sink_id, source_id, consent_id))
            debug("ConsentView took: {}s".format(time.time() - t))
            return resp
        except CustomError as e:
            raise e
        except Exception as e:
            raise CustomError(description="Error occurred: {}".format(error_handler(e, self.__class__.__name__)))


class ResourceSet(Resource):
    def get(self, ide):
        return response(db.src_ResourceSet(ide))


# class Register_ResourceSet(Resource):
#     @requires_auth
#     def get(self):
#         categories = request.args.get("categories")
#         service_id = request.args.get("service_id")
#         username = session["username"]
#         js = {"categories": categories,
#               "service_id": service_id,
#               "username": username}
#         db.CreateResourceSet(js)

class GiveConsent(Resource):
    @requires_auth
    def post(self):
        try:
            js = request.json
            js["rs_id"] = js["rs_id"]["rs_id"]  # TODO: This is a fix for UI problem
            db.create_consent_receipt(js, session["username"])
            return response({"status": "200", "success": True})
        except CustomError as e:
            raise e
        except Exception as e:
            raise CustomError(description="Error occurred: {}".format(error_handler(e, self.__class__.__name__)))


class Licenses(Resource):
    @requires_auth
    def get(self):
        try:
            return response(db.parse_dict_list_to_json([x.tojson for x in db.get_licensetypes()]))
        except CustomError as e:
            raise e
        except Exception as e:
            raise CustomError(description="Something went wrong in fetching licenses list with error: {}"
                              .format(error_handler(e, self.__class__.__name__)))


class ServDB(Resource):
    @requires_auth
    def get(self):
        try:
            return response(db.parse_dict_list_to_json([x.tojson for x in db.get_services()]))
        except CustomError as e:
            raise e
        except Exception as e:
            raise CustomError(description="Something went wrong in fetching licenses list with error: {}"
                              .format(error_handler(e, self.__class__.__name__)))


class Config(Resource):
    @requires_auth
    def get(self):
        try:
            return response(config)
        except Exception as e:
            raise CustomError(description="Something went wrong in fetching licenses list with error: {}".format(
                error_handler(e, self.__class__.__name__)))


class Active_Licenses(Resource):
    @requires_auth
    def get(self, id):
        try:
            resp = db.get_active_licenses(id)
            return response({"active_licenses": resp})
        except CustomError as e:
            raise e
        except Exception as e:
            raise CustomError(description="Error occurred: {}".format(error_handler(e, self.__class__.__name__)))


class Active_Categories(Resource):
    @requires_auth
    def get(self, id):
        try:
            resp = db.get_active_categories(id)
            return response({"active_categories": resp})
        except CustomError as e:
            raise e
        except Exception as e:
            raise CustomError(description="Error occurred: {}".format(error_handler(e, self.__class__.__name__)))


class Disable_Consent(Resource):
    @requires_auth
    def get(self, id):
        try:
            current_link = json.loads(db.get_consentreceiptslink(id).tojson)
            debug("[{}]Deleting ConsentReceiptLink:\n {}".format(time.time(), current_link))
            resp = db.delete_consentreceiptslink(id)
            return "Removed."
        except CustomError as e:
            raise e
        except Exception as e:
            raise CustomError(description="Error occurred: {}".format(error_handler(e, self.__class__.__name__)))


class ResetDB(Resource):
    # @requires_auth
    def get(self):
        try:
            db.reset_database()
        except Exception as e:
            pass
        global db
        setattr(g, '_database', None)
        db = LocalProxy(get_db)
        tests = Test_editable(db)
        with open("DO/GenericConfigFile.json", "r") as conf:
            global config
            config = json.load(conf)
            # config = get_config()

        return "DataBase has been RESETED and INITIALIZED!"


class TestConsentStatus(Resource):
    def get(self):
        js = {"Result": "First get current status which is '{}' then set status to paused. Operation was a '{}'."
                        " Checking that now its '{}' and we change it back to active after this."
                        " Operation was '{}' and status is now '{}'.".format(db.get_consent_status(1, session["username"]),
                                                                             db.set_consent_status(1, "paused",
                                                                                                   session["username"]),
                                                                             db.get_consent_status(1, session["username"]),
                                                                             db.set_consent_status(1, "active",
                                                                                                   session["username"]),
                                                                             db.get_consent_status(1, session["username"]))
              }
        return response(js)


class SetConsentStatus(Resource):
    @requires_auth
    def put(self):
        '''
        {
        "consent_id": consentID,
        "status":     "active"
        }
        '''
        js = json.loads(request.data)
        return response({"status": db.set_consent_status(js["consent_id"], js["status"], session["username"])})


api.add_resource(RunningTest, '/')
api.add_resource(UserInformation, api_path_ui + 'userInformation')                          # Documented in swagger.yml
api.add_resource(MyServices, api_path_ui + 'myServices')                                    # Documented in swagger.yml
api.add_resource(MyServices_Number, api_path_ui + 'myServices/numberOfServices')            # Documented in swagger.yml
api.add_resource(Services, api_path_ui + 'services')                                        # Documented in swagger.yml
api.add_resource(Service, api_path_ui + 'services/<ide>')                                   # Documented in swagger.yml

api.add_resource(Location_and_Nationality, api_path_ui + 'location/<table_name>',           # UNUSED
                 api_path_ui + 'language/<table_name>')
api.add_resource(Location_and_Nationality_id, api_path_ui + 'location/<table_name>/<ide>',  # UNUSED
                 api_path_ui + 'language/<table_name>/<ide>')

api.add_resource(Login, api_path_ui + "foreign_login")                                      # Documented in swagger.yml
api.add_resource(VerifyRPT, api_path + "verify_rpt")                                        # Documented in swagger.yml
api.add_resource(UiSCT, api_path_ui + "accept_contract")                                    # Documented in swagger.yml
api.add_resource(GiveConsent, api_path_ui + "give_consent")                                 # Documented in swagger.yml
api.add_resource(ResourceSets, api_path + "protection/resourceSets")                        # Documented in swagger.yml

api.add_resource(ResourceSet, api_path + "protection/resourceSets/<ide>")                   # UNUSED
api.add_resource(Licenses, api_path + "db/licenses")                                        # UNUSED
api.add_resource(ServDB, api_path + "db/services")                                          # Documented in swagger.yml

api.add_resource(ConsentView, api_path + "ui/ConsentView")                                  # Documented in swagger.yml

api.add_resource(Active_Licenses, api_path + "ui/active_licenses/<id>")                     # TODO: Document # UNUSED
api.add_resource(Active_Categories, api_path + "ui/active_categories/<id>")                 # TODO: Document # UNUSED

api.add_resource(Disable_Consent, api_path + "ui/disable_consent/<id>")                     # Documented in swagger.yml
api.add_resource(Config, api_path + "config")                                               # Documented in swagger.yml
api.add_resource(ResetDB, api_path + "RESET")                                               # Documented in swagger.yml
api.add_resource(TestConsentStatus, api_path + "CTest")                                     # TODO: Document, Testing
api.add_resource(SetConsentStatus, api_path + "db/ConsentStatus")                           # TODO: Document # UNUSED

if __name__ == '__main__':
    app.run(debug=False, port=8080, host="0.0.0.0", threaded=False)

'''
TODO:
Service contract starting from service
Make rpt invalid if consent is revoked/paused. (We check for invalid/missing rpt but fail silently incase or problems)

'''
