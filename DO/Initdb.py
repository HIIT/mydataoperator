# -*- coding: utf-8 -*-
__author__ = 'Aleksi Palomäki'
from json import dumps
from db_handler import error_handler

# This class expects High class DB_handler.
class Test_editable:
    def __init__(self, db):
        self.db = db
        # self.consent_test()
        self.initialize()
        # logging.shutdown()
        # reload(logging)

    def consent_test(self):
        js = {
            "source_id": "2",
            "sink_id": "3",
            "rs_id": "srughvsurhw0299217dh",
            "usage_license": "1",
            "status": "active",
        }
        username = "allu"
        self.db.create_consent_receipt(js, username)

    def initialize(self):

        #  Add countries, regions and cities
        try:
            self.db.debug("Adding Template Countries, Regions and Cities.")
            self.db.add_country("Finland")
            self.db.add_country("Sweden")
            self.db.add_region("Pohjois-Pohjanmaa", "Finland")
            self.db.add_region("Norrbotten", "Sweden")
            self.db.add_city("Oulu", "Pohjois-Pohjanmaa")
            self.db.add_city("Torn", "Norrbotten")
        except Exception as e:
            self.db.error("Something went wrong while adding templates for countries, regions and cities: {}"
                          .format((error_handler(e, self.__class__.__name__))))
            pass
        # Add languages and Nationalities
        try:
            self.db.debug("Adding Template Languages and Nationalities.")
            self.db.add_language("Finnish")
            self.db.add_nationality("Finnish")
            self.db.add_language("Swedish")
            self.db.add_nationality("Swedish")
        except Exception as e:
            self.db.error("Something went wrong while adding templates for languages and nationalities: {}"
                          .format((error_handler(e, self.__class__.__name__))))
            pass
        # Add statuses
        try:
            self.db.debug("Adding Template Statuses.")
            active = dumps({
                "type": "active",
                "description": "Status is active."
            })
            paused = dumps({
                "type": "paused",
                "description": "Status is paused."
            })
            withdrawn = dumps({
                "type": "withdrawn",
                "description": "Status is withdrawn."
            })
            self.db.add_status(active)
            self.db.add_status(paused)
            self.db.add_status(withdrawn)
        except Exception as e:
            self.db.error("Something went wrong while adding templates for statuses: {}"
                          .format((error_handler(e, self.__class__.__name__))))
            pass

        # Add categories
        try:
            self.db.info("Adding Template Categories.")
            self.db.info("Adding Template Categories from Sources")
            for source in self.db.config["sources"]:
                source_categories = self.db.config["sources"][source]["categories"]
                for category in source_categories:
                    try:
                        cate = {
                            "name": category,
                            "description": "Category containing {}".format(category)
                        }
                        self.db.add_category(dumps(cate))
                    except Exception as e:
                        self.db.error("Error occurred while adding category '{}', Error:{} ".format(category, repr(e)))

            self.db.info("Adding Template Categories from Sinks")
            for sink in self.db.config["sinks"]:
                sink_categories = self.db.config["sinks"][sink]["categories"]
                for category in sink_categories:
                    try:
                        cate = {
                            "name": category,
                            "description": "Category containing {}".format(category)
                        }
                        self.db.add_category(dumps(cate))
                    except Exception as e:
                        self.db.error("Error occurred while adding category '{}', Error:{} ".format(category, repr(e)))

        except Exception as e:
            self.db.error("Something went wrong while adding templates for categories: {}"
                          .format((error_handler(e, self.__class__.__name__))))
            pass
        # Add labels
        try:
            self.db.debug("Adding Template Labels.")
            services = dict(self.db.config["sources"])
            services.update(self.db.config["sinks"])
            self.db.debug("Services we have:\n{}".format(services))
            for service in services:
                labels = services[service]["labels"]
                for label in labels:
                    try:
                        template = {
                            "name": label,
                            "description": "'{}' label".format(label)
                        }
                        self.db.add_label(dumps(template))
                    except Exception as e:
                        self.db.error("Something went wrong while adding templates for labels: {}"
                                      .format((error_handler(e, self.__class__.__name__))))

        except Exception as e:
            self.db.error("Something went wrong while adding templates for labels: {}"
                          .format((error_handler(e, self.__class__.__name__))))
            pass
        # Add license types
        try:  # TODO: Are the configs commonConsents same as license types?
            licenses = [{"type": x} for x in self.db.config["data_licenses"]
                        ]
            self.db.debug("Adding Template LicenseTypes.")
            for lis in licenses:  # TODO: More adding stuff like this, helps logging, helps avoiding repeating of code and stuff
                try:
                    self.db.add_licensetype(dumps(lis))
                except Exception as e:
                    self.db.error("Something went wrong while adding template license types: {}"
                                  .format((error_handler(e, self.__class__.__name__))))
        except Exception as e:
            self.db.error("Something went wrong while adding template license types: {}"
                          .format((error_handler(e, self.__class__.__name__))))
            pass

        # Add test user with name
        try:
            country_id = self.db.get_countries()[0].id
            region_id = self.db.get_regions_by_country(country_id)[0].id
            city_id = self.db.get_cities_by_region(region_id)[0].id
            self.db.debug("Adding Template User.")
            for user in self.db.config["operators"]["1"]["users"]:
                self.db.debug(dumps(user, indent=3))
                user_id = self.db.add_user(dumps(user))["id"]
                
                # TODO: Users need profile image.
                
        except Exception as e:
            self.db.error("Something went wrong while adding template user: {}"
                          .format((error_handler(e, self.__class__.__name__))))
            pass
        # Add userAccount for user
        try:
            self.db.debug("Adding Template userAccount.")  # TODO: Get from config
            userAccount = {"users_id": user_id,
                           "statuses_id": self.db.get_status_by_type("active").id,
                           "username": "testuser",
                           "password": "Hello",
                           "isAdmin": False
                           }
            self.db.debug("Adding Template 2 userAccount.")
            userAccount2 = {"users_id": user_id,
                            "statuses_id": self.db.get_status_by_type("active").id,
                            "username": "Testeri",
                            "password": "Hello",
                            "isAdmin": False
                            }
            self.db.register_userAccount(dumps(userAccount))
            self.db.register_userAccount(dumps(userAccount2))
        except Exception as e:
            self.db.error("Something went wrong while adding template userAccount: {}"
                          .format((error_handler(e, self.__class__.__name__))))
            pass
        # Add serviceTypes
        try:
            self.db.debug("Adding Template ServiceTypes.")
            self.db.add_servicetype(dumps({"type": "Source", "description": "DataSource"}))
            self.db.add_servicetype(dumps({"type": "Sink", "description": "DataSink"}))
            self.db.add_servicetype(dumps({"type": "Both", "description": "Both DataSink and DataSource"}))
        except Exception as e:
            self.db.error("Something went wrong while adding template serviceTypes: {}"
                          .format((error_handler(e, self.__class__.__name__))))
            pass
        # Add serviceTerms
        try:
            self.db.debug("Adding Template ServiceTerms.")
            self.db.add_serviceterm(dumps({"eula": "http://some.eula.com/"}))
            self.db.add_serviceterm(dumps({"eula": "http://some2.eula.com/"}))
            self.db.add_serviceterm(dumps({"eula": "http://some3.eula.com/"}))
        except Exception as e:
            self.db.error("Something went wrong while adding template serviceTerms: {}"
                          .format((error_handler(e, self.__class__.__name__))))
            pass
        # Add services
        try:
            self.db.debug("Adding Template Services.")
            sorted_keys_src = sorted(
                self.db.config["sources"].keys())  # We need these in order to ensure correct id's in DB
            sorted_keys_sink = sorted(
                self.db.config["sinks"].keys())  # We need these in order to ensure correct id's in DB

            def service_template_generator(info_path, keys_list, typpe=self.db.get_servicetype_by_type("Source").id):
                for key in keys_list:
                    service_info = info_path[key]
                    service_template = {
                        "statuses_id": self.db.get_status_by_type("active").id,
                        "name": service_info["name"],
                        "descriptionShort": service_info["description"]["desc_short"],
                        "descriptionLong": service_info["description"]["desc_long"],
                        "serviceTerms_id": self.db.get_serviceterms()[0].id,
                        # TODO: We need to get the eula url from somewhere
                        "serviceTypes_id": typpe,
                        "img_url_logo": service_info["description"]["img_url_logo"],
                        "img_url_banner": service_info["description"]["img_url_banner"],
                        "img_url_overview": service_info["description"]["img_url_overview"],
                        "ip_address": service_info["network"]["ip_public"],
                        "port_api": service_info["network"]["port_api"],
                        "data_api": service_info["network"].get("data_api", None)  # Sinks don't have this.
                    }
                    self.db.add_service(dumps(service_template))

            service_template_generator(self.db.config["sources"], sorted_keys_src)
            service_template_generator(self.db.config["sinks"], sorted_keys_sink, self.db.get_servicetype_by_type("Sink").id)

        except Exception as e:
            self.db.error("Something went wrong while adding template services: {}"
                          .format((error_handler(e, self.__class__.__name__))))
            pass

        try:
            services_src = dict(self.db.config["sources"])
            services = dict(self.db.config["sources"])
            services_sink = dict(self.db.config["sinks"])
            for service in services_src:
                ide = service
                info = services_src[ide]
                categories = info["categories"]
                labels = info["labels"]
                for category in categories:
                    try:
                        cat_id = self.db.get_category_by_name(category).id
                        template = {
                            "services_id": ide,
                            "categories_id": cat_id,
                            "value": 1
                        }
                        self.db.add_servicedata(dumps(template))
                    except Exception as e:
                        self.db.error("Something went wrong while adding template services: {}"
                                      .format((error_handler(e, self.__class__.__name__))))
                for label in labels:
                    try:
                        lab_id = self.db.get_label_by_name(label).id
                        template = {
                            "services_id": ide,
                            "labels_id": lab_id
                        }
                        self.db.add_labellink(dumps(template))
                    except Exception as e:
                        self.db.error("Something went wrong while adding labels services: {}"
                                      .format((error_handler(e, self.__class__.__name__))))

            for service in services_sink:
                ide = service
                info = services_sink[ide]
                categories = info["categories"]
                labels = info["labels"]
                for category in categories:
                    try:
                        cat_id = self.db.get_category_by_name(category).id
                        template = {
                            "services_id": ide,
                            "categories_id": cat_id,
                            "value": 1
                        }
                        self.db.add_servicedata(dumps(template))
                    except Exception as e:
                        self.db.error("Something went wrong while adding template services: {}"
                                      .format((error_handler(e, self.__class__.__name__))))
                for label in labels:
                    try:
                        lab_id = self.db.get_label_by_name(label).id
                        template = {
                            "services_id": ide,
                            "labels_id": lab_id
                        }
                        self.db.add_labellink(dumps(template))
                    except Exception as e:
                        self.db.error("Something went wrong while adding labels services: {}"
                                      .format((error_handler(e, self.__class__.__name__))))
        except Exception as e:
            self.db.error("Error occurred: {}".format((error_handler(e, self.__class__.__name__))))
            #  TODO: Add ServiceDatas and LabelLinks
