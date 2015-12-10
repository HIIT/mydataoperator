# -*- coding: utf-8 -*-
__author__ = 'Aleksi Palomäki'

from json import loads, dumps
from inspect import currentframe
import datetime
from base64 import b64encode as encode_url
from resources.Resources import Users, Statuses, Cities, Regions, Countries, Nationalities, Languages, UserAccounts, \
    Categories, ServiceTerms, ServiceTypes, Services, ServiceDatas, Labels, LabelLinks, Summaries, \
    LicenseTypes, ConsentReceiptsForSource, ConsentReceiptsForSink, ConsentReceiptsLinks, Contracts, ContractDataTypes, \
    SummaryDataTypes, Ext_ids, ResourceSets, LicenseLinks
from passlib.hash import sha256_crypt
from custom_errors import CustomError
from db_handler import DB_Handler, error_handler


class Basic(DB_Handler):
    '''Methods for user'''

    def add_user(self, user_info):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, user_info))
        user_info = loads(user_info)
        user = Users()
        for item in user_info:
            value = user_info[item]
            setattr(user, item, value)
        try:
            ide = self.add(user)
            return {"status": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def get_user_by_email(self, user_email):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, user_email))
        hits = self.session.query(Users).filter_by(email=user_email).all()
        if len(hits) == 1:
            self.info("User with first name {} and user id {} found.".format(hits[0].firstName, hits[0].id))
            return hits[0]
        else:
            self.warning("User with email {} not found.".format(user_email))
            return None

    def get_user(self, user_id):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, user_id))

        hits = self.session.query(Users).filter_by(id=user_id).all()
        if len(hits) == 1:
            self.debug(hits)
            self.info("User with first name {} and user id {} found.".format(hits[0].firstName, hits[0].id))
            return hits[0]
        else:
            self.warning("User with id {} not found.".format(user_id))
            return None

    def delete_user(self, user_id):  # TODO: This function return values are inconsistent with lot of other stuff.
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, user_id))

        try:
            self.session.query(Users).filter_by(id=user_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_user(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        info = loads(dict_containing_new_data_and_id)
        Object = self.get_user(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    ''' Methods for countries '''

    def add_country(self, country_name):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, country_name))
        country = Countries(name=country_name)
        try:
            ide = self.add(country)
            return {"status": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format(error_handler(e, self.__class__.__name__)), code=500)

    def get_country(self, country_id):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, country_id))
        hits = self.session.query(Countries).filter_by(id=country_id).all()
        if len(hits) == 1:
            self.debug(hits)
            self.info("Found country {} with id {}.".format(hits[0].name, hits[0].id))
            return hits[0]
        else:
            self.warning("Didn't find country {}.".format(country_id))
            return None

    def get_country_by_name(self, country_name):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, country_name))
        hits = self.session.query(Countries).filter_by(name=country_name).all()
        if len(hits) >= 1:
            self.debug(hits[0])
            self.info("Found country {} with id {}.".format(hits[0].name, hits[0].id))
            return hits[0]
        else:
            self.warning("Didn't find country {}.".format(country_name))
            return None

    def get_countries(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(Countries)

    def delete_country(self, country_id):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, country_id))
        self.session.query(Countries).filter_by(id=country_id).delete()
        self.session.commit()

    ''' Methods for cities   '''

    def add_city(self, city_name, region_name):
        self.debug("Entered function '{}' in class Basic with parameter: {}, {}"
                   .format(currentframe().f_code.co_name, city_name, region_name))
        region_id = self.get_region_by_name(region_name).id
        city = Cities(name=city_name, region_id=region_id)
        try:
            ide = self.add(city)
            return {"status": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def get_city(self, city_id):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, city_id))
        hits = self.session.query(Countries).filter_by(id=city_id).all()
        if len(hits) == 1:
            self.debug(hits)
            self.info("Found city {} with id {}.".format(hits[0].name, hits[0].id))
            return hits[0]
        else:
            self.warning("Didn't find city {}.".format(city_id))
            return None

    def get_cities_by_region(self, region_id):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, region_id))
        hits = self.session.query(Cities).filter_by(region_id=region_id).all()
        return hits

    def get_cities(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(Cities)

    def delete_city(self, city_id):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, city_id))
        self.session.query(Cities).filter_by(id=city_id).delete()
        self.session.commit()

    ''' Methods for regions   '''

    def add_region(self, region_name, country_name):
        self.debug("Entered function '{}' in class Basic with parameter: {}, {}"
                   .format(currentframe().f_code.co_name, region_name, country_name))
        country_id = self.get_country_by_name(country_name).id
        region = Regions(name=region_name, country_id=country_id)
        try:
            ide = self.add(region)
            return {"status": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def get_region(self, region_id):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, region_id))
        hits = self.session.query(Regions).filter_by(id=region_id).all()
        if len(hits) == 1:
            self.debug(hits)
            self.info("Found region {} with id {}.".format(hits[0].name, hits[0].id))
            return hits[0]
        else:
            self.warning("Didn't find region {}.".format(region_id))
            return None

    def get_region_by_name(self, region_name):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, region_name))
        hits = self.session.query(Regions).filter_by(name=region_name).all()
        if len(hits) == 1:
            self.debug(hits)
            self.info("Found region {} with id {}.".format(hits[0].name, hits[0].id))
            return hits[0]
        else:
            self.warning("Didn't find region {}.".format(region_name))
            return None

    def get_regions_by_country(self, country_id):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, country_id))
        hits = self.session.query(Regions).filter_by(country_id=country_id).all()
        return hits

    def get_regions(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(Regions)

    def delete_region(self, region_id):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, region_id))
        self.session.query(Regions).filter_by(id=region_id).delete()
        self.session.commit()

    ''' Methods for languages '''

    def add_language(self, language_name):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, language_name))
        language = Languages(name=language_name)
        try:
            ide = self.add(language)
            return {"status": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def get_language(self, language_id):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, language_id))
        hits = self.session.query(Languages).filter_by(id=language_id).all()
        if len(hits) == 1:
            self.debug(hits)
            self.info("Found language {} with id {}.".format(hits[0].name, hits[0].id))
            return hits[0]
        else:
            self.warning("Didn't find language {}.".format(language_id))
            return None

    def get_language_by_name(self, language_name):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, language_name))
        hits = self.session.query(Languages).filter_by(name=language_name).all()
        if len(hits) >= 1:
            self.debug(hits)
            self.info("Found language {} with id {}.".format(hits[0].name, hits[0].id))
            return hits[0]
        else:
            self.warning("Didn't find language {}.".format(language_name))
            return None

    def get_languages(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(Languages)

    def delete_language(self, language_id):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, language_id))
        self.session.query(Languages).filter_by(id=language_id).delete()
        self.session.commit()

    ''' Methods for nationalities '''

    def add_nationality(self, nationality_name):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, nationality_name))
        nationality = Nationalities(name=nationality_name)
        try:
            ide = self.add(nationality)
            return {"status": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def get_nationality(self, nationality_id):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, nationality_id))
        hits = self.session.query(Nationalities).filter_by(id=nationality_id).all()
        if len(hits) == 1:
            self.debug(hits)
            self.info("Found nationality {} with id {}.".format(hits[0].name, hits[0].id))
            return hits[0]
        else:
            self.warning("Didn't find nationality {}.".format(nationality_id))
            return None

    def get_nationality_by_name(self, nationality_name):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, nationality_name))
        hits = self.session.query(Nationalities).filter_by(name=nationality_name).all()
        if len(hits) >= 1:
            self.debug(hits)
            self.info("Found nationality {} with id {}.".format(hits[0].name, hits[0].id))
            return hits[0]
        else:
            self.warning("Didn't find nationality {}.".format(nationality_name))
            return None

    def get_nationalities(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(Nationalities)

    def delete_nationality(self, nationality_id):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, nationality_id))
        self.session.query(Nationalities).filter_by(id=nationality_id).delete()
        self.session.commit()

    '''Methods for userAccounts'''

    def add_userAccount(self, userAccount_info):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, userAccount_info))
        userAccount_info = loads(userAccount_info)

        userAccount = UserAccounts()
        for item in userAccount_info:
            value = userAccount_info[item]
            setattr(userAccount, item, value)
        try:
            ide = self.add(userAccount)
            return {"status": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def get_userAccount(self, userAccount_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, userAccount_id))
        hits = self.session.query(UserAccounts).filter_by(id=userAccount_id).all()
        if len(hits) == 1:
            self.debug(hits)
            self.info("UserAccount with username {} and user account id {} found.".format(hits[0].username, hits[0].id))
            return hits[0]
        else:
            self.warning("UserAccount with id {} not found.".format(userAccount_id))
            return None

    def get_userAccounts(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(UserAccounts)

    def get_userAccount_by_username(self, username):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, username))
        hits = self.session.query(UserAccounts).filter_by(username=username).all()
        if len(hits) == 1:
            self.info("UserAccount with username {} and user account id {} found.".format(hits[0].username, hits[0].id))
            return hits[0]
        else:
            self.warning("UserAccount with username {} not found.".format(username))
            return None

    def delete_userAccount(self, userAccount_id):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, userAccount_id))
        try:
            self.session.query(UserAccounts).filter_by(id=userAccount_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            error_handler(e, self.__class__.__name__)
            return False

    def modify_userAccount(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        info = loads(dict_containing_new_data_and_id)
        if info.get("password", False):
            self.info("We are changing password!")
            info["password"] = sha256_crypt.encrypt(info["password"])
            dict_containing_new_data_and_id = dumps(info)
        Object = self.get_userAccount(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''Statuses '''

    def get_status(self, status_id):
        object_id = status_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "Status"
        Object = Statuses

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_status_by_type(self, type):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, type))
        hits = self.session.query(Statuses).filter_by(type=type).first()
        return hits

    def get_statuses(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(Statuses)

    def add_status(self, status_info):  # status_info should not contain id.
        self.debug("Entered function '{}' in class Basic with patameter:\n {}".format(currentframe().f_code.co_name,
                                                                                      status_info))
        js = loads(status_info)
        Object = Statuses()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = self.add(Object)
            return {"status": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_status(self, status_id):
        object_id = status_id
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = Statuses
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:  # TODO: Return values should be consistent, raise, False, which is better?
            self.error("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)
            return False

    def modify_status(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_status

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''Labels '''

    def get_label(self, label_id):
        object_id = label_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "Label"
        Object = Labels

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_labels(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(Labels)

    def get_label_by_name(self, name):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, name))
        hits = self.session.query(Labels).filter_by(name=name).first()
        return hits

    def add_label(self, label_info):  # label_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(label_info)
        Object = Labels()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = self.add(Object)
            return {"label": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_label(self, label_id):
        object_id = label_id
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = Labels
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error: {}".format(error_handler(e, self.__class__.__name__)))
            return False

    def modify_label(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_label

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''Categories '''

    def get_category(self, category_id):
        object_id = category_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "Category"
        Object = Categories

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_category_by_name(self, name):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, name))
        hits = self.session.query(Categories).filter_by(name=name).first()
        return hits

    def get_categories(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(Categories)

    def get_categories_by_service_id(self, service_id):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        hits = self.session.query(Categories).join(ServiceDatas).filter(ServiceDatas.services_id == service_id).all()
        # hits = list(set([self.get_category(x.categories_id) for x in self.session.query(ServiceDatas)
        # .filter_by(services_id=service_id).all()]))
        return hits

    def add_category(self, category_info):  # category_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(category_info)
        Object = Categories()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = self.add(Object)
            return {"category": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_category(self, category_id):
        object_id = category_id
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = Categories
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error {} in {}".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_category(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_category

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''ServiceTerms '''

    def get_serviceterm(self, serviceterm_id):
        object_id = serviceterm_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "ServiceTerm"
        Object = ServiceTerms

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_serviceterms(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(ServiceTerms)

    def add_serviceterm(self, serviceterm_info):  # serviceterm_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(serviceterm_info)
        Object = ServiceTerms()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = self.add(Object)
            return {"serviceterm": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_serviceterm(self, serviceterm_id):
        object_id = serviceterm_id
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = ServiceTerms
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error {} in {}".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_serviceterm(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_serviceterm

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''ServiceTypes '''

    def get_servicetype(self, servicetype_id):
        object_id = servicetype_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "ServiceType"
        Object = ServiceTypes

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_servicetype_by_type(self, type):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, type))
        hits = self.session.query(ServiceTypes).filter_by(type=type).first()
        return hits

    def get_servicetypes(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(ServiceTypes)

    def add_servicetype(self, servicetype_info):  # servicetype_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(servicetype_info)
        Object = ServiceTypes()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = self.add(Object)
            return {"servicetype": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_servicetype(self, servicetype_id):
        object_id = servicetype_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = ServiceTypes
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_servicetype(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_servicetype

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''Services '''

    def get_service(self, service_id):
        object_id = service_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "Service"
        Object = Services

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_services(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(Services)

    def add_service(self, service_info):  # service_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(service_info)
        Object = Services()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = self.add(Object)
            return {"service": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_service(self, service_id):
        object_id = service_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = Services
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_service(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_service

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''ServiceDatas '''

    def get_servicedata(self, servicedata_id):
        object_id = servicedata_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "ServiceData"
        Object = ServiceDatas

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_servicedatas(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(ServiceDatas)

    def get_services_ids_by_category(self, category_id):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        hits = self.session.query(ServiceDatas).join(Categories).filter(
            Categories.id == category_id).all()  # TODO check functionality.
        # hits = self.session.query(Categories).join(ServiceDatas).filter(ServiceDatas.services_id==service_id).all()
        self.debug("We got hits: {}".format(hits))
        return hits

    def add_servicedata(self, servicedata_info):  # servicedata_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(servicedata_info)
        Object = ServiceDatas()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = self.add(Object)
            return {"servicedata": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_servicedata(self, servicedata_id):
        object_id = servicedata_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = ServiceDatas
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_servicedata(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_servicedata

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''ContractDataTypes '''

    def get_contractdatatype(self, contractdatatype_id):
        object_id = contractdatatype_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "ContractDataType"
        Object = ContractDataTypes

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_contractdatatypes(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(ContractDataTypes)

    def get_contractdatatypes_by_contract_id(self, contract_id):
        object_id = contract_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "ContractDataType"
        Object = ContractDataTypes
        hits = self.session.query(Object).filter_by(contracts_id=object_id).all()
        hits_string = "{" + "".join([x.tojson + ",\n" for x in hits]) + "}"
        self.debug("We got hits:\n{}".format(hits_string))
        return hits

    def add_contractdatatype(self, contractdatatype_info):  # contractdatatype_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(contractdatatype_info)
        Object = ContractDataTypes()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = self.add(Object)
            return {"contractdatatype": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_contractdatatype(self, contractdatatype_id):
        object_id = contractdatatype_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = ContractDataTypes
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_contractdatatype(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_contractdatatype

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''SummaryDataTypes '''

    def get_summarydatatype(self, summarydatatype_id):
        object_id = summarydatatype_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "SummaryDataType"
        Object = SummaryDataTypes

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_summarydatatypes(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(SummaryDataTypes)

    def get_summarydatatypes_by_summaries_id(self, summaries_id):
        object_id = summaries_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "SummaryDataType"
        Object = SummaryDataTypes

        hits = self.session.query(Object).filter_by(summaries_id=object_id).all()
        if len(hits) > 0:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def add_summarydatatype(self, summarydatatype_info):  # summarydatatype_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(summarydatatype_info)
        Object = SummaryDataTypes()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = ide = self.add(Object)
            return {"summarydatatype": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_summarydatatype(self, summarydatatype_id):
        object_id = summarydatatype_id
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = SummaryDataTypes
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_summarydatatype(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_summarydatatype

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''LabelLinks '''

    def get_labellink(self, labellink_id):
        object_id = labellink_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "LabelLink"
        Object = LabelLinks

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_labellinks(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(LabelLinks)

    def add_labellink(self, labellink_info):  # labellink_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(labellink_info)
        Object = LabelLinks()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = ide = self.add(Object)
            return {"labellink": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_labellink(self, labellink_id):
        object_id = labellink_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = LabelLinks
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_labellink(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_labellink

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''LicenseLinks '''

    def get_licenselink(self, licenselink_id):
        object_id = licenselink_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "LicenseLink"
        Object = LicenseLinks

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_licenselinks_by_recept(self, receipt_id):
        object_id = receipt_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "LicenseLink"
        Object = LicenseLinks

        hits = self.session.query(Object).filter_by(sink_receipt_id=object_id).all()
        if len(hits) >= 1:
            self.debug("{} found.".format(object_name))
            return hits
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_licenselinks(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(LicenseLinks)

    def add_licenselink(self, licenselink_info):  # licenselink_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(licenselink_info)
        Object = LicenseLinks()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = ide = self.add(Object)
            return {"licenselink": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_licenselink(self, licenselink_id):
        object_id = licenselink_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = LicenseLinks
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_licenselink(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_licenselink

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''Summaries '''

    def get_summary(self, summary_id):
        object_id = summary_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "Summary"
        Object = Summaries

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_summaries(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(Summaries)

    def add_summary(self, summary_info):  # summary_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(summary_info)
        Object = Summaries()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = self.add(Object)
            return {"summary": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_summary(self, summary_id):
        object_id = summary_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = Summaries
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_summary(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_summary

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''Ext_ids '''

    def get_ext_id(self, ext_id_id):
        object_id = ext_id_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "Ext_id"
        Object = Ext_ids

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_ext_id_by_username_and_service(self, username, service_id):
        Object = Ext_ids
        object_name = "Ext_id"
        userAccount_id = self.get_userAccount_by_username(username).id
        hits = self.session.query(Object).filter_by(userAccounts_id=userAccount_id, services_id=service_id).all()
        if len(hits) == 1 or len(hits) >= 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with userAccounts_id {} and services_id {} not found."
                         .format(object_name, userAccount_id, service_id))
            return None

    def get_ext_id_by_ext_id(self, ext_id):
        Object = Ext_ids
        object_name = "Ext_id"
        hits = self.session.query(Object).filter_by(ext_id=ext_id).all()
        if len(hits) == 1 or len(hits) >= 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with ext_id {} not found."
                         .format(object_name, ext_id))
            return None

    def get_ext_ids(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(Ext_ids)

    def add_ext_id(self, ext_id_info):  # ext_id_info should not contain id.
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, ext_id_info))
        js = loads(ext_id_info)
        Object = Ext_ids()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = self.add(Object)
            return {"ext_id": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_ext_id(self, ext_id_id):
        object_id = ext_id_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = Ext_ids
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_ext_id(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_ext_id

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''LicenseTypes '''

    def get_licensetype(self, licensetype_id):
        object_id = licensetype_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "LicenseType"
        Object = LicenseTypes

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_licensetype_by_type(self, licensetype):
        object_id = licensetype
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "LicenseType"
        Object = LicenseTypes

        hits = self.session.query(Object).filter_by(type=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_licensetypes(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(LicenseTypes)

    def add_licensetype(self, licensetype_info):  # licensetype_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(licensetype_info)
        Object = LicenseTypes()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = self.add(Object)
            return {"licensetype": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_licensetype(self, licensetype_id):
        object_id = licensetype_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = LicenseTypes
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_licensetype(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_licensetype

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''ConsentReceiptsForSource '''

    def get_consentreceiptforsource(self, consentreceiptforsource_id):
        object_id = consentreceiptforsource_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "ConsentReceiptForSource"
        Object = ConsentReceiptsForSource

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_consentreceiptsforsource(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(ConsentReceiptsForSource)

    def add_consentreceiptforsource(self, consentreceiptforsource_info):  # consentreceiptforsource_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(consentreceiptforsource_info)
        Object = ConsentReceiptsForSource()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = self.add(Object)
            return {"consentreceiptforsource": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_consentreceiptforsource(self, consentreceiptforsource_id):
        object_id = consentreceiptforsource_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = ConsentReceiptsForSource
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_consentreceiptforsource(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_consentreceiptforsource

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''Consentreceiptsforsink '''

    def get_consentreceiptforsink(self, consentreceiptforsink_id):
        object_id = consentreceiptforsink_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "ConsentReceiptForSink"
        Object = ConsentReceiptsForSink

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_consentreceiptsforsink(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(ConsentReceiptsForSink)

    def add_consentreceiptforsink(self, consentreceiptforsink_info):  # consentreceiptforsink_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(consentreceiptforsink_info)
        Object = ConsentReceiptsForSink()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = self.add(Object)
            return {"consentreceiptforsink": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_consentreceiptforsink(self, consentreceiptforsink_id):
        object_id = consentreceiptforsink_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = ConsentReceiptsForSink
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_consentreceiptforsink(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_consentreceiptforsink

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''Contracts '''

    def get_contract(self, contract_id):
        object_id = contract_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "Contract"
        Object = Contracts

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_contracts_by_userAccount_id_and_service_id(self, userAccount_id, service_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}\n {}"
                   .format(currentframe().f_code.co_name, userAccount_id, service_id))
        hits = self.session.query(Contracts).filter_by(userAccount_id=userAccount_id, services_id=service_id).all()
        return hits[0]

    def get_contracts_by_userAccount_id(self, userAccount_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, userAccount_id))
        hits = self.session.query(Contracts).filter_by(userAccount_id=userAccount_id).all()
        return hits

    def get_contracts(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(Contracts)

    def add_contract(self, contract_info):  # contract_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(contract_info)
        js["created"] = datetime.datetime.now()
        Object = Contracts()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = self.add(Object)
            return {"contract": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_contract(self, contract_id):
        object_id = contract_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = Contracts
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_contract(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_contract

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''Consentreceiptslinks '''

    def get_consentreceiptslink(self, consentreceiptslink_id):
        object_id = consentreceiptslink_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "ConsentReceiptsLink"
        Object = ConsentReceiptsLinks

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_consentreceiptlinks_by_source_contract(self, contract_id):
        object_id = contract_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "ConsentReceiptsLink"
        Object = ConsentReceiptsLinks

        hits = self.session.query(Object).filter_by(source_contract_id=object_id).all()
        self.debug("We found: {}".format([x.tojson for x in hits]))
        if len(hits) > 0:
            # self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits
        else:
            self.warning("{} with source id {} not found.".format(object_name, object_id))
            return None

    def get_consentreceiptlinks_by_sink_contract(self, contract_id):
        object_id = contract_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "ConsentReceiptsLink"
        Object = ConsentReceiptsLinks

        hits = self.session.query(Object).filter_by(sink_contract_id=object_id).all()
        if len(hits) > 0:
            # self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_consentreceiptslinks(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(ConsentReceiptsLinks)

    def add_consentreceiptslink(self, consentreceiptslink_info):  # consentreceiptslink_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(consentreceiptslink_info)
        Object = ConsentReceiptsLinks()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = self.add(Object)
            return {"consentreceiptslink": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_consentreceiptslink(self, consentreceiptslink_id):
        object_id = consentreceiptslink_id
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = ConsentReceiptsLinks
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_consentreceiptslink(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_consentreceiptslink

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)

    '''ResourceSets '''

    def get_resourceset(self, resourceset_id):
        object_id = resourceset_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        object_name = "ResourceSet"
        Object = ResourceSets

        hits = self.session.query(Object).filter_by(id=object_id).all()
        if len(hits) == 1:
            self.info("{} found with content:\n{}".format(object_name, hits[0].tojson))
            return hits[0]
        else:
            self.warning("{} with id {} not found.".format(object_name, object_id))
            return None

    def get_resourceset_by_rs_id(self, rs_id):
        self.debug("Entered function '{}' in class Basic with parameter: {}"
                   .format(currentframe().f_code.co_name, rs_id))
        rs_sets = self.session.query(ResourceSets).filter_by(rs_id=rs_id).all()
        rs_ids = {}
        for hit in rs_sets:
            if hit.rs_id not in rs_ids:
                rs_ids[str(hit.rs_id)] = {}
                rs_ids[str(hit.rs_id)]["categories"] = [self.get_category(hit.categories_id).name]
            else:
                rs_ids[str(hit.rs_id)]["categories"].append(self.get_category(hit.categories_id).name)
        return rs_ids

    def get_resourcesets(self):
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        return self.get_table(ResourceSets)

    def add_resourceset(self, resourceset_info):  # resourceset_info should not contain id.
        self.debug("Entered function '{}' in class Basic.".format(currentframe().f_code.co_name))
        js = loads(resourceset_info)
        js["rs_id"] = encode_url(js["rs_id"])
        Object = ResourceSets()
        for item in js:
            value = js[item]
            setattr(Object, item, value)
        try:
            ide = self.add(Object)
            return {"resourceset": True, "Error": None, "id": ide}
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            raise CustomError("We encountered error: {}".format((error_handler(e, self.__class__.__name__))), code=500)

    def delete_resourceset(self, resourceset_id):
        object_id = resourceset_id
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, object_id))
        Object = ResourceSets
        try:
            self.session.query(Object).filter_by(id=object_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.error("We encountered error '{}' in '{}'".format(repr(e), currentframe().f_code.co_name))
            return False

    def modify_resourceset(self, dict_containing_new_data_and_id):
        self.debug("Entered function '{}' in class Basic with parameter:\n {}"
                   .format(currentframe().f_code.co_name, dict_containing_new_data_and_id))
        get_method = self.get_resourceset

        info = loads(dict_containing_new_data_and_id)
        Object = get_method(info["id"])
        self.modify(Object, dict_containing_new_data_and_id)
