# -*- coding: utf-8 -*-
__author__ = 'Aleksi Palomäki'

from json import loads, dumps
from uuid import uuid4 as guid
from inspect import currentframe
import logging
import time
from base64 import b64encode as encode_url
from base64 import b64decode as decode_url
import requests
from resources.Resources import Categories, ServiceDatas, LabelLinks, Summaries, ConsentReceiptsForSource, \
    ConsentReceiptsForSink, Contracts, LicenseLinks
from passlib.hash import sha256_crypt
import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from custom_errors import CustomError
from db_handler import error_handler
from db_handler_Basic import Basic

# Private key
with open("operator_private_key.pem", "rb") as key_file:
    operator_rsa_private = serialization.load_pem_private_key(key_file.read(), None, default_backend())

# operator_rsa_private = load_pem_x509_certificate(key_file.read(), default_backend())
# Public key
with open("operator_public_key.pem", "rb") as key_file:
    operator_rsa_public = serialization.load_pem_public_key(key_file.read(), default_backend())
# operator_rsa_public = load_pem_x509_certificate(key_file.read(), default_backend())
with open("operator_public_key.pem", "r") as key_file:
    pub_key = "".join(key_file.readlines()[1:-1]).replace("\n", "")

# from conffi import src_ip, sink_ip

LOG_LEVEL = logging.DEBUG
debug_mode = False  # TODO: REMOVE BEFORE PRODUCTION


class High(Basic):
    def pre_calc(self):
        '''
        For optimizing some queries we could do with for loops, we could pre-calculate them on start up.
        '''
        pass

    def get_consent_status(self, consentID, username):
        self.debug("Entered function '{}' in class High with parameter:\n {}"
                   .format(currentframe().f_code.co_name, consentID))
        userAccount_id = self.get_userAccount_by_username(username).id
        links = self.get_consentreceiptslink(consentID)
        sink_receipt = self.get_consentreceiptforsink(links.sink_receipt)
        source_receipt = self.get_consentreceiptforsource(links.source_receipt)
        if source_receipt.userAccount_id == userAccount_id:
            return self.get_status(sink_receipt.authorization_status).type
        raise CustomError(description="You do not own this consent.", code=403)

    def set_consent_status(self, consentID, status, username):  # status is type of the status
        self.debug("Entered function '{}' in class High with parameters:\n {}\n {}"
                   .format(currentframe().f_code.co_name, consentID, status))
        try:
            userAccount_id = self.get_userAccount_by_username(username).id
            status_id = self.get_status_by_type(status).id
            links = self.get_consentreceiptslink(consentID)
            sink_receipt = self.get_consentreceiptforsink(links.sink_receipt)
            if userAccount_id != sink_receipt.userAccount_id:
                return "Failure 403"
            source_receipt = self.get_consentreceiptforsource(links.source_receipt)
            sink_receipt.authorization_status = status_id
            source_receipt.authorization_status = status_id
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            self.debug("Failed to set consent status.")
            error_handler(e, "High")
        return "Success"

    def get_consent_status_by_rs_id(self, rs_id):
        try:
            rs_id = encode_url(rs_id)
            resp = self.get_status(self.session.query(ConsentReceiptsForSink).filter_by(rs_id=rs_id)
                                   .first().authorization_status).type
            return resp
        except Exception as e:
            error_handler(e, "High")
            return None

    def get_userAccount_token(self, username):
        self.debug("Entered function '{}' in class High with username {}."
                   .format(currentframe().f_code.co_name, username))
        user = self.get_userAccount_by_username(username)
        return user.accessToken

    def get_user_password(self, username):
        self.debug("Entered function '{}' in class High with username {}."
                   .format(currentframe().f_code.co_name, username))
        user = self.get_userAccount_by_username(username)
        pw = user.password
        return pw

    def verify_pw(self, username, pw):
        self.debug("Entered function '{}' in class High with username {}."
                   .format(currentframe().f_code.co_name, username))
        hashi = self.get_user_password(username)
        result = sha256_crypt.verify(pw, hashi)
        self.debug("Result of verify: {}".format(result))
        return result

    def register_userAccount(self, userAccount_info):
        self.debug("Entered function '{}' in class High with username {}."
                   .format(currentframe().f_code.co_name, userAccount_info))
        js = loads(userAccount_info)
        js["password"] = sha256_crypt.encrypt(js["password"])
        userAccount_info = dumps(js)
        try:
            self.add_userAccount(userAccount_info)
            return True
        except Exception as e:
            error_handler(e, "High")
            return False

    def filtering(self, dictionary, filter_list):
        self.debug("Entered function '{}' in class High with parameters:\n {}\n {}"
                   .format(currentframe().f_code.co_name, dictionary, filter_list))
        reply = dictionary
        for key in dictionary.keys():
            if key not in filter_list:
                reply.pop(key, None)
        return reply

    def parse_dict_list_to_json(self, dict_list):
        t = time.time()
        self.debug("Entered function '{}' in class High with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_list))
        self.info("We got dictionary list: {}".format(dict_list))

        if isinstance(dict_list[0], dict):
            lista = []
            for x in list(dict_list):
                lista.append(dumps(x))
            dict_list = lista

        dict_list_helper = []
        for x in dict_list:
            dict_list_helper.append(loads(x))
        dict_list = dict_list_helper
        self.info("New dict_list is: {}".format(dict_list))
        helper = {}
        for dictionary in dict_list:
            ide = dictionary["id"]
            helper[ide] = {}
            for key, value in dictionary.iteritems():
                if key == "id":
                    pass
                else:
                    helper[ide][key] = value
        self.debug("Parsing JSON list took: {}s".format(time.time() - t))
        return dumps(helper)

    def userInformation(self, username, filte):
        self.debug("Entered function '{}' in class High with parameters:\n {}\n {}"
                   .format(currentframe().f_code.co_name, username, filte))
        user = self.get_userAccount_by_username(username)
        user = self.get_user(user.users_id)
        filtered_info = {str(user.id): self.filtering(loads(user.tojson), filte)}
        return filtered_info

    def current_count_filtering(self, dictionary, current, count):
        self.debug("Entered function '{}' in class High with parameters:\n {}\n {}\n {}"
                   .format(currentframe().f_code.co_name, dictionary, current, count))
        keys = sorted(dictionary.keys())  # Keys are numbers, so this will be from smallest to largest
        counter = 0
        for key in keys:
            if counter < current:
                dictionary.pop(keys[counter])
            if count < counter:
                dictionary.pop(keys[counter])
            counter = counter + 1
        return dictionary

    def myServices(self, current, count, categories, username):
        self.debug("Entered function '{}' in class High with parameters:\n {}\n {} and {}\n {}"
                   .format(currentframe().f_code.co_name, categories, current, count, username))
        # TODO: This can probably be written with sqlalchemy in form of query from DB. Also needs filter with contacts.
        username_id = self.get_userAccount_by_username(username).id
        contracts = self.get_contracts_by_userAccount_id(username_id)
        reply = {}

        for con in contracts:  # Iterate trough contracts user has
            category_list = []
            service_type = self.get_servicetype(con.serviceType)  # Get if service is Sink, Source or Both
            if service_type.type == "Source":
                try:
                    links = self.get_consentreceiptlinks_by_source_contract(con.id)  # Get services connected to this one.
                except Exception as e:  # None found.
                    self.error((error_handler(e, self.__class__.__name__)))
                    links = None
                sending = {}
                receiving = {}
                if links is not None:
                    for hit in links:
                        cont = self.get_contract(hit.sink_contract_id)
                        service = self.get_service(cont.services_id)
                        service_name = service.name
                        sending[service_name] = {}
                        sending[service_name]["serviceID"] = service.id
                        sending[service_name]["img_url_logo"] = service.img_url_logo
                        sending[service_name]["description"] = {}
                        sending[service_name]["description"]["short"] = service.descriptionShort
                        sending[service_name]["consentActive"] = self.get_status(
                            self.get_consentreceiptforsink(hit.sink_receipt).authorization_status).type

                else:
                    sending = {}
            elif service_type.type == "Sink":
                try:
                    links = self.get_consentreceiptlinks_by_sink_contract(con.id)
                except Exception as e:
                    self.error(error_handler(e, self.__class__.__name__))
                    links = None
                receiving = {}
                sending = {}
                if links is not None:
                    for hit in links:
                        cont = self.get_contract(hit.source_contract_id)
                        service = self.get_service(cont.services_id)
                        service_name = service.name
                        receiving[service_name] = {}
                        receiving[service_name]["serviceID"] = service.id
                        receiving[service_name]["img_url_logo"] = service.img_url_logo
                        receiving[service_name]["description"] = {}
                        receiving[service_name]["description"]["short"] = service.descriptionShort
                        receiving[service_name]["consentActive"] = self.get_status(
                            self.get_consentreceiptforsource(hit.source_receipt).authorization_status).type
                else:
                    sending = {}

            elif service_type.type == "Both":
                links_sink = self.get_consentreceiptlinks_by_sink_contract(con.id)
                links_src = self.get_consentreceiptlinks_by_source_contract(con.id)
                receiving = {}
                sending = {}  # TODO add check for links_sink&source not None
                for hit in links_src:
                    cont = self.get_contract(hit.sink_contract_id)
                    service = self.get_service(cont.services_id)
                    sending[service.name] = {}
                    sending[service.name]["serviceID"] = service.id
                    sending[service.name]["img_url_logo"] = service.img_url_logo
                    sending[service.name]["description"] = {}
                    sending[service.name]["description"]["short"] = service.descriptionShort
                    sending[service.name]["consentActive"] = self.get_status(
                        self.get_consentreceiptforsink(hit.sink_receipt).authorization_status).type
                for hit in links_sink:
                    cont = self.get_contract(hit.source_contract_id)
                    service = self.get_service(cont.services_id)
                    receiving[service.name] = {}
                    receiving[service.name]["serviceID"] = service.id
                    receiving[service.name]["img_url_logo"] = service.img_url_logo
                    receiving[service.name]["description"] = {}
                    receiving[service.name]["description"]["short"] = service.descriptionShort
                    receiving[service.name]["consentActive"] = self.get_status(
                        self.get_consentreceiptforsource(hit.source_receipt).authorization_status).type
            else:
                self.error("We got serviceType that shouldn't exist, we support only Source, Sink and Both!")
                raise CustomError("We got serviceType that shouldn't exist,"
                                  "We support only Source, Sink and Both!"
                                  "We got {}".format(service_type.type), 500)
            service = self.get_service(con.services_id)
            contract_datatypes = self.get_contractdatatypes_by_contract_id(con.id)
            for hit in contract_datatypes:
                cate_name = self.get_category(hit.categories_id).name
                if cate_name not in category_list:
                    category_list.append(cate_name.split(".")[0])
            reply[con.services_id] = {}
            reply[con.services_id]["name"] = service.name
            reply[con.services_id]["categories"] = category_list
            reply[con.services_id]["connections"] = {}
            reply[con.services_id]["connections"]["ReceivingData"] = sending
            reply[con.services_id]["connections"]["DataShared"] = receiving
            self.debug(reply)

        templu = {
            "1": {
                "category": [
                    "sports",
                    "health"
                ],
                "connections": {
                    "ReceivingData": {
                        "Source_name": {
                            "serviceID": "1234",
                            "img_url_logo": "http://url.to.something/logo.png",
                            "description": {
                                "short": "Short and compact description"
                            },
                            "consentActive": "True"
                        }
                    },
                    "SharingData": {
                        "Sink_name": {
                            "serviceID": "1234",
                            "img_url_logo": "http://url.to.something/logo.png",
                            "description": {
                                "short": "Short and compact description"
                            },
                            "consentActive": "True"
                        }
                    }
                }
            }

        }
        self.debug("We got following keys {}".format(reply.keys()))
        # for key in dummy:
        #     cat = dummy[key]["categories"]
        #     if categories != cat:
        #         any_matches = False
        #         for item in categories:
        #             if item in cat:
        #                 any_matches = True
        #                 break
        #         if any_matches:
        #             pass
        #         else:
        #             dummy.pop(key, None)
        # Now we have all hits filtered by categories, time to filter by current and count.
        reply_filtered = self.current_count_filtering(reply, current, count)
        return reply_filtered

    def myServices_numberOfServices(self, status, username):
        self.debug("Entered function '{}' in class High with parameter:\n {}"
                   .format(currentframe().f_code.co_name, status))
        services = self.get_contracts_by_userAccount_id(self.get_userAccount_by_username(
            username).id)  # TODO: This can probably be written with sqlalchemy in form of query from DB.
        try:
            count = len(services)
        except TypeError:
            count = 0
        if status == "All":
            return {"numberOfServices": count}
        else:
            active = []
            for service in services:
                if service.statuses_id == 1:  # TODO: figure how to get active type id reliably,
                    #  how about self.get_status_by_type
                    active.append(service)
            active_num = len(active)
            if status == "Active":
                return {"numberOfServices": active_num}
            disabled_num = count - active_num
            return {"numberOfServices": disabled_num}

    def ui_Services(self, categories, labels, current, count,
                    username):  # TODO: Move functionality to grab labels/categories based on service to Basic
        total_timer = time.time()
        self.debug("Entered function '{}' in class High with parameters:\n {},\n {},\n {},\n {}"
                   .format(currentframe().f_code.co_name, categories, labels, current, count))

        t1_end = time.time()
        category_names = categories  # id's for all categories we are interested in.
        services_ids = []
        # services_ids has list of service id's that match the category filter

        for hit in categories:
            cats = self.session.query(ServiceDatas).join(Categories).filter(Categories.name.contains(hit))
            self.debug(cats)
            for serviceData in cats:
                if serviceData.services_id not in services_ids:
                    services_ids.append(serviceData.services_id)
        t2_end = time.time()

        labels_unfiltered = self.get_labellinks()
        final = []
        for x in labels_unfiltered:
            if (self.get_label(x.labels_id).name in labels) and (x.services_id in services_ids):
                final.append(x.services_id)
        t3_end = time.time()

        # Now Final has list of service id that march to label criteria.
        ids = list(set(final).intersection(services_ids))  # List of service ids matching both label and category filter
        contracts = self.session.query(Contracts).filter_by(
            userAccount_id=self.get_userAccount_by_username(username).id).all()
        for hit in contracts:  # Remove ids whom we already have contract with
            if hit.services_id in list(ids):  # We want to handle copy of a list, not the list.
                try:
                    ids.remove(hit.services_id)
                except Exception as e:
                    self.debug("Encountered error caused probably by nothing serious (Probably trying to remove id from"
                               " list that wasn't there to begin with): {}"
                               .format((error_handler(e, self.__class__.__name__))))
                    pass
        t4_end = time.time()
        services = []
        for ide in ids:
            s = self.get_service(ide)
            if s not in services:
                services.append(s)
        t5_end = time.time()
        dict_list = []
        for item in services:
            # self.session.query()
            categories_for_service = list(set([x.name.split(".")[0] for x in
                                               self.get_categories_by_service_id(item.id)]))

            labels_for_service = [self.get_label(x.labels_id).name for x in
                                  self.session.query(LabelLinks).filter_by(services_id=item.id).all()]
            template = {
                "id": item.id,
                "name": item.name,
                "img_url_overview": item.img_url_overview,
                "description": item.descriptionShort,
                "categories": categories_for_service,
                "labels": labels_for_service,
            }
            dict_list.append(template)
        hits = loads(self.parse_dict_list_to_json(dict_list))
        self.debug("Hits are: \n{}".format(hits))
        hits = self.current_count_filtering(hits, current, count)
        t6_end = time.time()
        self.info("Timings:\n"
                  " Initializing function:-----------|{}s\n"
                  " Filering Categories:-------------|{}s\n"
                  " Filtering Labels:----------------|{}s\n"
                  " Filtering Services with contract:|{}s\n"
                  " Fetch service Objects:-----------|{}s\n"
                  " Creating JSON for all hits-------|{}s\n"
                  "Total: {}s".format(t1_end - total_timer,
                                      t2_end - t1_end,
                                      t3_end - t2_end,
                                      t4_end - t3_end,
                                      t5_end - t4_end,
                                      t6_end - t5_end,
                                      t6_end - total_timer))
        return hits

    def ui_Services_id(self, ide, username):
        total_start = time.time()  # Initializing function
        service = self.get_service(ide)
        userAccount = self.get_userAccount_by_username(username)

        categories = [x.name.replace("-", " ").replace(".", " - ") for x in self.get_categories_by_service_id(ide)]
        main_categories = list(set([x.name.split(".")[0] for x in self.get_categories_by_service_id(ide)]))

        labels = [self.get_label(x.labels_id).name for x in
                  self.session.query(LabelLinks).filter_by(services_id=service.id).all()]

        service_ids_with_contract = [x.services_id for x in
                                     self.get_contracts_by_userAccount_id(userAccount.id) if
                                     x.services_id != service.id]

        t1_end = time.time()  # Filter Serv with C&P

        services_with_contract_and_potential = []
        for service_id in service_ids_with_contract:
            service_object = self.get_service(service_id)
            servi_categories = list(set([x.name.split(".")[0] for x in self.get_categories_by_service_id(service_id)]))

            if (len(set(main_categories).intersection(servi_categories)) > 0) and \
                    (service_id not in services_with_contract_and_potential):
                services_with_contract_and_potential.append(service_object)
        t2_end = time.time()  # Filter Serv with C
        try:
            potential_with_contract = \
                self.parse_dict_list_to_json([
                                                 {"id": x.id,

                                                  "role": self.get_servicetype(x.serviceTypes_id).type,

                                                  "contractID": self.get_contracts_by_userAccount_id_and_service_id(
                                                      userAccount.id, x.id).id,

                                                  "contractStatus": self.get_status(
                                                      self.get_contracts_by_userAccount_id_and_service_id(
                                                          userAccount.id, x.id).status_id).type
                                                  } for x in services_with_contract_and_potential])
        except Exception as e:
            potential_with_contract = "{}"

        t2_5_end = time.time()  # Filter own role from P:

        potential_with_contract = loads(potential_with_contract)
        for key in dict(potential_with_contract):
            if potential_with_contract[key]["role"] == self.get_servicetype(service.serviceTypes_id).type:
                potential_with_contract.pop(key, None)
        potential_with_contract = dumps(potential_with_contract)

        t3_end = time.time()  # Filter Serv with P no C

        potential_without_contract = self.parse_dict_list_to_json([{
                                                                       "id": x.id,
                                                                       "role": self.get_servicetype(
                                                                           x.serviceTypes_id).type
                                                                   }
                                                                   for x in list(set(self.get_services()) -
                                                                                 set(
                                                                                     services_with_contract_and_potential))])
        t4_end = time.time()  # Filter above
        potential_without_contract = loads(potential_without_contract)
        for key in dict(potential_without_contract):
            if potential_without_contract[key]["role"] == self.get_servicetype(service.serviceTypes_id).type:
                potential_without_contract.pop(key, None)
        potential_without_contract = dumps(potential_without_contract)
        t5_end = time.time()  # Filter Service with Consent

        service_with_consent = ""

        if self.get_servicetype(service.serviceTypes_id).type == "Source":
            try:
                self.debug("We are dealing with a Source.")
                service_with_consent_src = self.parse_dict_list_to_json([
                                                                            {"id": self.get_service(self.get_contract(
                                                                                x.sink_contract_id).services_id).id,

                                                                             "role": self.get_servicetype(
                                                                                 self.get_service(
                                                                                     self.get_contract(
                                                                                         x.sink_contract_id).services_id).serviceTypes_id).type,

                                                                             "consentStatus": self.get_status(
                                                                                 self.get_consentreceiptforsink(
                                                                                     x.sink_receipt)
                                                                                     .authorization_status).type,

                                                                             "consentID": x.id,

                                                                             "duration": "To be implemented"
                                                                             } for x in
                                                                            self.get_consentreceiptlinks_by_source_contract(
                                                                                self.get_contracts_by_userAccount_id_and_service_id(
                                                                                    userAccount.id,
                                                                                    service.id).id)
                                                                            ])

                service_with_consent_src = loads(service_with_consent_src)
                for key in dict(service_with_consent_src):
                    # When we look for services to connect to a Source, we must remove hits that are Sources.
                    if service_with_consent_src[key]["role"] == "Source":
                        service_with_consent_src.pop(key, None)
                service_with_consent = dumps(service_with_consent_src)
            except Exception as e:
                service_with_consent = "{}"

        else:
            try:
                self.debug("We are dealing with a Sink.")
                service_with_consent_sink = self.parse_dict_list_to_json(
                    [
                        {"id": self.get_service(self.get_contract(x.source_contract_id).services_id).id,

                         "role": self.get_servicetype(self.get_service(self.get_contract(x.source_contract_id)
                                                                       .services_id).serviceTypes_id).type,

                         "consentStatus": self.get_status(self.get_consentreceiptforsource(x.source_receipt)
                                                          .authorization_status).type,

                         "consentID": x.id,

                         "duration": "To be implemented"
                         } for x in self.get_consentreceiptlinks_by_sink_contract(
                        self.get_contracts_by_userAccount_id_and_service_id(
                            userAccount.id, service.id).id)
                        ])

                service_with_consent_sink = loads(service_with_consent_sink)

                for key in dict(service_with_consent_sink):
                    # When we look for services to connect to a sink, we must remove hits that are sinks.
                    if service_with_consent_sink[key]["role"] == "Sink":
                        service_with_consent_sink.pop(key, None)
                service_with_consent = dumps(service_with_consent_sink)
            except Exception as e:
                service_with_consent = "{}"
        t6_end = time.time()  # Filter stuff I need reminding why
        pot = {}
        self.debug("Before the filtering for loop:\n {}".format(service_with_consent))
        if service_with_consent != "{}":  # If service_with_consent is not empty
            swcons = loads(service_with_consent).keys()  # Make list of keys in Services_with_consent
            self.debug("swcon containts:\n {}".format(swcons))
            pwc = loads(potential_with_contract)  # Load potential services with contract as dictionary
            self.debug("pwc containts:\n {}".format(pwc))
            for hit in pwc:  # For each service in PWC
                if hit not in swcons and len(
                        hit) > 0:  # If service is not in services with consent list and is not empty
                    self.debug("We got hit: {}".format(hit))
                    pot.update({hit: pwc[hit]})  # Add service in pot dictionary
            potential_with_contract = dumps(pot)  # Update potential_with contract to be content of pot
            # This filters our services we have consent with from the list of services we have contract with (since we can have consent only with services we have contract already)
        t7_end = time.time()  # Generate JSON

        joined_dict = self.config["sources"]
        joined_dict.update(self.config["sinks"])
        self.debug("We got this service list:\n{}".format(repr(joined_dict)))
        common_consents = joined_dict[str(service.id)]["commonConsents"]
        self.debug("We have {}".format(repr(common_consents)))
        template = {
            service.id: {
                "name": service.name,
                "role": self.get_servicetype(service.serviceTypes_id).type,
                "img_url_logo": service.img_url_logo,
                "img_url_banner": service.img_url_banner,
                "img_url_overview": service.img_url_overview,
                "description": {
                    "short": service.descriptionShort,
                    "longer": service.descriptionLong
                },
                "categories": categories,
                "labels": labels,
                "commonConsents": common_consents,
                "potentialServicesWithoutContract": loads(potential_without_contract),
                "potentialServicesWithContract": loads(potential_with_contract),

                "servicesWithConsent": loads(service_with_consent)
            }
        }
        t8_end = time.time()
        self.info("Timings:\n"
                  " Initializing function:-----------|{}s\n"
                  " Filter Serv with C&P:------------|{}s\n"
                  " Filter Serv with C:--------------|{}s\n"
                  " Filter own role from P:----------|{}s\n"
                  " Filter Serv with P no C:---------|{}s\n"
                  " Filter above:--------------------|{}s\n"
                  " Filter Service with Consent:-----|{}s\n"
                  " Filter stuff I need reminding why|{}s\n"
                  " Generate JSON:-------------------|{}s\n"
                  "Total: {}s".format(t1_end - total_start,
                                      t2_end - t1_end,
                                      t2_5_end - t2_end,
                                      t3_end - t2_5_end,
                                      t4_end - t3_end,
                                      t5_end - t4_end,
                                      t6_end - t5_end,
                                      t7_end - t6_end,
                                      t8_end - t7_end,
                                      t8_end - total_start))
        return template

    def ui_Locations_and_Nationalities(self, table_name):
        self.debug("Entered function '{}' in class High with parameter:\n {}"
                   .format(currentframe().f_code.co_name, table_name))
        if table_name.lower() == "countries":
            objects = self.get_countries()
            reply = []
            for single_object in objects:
                reply.append(single_object.tojson)
            reply = self.parse_dict_list_to_json(reply)
            return reply
        if table_name.lower() == "nationalities":
            objects = self.get_nationalities()
            reply = []
            for single_object in objects:
                reply.append(single_object.tojson)
            reply = self.parse_dict_list_to_json(reply)
            return reply
        if table_name.lower() == "languages":
            objects = self.get_languages()
            reply = []
            for single_object in objects:
                reply.append(single_object.tojson)
            reply = self.parse_dict_list_to_json(reply)
            return reply
        if table_name.lower() == "regions":
            objects = self.get_regions()
            reply = []
            for single_object in objects:
                reply.append(single_object.tojson)
            reply = self.parse_dict_list_to_json(reply)
            return reply
        if table_name.lower() == "cities":
            objects = self.get_cities()
            reply = []
            for single_object in objects:
                reply.append(single_object.tojson)
            reply = self.parse_dict_list_to_json(reply)
            return reply

    def ui_Locations_and_Nationalities_id(self, table_name, ide):
        self.debug("Entered function '{}' in class High with parameters:\n {},\n {}"
                   .format(currentframe().f_code.co_name, table_name, ide))
        dictionary = loads(self.ui_Locations_and_Nationalities(table_name))
        return dictionary[ide]

    def SCT_correctly_formatted(self, SCT):
        self.debug("Entered function '{}' in class High with parameter:\n {}"
                   .format(currentframe().f_code.co_name, SCT))
        return True

    def ui_SCT_correctly_formatted(self, SCT):
        self.debug("Entered function '{}' in class High with parameter:\n {}"
                   .format(currentframe().f_code.co_name, SCT))
        return True

    def signing_function(self, SCT):
        self.debug("Entered function '{}' in class High with parameter:\n {}"
                   .format(currentframe().f_code.co_name, SCT))
        return True

    def ui_ConsentView(self, username, sink_id, source_id, consentID):
        self.debug("Entered function '{}' in class High with parameters:\n {},\n {},\n {}"
                   .format(currentframe().f_code.co_name, username, sink_id, source_id))
        sink = self.get_service(sink_id)
        source = self.get_service(source_id)

        service_categories = list(set([
                                          self.get_category(x.categories_id).name
                                          for x in
                                          self.session.query(ServiceDatas).filter_by(services_id=source.id).all()
                                          ]))

        list_of_licenses = [x.type.replace("-", " ").split(".") for x in self.get_licensetypes()]
        list_of_categories = [x.replace("-", " ").split(".") for x in service_categories]

        list_of_licenses_selected = self.get_active_licenses(consentID)
        list_of_categories_selected = self.get_active_categories(consentID)
        template = {
            "sink": {
                "name": sink.name,
                "service_id": sink.id,
                "img_url_logo": sink.img_url_logo,
                "licenses": list_of_licenses,
                "selected_licenses": list_of_licenses_selected
            },
            "source": {
                "name": source.name,
                "service_id": source.id,
                "img_url_logo": source.img_url_logo,
                "categories": list_of_categories,
                "selected_categories": list_of_categories_selected
            }
        }

        return template

    def make_contract(self, username, SCT):
        self.debug("Entered function '{}' in class High with parameter:\n {},\n {}"
                   .format(currentframe().f_code.co_name, username, SCT))
        contract = SCT
        contract["actor_id"] = int(contract["actor_id"])  # When we move to real UUID this needs to change appropriately
        userAccount_id = self.get_userAccount_by_username(username).id
        self.debug(contract["status"])
        status_id = self.get_status_by_type(contract["status"]).id
        services_id = contract["actor_id"]
        created = 0  # This gets added in the add_contract function
        serviceType = self.get_servicetype_by_type(contract["role"]).id
        legalRole = contract["legal_role"]
        contract_terms = contract["contract_terms"]
        intended_use = contract["intendet_use"]
        validity_period = contract["validity_period"]
        table = {"status_id": status_id,
                 "userAccount_id": userAccount_id,
                 "services_id": services_id,
                 "created": created,
                 "serviceType": serviceType,
                 "legalRole": legalRole,
                 "contract_terms": contract_terms,
                 "intended_use": intended_use,
                 "validity_period": validity_period}

        contract_id = self.add_contract(dumps(table))["id"]
        for data_type in contract["data_type"]:
            self.add_contractdatatype(dumps({"categories_id": self.get_category_by_name(data_type).id,
                                             "contracts_id": contract_id}))

    def src_ResourceSets(self):
        self.debug("Entered function '{}' in class High.".format(currentframe().f_code.co_name))
        rs = self.get_resourcesets()

        hits = []
        rs_ids = {}
        for hit in rs:
            category = self.get_category(hit.categories_id).name
            rs_id = hit.rs_id
            if rs_id not in rs_ids:
                rs_ids[str(rs_id)] = [category]
            else:
                rs_ids[str(rs_id)].append(category)

        for rs in rs_ids.keys():
            hits.append(dumps({"id": rs, "categories": rs_ids[rs]}))

        return self.parse_dict_list_to_json(hits)

    def src_ResourceSet(self, rs_id):
        self.debug("Entered function '{}' in class High with parameter:\n {}"
                   .format(currentframe().f_code.co_name, rs_id))
        rs = self.get_resourceset_by_rs_id(rs_id)
        return rs

    def get_active_licenses(self, consent_links_id):
        try:
            list_of_licenses = [
                self.get_licensetype(x.license_types_id).type.replace("-", " ").split(".")
                for x in self.get_licenselinks_by_recept(self.get_consentreceiptslink(consent_links_id).sink_receipt)
                ]

        except Exception as e:
            self.debug("Getting active licenses failed, probably we got no consent, returning empty list. Error:{}"
                       .format(repr(e)))
            return []
        return list_of_licenses

    def get_active_categories(self, consent_links_id):
        try:
            receipt = self.get_consentreceiptforsink(self.get_consentreceiptslink(consent_links_id).id)
            rs_id = self.get_resourceset_by_rs_id(receipt.rs_id)
            rs_id = rs_id[rs_id.keys()[0]]
            list_of_categories = [x.replace("-", " ").split(".") for x in rs_id["categories"]]
        except Exception as e:
            self.debug("Getting active categories failed, probably we got no consent, returning empty list.")
            return []
        return list_of_categories

    def CreateResourceSet(self, js):
        self.debug("Entered function '{}' in class High with parameter:\n {}"
                   .format(currentframe().f_code.co_name, js))
        categories = js["categories"]
        ext_id = self.get_ext_id_by_username_and_service(js["username"], js["service_id"])
        service_id = ext_id.services_id  # Probably bit redundant since we could just js["service_id"] but verifies ext_id
        service = self.get_service(service_id)
        source_url = "http://{}:{}".format(service.ip_address, service.port_api)
        rs_id = "{}{}/{}".format(source_url, service.data_api, str(guid()))
        userAccount = self.get_userAccount_by_username(js["username"])
        contract = self.get_contracts_by_userAccount_id_and_service_id(userAccount.id, service_id)
        rq_js = {"categories": categories,
                 "rs_id": rs_id}
        # Register at source:
        self.info("Sending DataSource Resource Set")
        self.debug("service url: {}".format(source_url))
        registration = requests.post("{}/api/v0.1/resource_set".format(source_url),
                                     headers={"Authorization": "bearer {}".format(ext_id.ext_id)}, json=rq_js)
        helper_id = ""
        if registration.__bool__():  # Returns True if response is OK
            self.info("Registering of ResourceSet to DataSource was successful and we received OK 200.")
            self.debug("Adding resourceset to DB tables.")
            for category in categories:  # Loop trough categories and add each one to resource set table, This breaks
                table = {  # getting resource_sets as those functions expect unique rs_id field
                    "rs_id": rs_id,
                    "contracts_id": contract.id,
                    "categories_id": self.get_category_by_name(category).id
                }
                self.debug("Adding row:\n {}".format(dumps(table, indent=3)))
                helper_id = self.add_resourceset(dumps(table))

            reply = {"rs_id": rs_id,
                     "categories": categories
                     }
            return reply
        else:
            raise CustomError(description="DataSource didn't reply OK to our message. We received code {}"
                                          " and message: {}"
                              .format(registration.status_code, registration.text), code=500)

    def generate_rpt(self, rs_id):
        self.debug("Entered function '{}' in class High with parameter:\n {}"
                   .format(currentframe().f_code.co_name, rs_id))
        now = int(time.time())
        TOKEN_VALID_FOR = 999999999999
        alg = "RS256"
        iat = str(now)
        exp = str(now + TOKEN_VALID_FOR)
        iss = "DataOperator"
        rpt_payload = {"iat": iat, "exp": exp, "iss": iss, "rs_id": decode_url(rs_id)}
        self.debug("RPT payload: {}".format(repr(rpt_payload)))
        rpt = jwt.encode(rpt_payload, operator_rsa_private, algorithm=alg)
        self.debug("Generated RPT: {}".format(repr(rpt)))
        return rpt

    def create_consent_receipt(self, js, username):
        '''
        JSON in js
        {
         "source_id": id,
         "sink_id": id,
         "rs_id": rs_id,
         "usage_license": [license]
         "status": status
        }
        '''
        js["rs_id"] = encode_url(js["rs_id"])
        self.debug("Entered function '{}' in class High with parameters:\n {},\n {}"
                   .format(currentframe().f_code.co_name, js, username))
        userAccount = self.get_userAccount_by_username(username)
        sink = self.get_service(js["sink_id"])
        source = self.get_service(js["source_id"])
        self.debug("We got sink {} and source {}".format(sink.name, source.name))
        source_url = "http://{}:{}".format(source.ip_address, source.port_api)
        sink_url = "http://{}:{}".format(sink.ip_address, sink.port_api)
        self.debug("We got sink_url {} and source_url {}".format(sink_url, source_url))
        categories = self.get_resourceset_by_rs_id(js["rs_id"])[js["rs_id"]]["categories"]
        status = self.get_status_by_type(js["status"])
        service_contract_id_sink = self.get_contracts_by_userAccount_id_and_service_id(userAccount.id, js["sink_id"]).id
        service_contract_id_src = self.get_contracts_by_userAccount_id_and_service_id(userAccount.id,
                                                                                      js["source_id"]).id
        summary = Summaries(data_source=js["source_id"], data_sink=js["sink_id"])
        self.session.add(summary)
        self.session.flush()
        sink_db_object = ConsentReceiptsForSink(userAccount_id=userAccount.id,
                                                authorization_status=status.id,
                                                consent_summary=summary.id,
                                                rs_id=js["rs_id"]
                                                )

        self.session.add(sink_db_object)

        source_db_object = ConsentReceiptsForSource(userAccount_id=userAccount.id,
                                                    authorization_status=status.id,
                                                    key_used_to_sign_rpt=pub_key,
                                                    consent_summary=summary.id,
                                                    rs_id=js["rs_id"]
                                                    )
        self.session.add(source_db_object)
        self.session.flush()
        licenseLink_templates = [self.session.add(LicenseLinks(sink_receipt_id=sink_db_object.id,
                                                               license_types_id=self.get_licensetype_by_type(
                                                                   x.replace(" ", "-")).id))
                                 for x in js["usage_license"]]
        self.session.flush()
        templu_sink = {"consentReceipt": {
            "consent_receipt_id": sink_db_object.id,
            "account_id": self.get_ext_id_by_username_and_service(username, sink.id).ext_id,
            "service_contract_id": service_contract_id_sink,
            "rs_id": decode_url(js["rs_id"]),
            "data_usage_license": ",".join([self.get_licensetype_by_type(x.replace(" ", "-")).type
                                            for x in js["usage_license"]]),
            "authorization_status": self.get_status_by_type(js["status"]).type,
            "consent_summary": {
                "data_source": {
                    "name": source.name,
                    "description": source.descriptionShort
                },
                "data_sink": {
                    "name": sink.name,
                    "description": sink.descriptionShort
                },
                "data": categories  # List
            }
        },
            "rpt": self.generate_rpt(js["rs_id"])
        }
        self.debug(dumps(templu_sink, indent=3))

        templu_source = {"consentReceipt": {
            "consent_receipt_id": source_db_object.id,
            "account_id": self.get_ext_id_by_username_and_service(username, source.id).ext_id,
            "service_contract_id": service_contract_id_src,
            "rs_id": decode_url(js["rs_id"]),
            "key_used_to_sign_rpt": pub_key,
            "authorization_status": self.get_status_by_type(js["status"]).type,
            "consent_summary": {
                "data_source": {
                    "name": source.name,
                    "description": source.descriptionShort
                },
                "data_sink": {
                    "name": sink.name,
                    "description": sink.descriptionShort
                },
                "data": categories  # List
            }
        }
        }
        self.debug(dumps(templu_source, indent=3))
        ext_id_src = self.get_ext_id_by_username_and_service(username, source.id).ext_id
        ext_id_sink = self.get_ext_id_by_username_and_service(username, sink.id).ext_id
        try:
            self.info("Sending DataSink at {} a consent receipt.".format(sink_url))

            req = requests.post("{}/api/v0.1/receipt".format(sink_url),
                                json=templu_sink,
                                headers={"Authorization": "bearer {}".format(ext_id_sink)}
                                )
            sink_success = req.status_code == requests.codes.created
            if req.status_code == 409:  # TODO: Do this better. If sink has this receipt already in database we get 409.
                sink_success = True
            self.info("sink_success = {}".format(sink_success))
            self.debug("Sink replied:\n{}".format(req.text))
            self.info("Sending DataSource at {} a consent receipt.".format(source_url))

            req = requests.post("{}/api/v0.1/receipt".format(source_url),
                                json=templu_source,
                                headers={"Authorization": "bearer {}".format(ext_id_src)}
                                )

            source_success = req.status_code == requests.codes.created
            self.info("source_success = {}".format(source_success))
            self.debug("Source replied:\n{}".format(req.text))
        except Exception as e:
            self.error("Connection to service failed:{}".format(repr(e)))
            self.session.rollback()
            raise CustomError(description="Connection to service failed with error:{}"
                              .format((error_handler(e, self.__class__.__name__))))
        if sink_success and source_success:
            self.info("Successfully delivered receipts to services, adding ConsentReceiptLink and committing DB.")
            js = {
                "source_receipt": source_db_object.id,
                "sink_receipt": sink_db_object.id,
                "source_contract_id": service_contract_id_src,
                "sink_contract_id": service_contract_id_sink
            }
            self.add_consentreceiptslink(dumps(js))  # This will also run commit for above objects.
            self.info("Finished consent receipt delivery successfully.")
        else:
            self.error("Failed to deliver receipt to services:\n  sink = {}\n  source = {}".format(sink_success,
                                                                                                   source_success))
            self.error("Rolling DB back to revert any changes.")
            self.session.rollback()
