# -*- coding: utf-8 -*-
'''!
@author Aleksi Palomäki
Defining the database scheme for sqlalchemy.
'''
from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, Boolean, UniqueConstraint, DATETIME
from base import Base
from json import dumps
from datetime import datetime
class Users(Base):
    '''document'''
    debug = False
    __tablename__ = "users"
    id = Column(Integer, primary_key=True )
    gender = Column(String(760), nullable=debug)
    statuses_id = Column(Integer, ForeignKey("statuses.id"), nullable=debug)
    firstName = Column(String(760), nullable=debug)
    lastName = Column(String(760), nullable=debug)
    email = Column(String(760), nullable=False, unique=True)
    address1 = Column(String(760), nullable=debug)
    address2 = Column(String(760), nullable=True)
    cities_id = Column(Integer, ForeignKey("cities.id"), nullable=debug)
    regions_id = Column(Integer, ForeignKey("regions.id"), nullable=debug)
    countries_id = Column(Integer, ForeignKey("countries.id"), nullable=debug)
    languages_id = Column(Integer, ForeignKey("languages.id"), nullable=debug)
    nationalities_id = Column(Integer, ForeignKey("nationalities.id"), nullable=debug)
    img_url_avatar = Column(String(760))
    created = Column(DATETIME, default=datetime.now())

    @property
    def tojson(self):
        creat = self.created
        if self.created is None:
            creat = datetime.now()
        js = {"id":self.id,
              "gender": self.gender,
              "statuses_id": self.statuses_id,
              "firstName": self.firstName,
              "lastName":self.lastName,
              "email": self.email,
              "address1": self.address1,
              "address2": self.address2,
              "cities_id": self.cities_id,
              "regions_id": self.regions_id,
              "countries_id": self.countries_id,
              "languages_id": self.languages_id,
              "nationalities_id": self.nationalities_id,
              "img_url_avatar": self.img_url_avatar,
              "created": creat.strftime('%d/%m/%Y-%X')}
        return dumps(js, indent=3)

class Statuses(Base):
    '''!
    @brief We store statuses here.'''
    __tablename__ = "statuses"
    id = Column(Integer, primary_key=True)
    type = Column(String(760), unique=True)
    description = Column(String(760))

    @property
    def tojson(self):
        js = {"id": self.id,
              "type": self.type,
              "description": self.description}
        return dumps(js, indent=3)

class Cities(Base):
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True)
    name = Column(String(760), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"))

    @property
    def tojson(self):
        js = {"id": self.id,
              "name": self.name,
              "region_id": self.region_id}
        return dumps(js, indent=3)

class Regions(Base):
    __tablename__ = "regions"
    __table_args__ = (UniqueConstraint('name', 'country_id', name='_region_country_uc'),)
    id = Column(Integer, primary_key=True)
    name = Column(String(760), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"))

    @property
    def tojson(self):
        js = {"id": self.id,
              "name": self.name,
              "country_id": self.country_id}
        return dumps(js, indent=3)

class Countries(Base):
    debug = False #false is on, True is off
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True)
    name = Column(String(760), unique=debug, nullable=False) # TODO: Change unique to true when ready.

    @property
    def tojson(self):
        js = {"id": self.id,
              "name": self.name}
        return dumps(js, indent=3)

class Nationalities(Base):
    debug = False #false is on, True is off
    __tablename__ = "nationalities"
    id = Column(Integer, primary_key=True)
    name = Column(String(760), unique=debug, nullable=False)

    @property
    def tojson(self):
        js = {"id": self.id,
              "name": self.name}
        return dumps(js, indent=3)

class Languages(Base):
    debug = False #false is on, True is off
    __tablename__ = "languages"
    id = Column(Integer, primary_key=True)
    name = Column(String(760), unique=debug, nullable=False)

    @property
    def tojson(self):
        js = {"id": self.id,
              "name": self.name}
        return dumps(js, indent=3)

class UserAccounts(Base):
    debug = False
    __tablename__ = "userAccounts"
    id = Column(Integer, primary_key=True)
    users_id = Column(Integer, ForeignKey("users.id"), nullable=debug)
    statuses_id = Column(Integer, ForeignKey("statuses.id"), nullable=debug)
    username = Column(String(760), nullable=debug, unique=True)
    password = Column(String(760), nullable=debug)
    accessToken = Column(String(760), nullable=True)
    isAdmin = Column(Boolean, nullable=debug)

    @property
    def tojson(self):
        js = {"id": self.id,
              "users_id": self.users_id,
              "statuses_id": self.statuses_id,
              "username": self.username,
              "password": self.password,
              "accessToken": self.accessToken,
              "isAdmin": self.isAdmin}
        return dumps(js, indent=3)

class Categories(Base):
    debug = False
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(760), unique=True, nullable=False)
    description = Column(String(760), unique=False, nullable=False)

    @property
    def tojson(self):
        js = {"id": self.id,
              "name": self.name,
              "description": self.description}
        return dumps(js, indent=3)

class ServiceTerms(Base):
    debug = False
    __tablename__ = "serviceTerms"
    id = Column(Integer, primary_key=True)
    eula = Column(String(760), unique=False, nullable=False)

    @property
    def tojson(self):
        js = {"id": self.id,
              "eula": self.eula}
        return dumps(js, indent=3)

class ServiceTypes(Base):
    debug = False
    __tablename__ = "serviceTypes"
    id = Column(Integer, primary_key=True)
    type = Column(String(760), unique=True, nullable=False)
    description = Column(String(760), unique=False, nullable=False)

    @property
    def tojson(self):
        js = {"id": self.id,
              "type": self.type,
              "description": self.description}
        return dumps(js, indent=3)

class Services(Base):
    debug = False
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    statuses_id = Column(Integer, ForeignKey("statuses.id"), nullable=debug)
    name = Column(String(760), unique=True, nullable=False)
    descriptionShort = Column(String(760), unique=False, nullable=debug)
    descriptionLong = Column(String(760), unique=False, nullable=debug)
    serviceTerms_id = Column(Integer, ForeignKey("serviceTerms.id"), nullable=debug)
    serviceTypes_id = Column(Integer, ForeignKey("serviceTypes.id"), nullable=debug)
    img_url_logo = Column(String(760))
    img_url_banner = Column(String(760))
    img_url_overview = Column(String(760))
    ip_address = Column(String(760))
    port_api = Column(String(760))
    data_api = Column(String(760), nullable=True) #  Sink doesn't have this for example


    @property
    def tojson(self):
        js = {"id": self.id,
              "statuses_id": self.statuses_id,
              "name": self.name,
              "descriptionShort": self.descriptionShort,
              "descriptionLong": self.descriptionLong,
              "serviceTerms_id": self.serviceTerms_id,
              "serviceTypes_id": self.serviceTypes_id,
              "img_url_logo": self.img_url_logo,
              "img_url_banner": self.img_url_banner,
              "img_url_overview": self.img_url_overview,
              "ip_address": self.ip_address
              }
        return dumps(js, indent=3)

class ServiceDatas(Base):
    debug = False
    __tablename__ = "serviceDatas"
    id = Column(Integer, primary_key=True)
    services_id = Column(Integer, ForeignKey("services.id"), nullable=debug)
    categories_id = Column(Integer, ForeignKey("categories.id"), nullable=debug)
    value = Column(Integer, nullable=debug)

    @property
    def tojson(self):
        js = {"id": self.id,
              "services_id": self.services_id,
              "categories_id": self.categories_id,
              "value": self.value}
        return dumps(js, indent=3)

class Labels(Base):
    debug = False
    __tablename__ = "labels"
    id = Column(Integer, primary_key=True)
    name = Column(String(760), unique=True, nullable=False)
    description = Column(String(760), unique=False, nullable=False)

    @property
    def tojson(self):
        js = {"id": self.id,
              "name": self.name,
              "description": self.description}
        return dumps(js, indent=3)

class LabelLinks(Base):
    debug = False
    __tablename__ = "labelLinks"
    id = Column(Integer, primary_key=True)
    services_id = Column(Integer, ForeignKey("services.id"), nullable=debug)
    labels_id = Column(Integer, ForeignKey("labels.id"), nullable=debug)

    @property
    def tojson(self):
        js = {"id": self.id,
              "services_id": self.services_id,
              "labels_id": self.labels_id}
        return dumps(js, indent=3)

class LicenseLinks(Base):
    debug = False
    __tablename__ = "licenselinks"
    id = Column(Integer, primary_key=True)
    sink_receipt_id = Column(Integer, ForeignKey("services.id"), nullable=debug)
    license_types_id = Column(Integer, ForeignKey("license_types.id"), nullable=debug)

    @property
    def tojson(self):
        js = {"id": self.id,
              "sink_receipt_id": self.services_id,
              "license_types_id": self.labels_id}
        return dumps(js, indent=3)


class Summaries(Base):
    debug = False
    __tablename__ = "summaries"
    id = Column(Integer, primary_key=True)
    data_source = Column(Integer, ForeignKey("services.id"), nullable=debug)
    data_sink = Column(Integer, ForeignKey("services.id"), nullable=debug)

    @property
    def tojson(self):
        js = {"id": self.id,
              "data_source": self.data_source,
              "data_sink": self.data_sink}
        return dumps(js, indent=3)

class LicenseTypes(Base):
    debug = False
    __tablename__ = "license_types"
    id = Column(Integer, primary_key=True)
    type = Column(String(760), unique=True, nullable=debug)

    @property
    def tojson(self):
        js = {"id": self.id,
              "type": self.type}
        return dumps(js, indent=3)

class ConsentReceiptsForSource(Base):
    debug = False
    __tablename__ = "consent_receipts_for_source"
    id = Column(Integer, primary_key=True)
    key_used_to_sign_rpt = Column(String(760), unique=debug, nullable=debug)
    rs_id = Column(String(760), unique=debug, nullable=debug)
    userAccount_id = Column(Integer, ForeignKey("userAccounts.id"), nullable=debug)
    authorization_status = Column(Integer, ForeignKey("statuses.id"), nullable=debug)
    consent_summary = Column(Integer, ForeignKey("summaries.id"), nullable=debug)

    @property
    def tojson(self):
        js = {"id": self.id,
              "key_used_to_sign_rpt": self.key_used_to_sign_rpt,
              "rs_id": self.rs_id,
              "userAccount_id": self.userAccount_id,
              "authorization_status": self.authorization_status,
              "consent_summary": self.consent_summary,
              }
        return dumps(js, indent=3)

class ConsentReceiptsForSink(Base):
    debug = False
    __tablename__ = "consent_receipts_for_sink"
    id = Column(Integer, primary_key=True)
    userAccount_id = Column(Integer, ForeignKey("userAccounts.id"), nullable=debug)
    rs_id = Column(String(760), unique=debug, nullable=debug)
    authorization_status = Column(Integer, ForeignKey("statuses.id"), nullable=debug)
    consent_summary = Column(Integer, ForeignKey("summaries.id"), nullable=debug)

    @property
    def tojson(self):
        js = {"id": self.id,
              "rs_id": self.rs_id,
              "userAccount_id": self.userAccount_id,
              "authorization_status": self.authorization_status,
              "consent_summary": self.consent_summary,
              }
        return dumps(js, indent=3)

class Contracts(Base):
    debug = False
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True)
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=debug)
    userAccount_id = Column(Integer, ForeignKey("userAccounts.id"), nullable=debug)
    services_id = Column(Integer, ForeignKey("services.id"), nullable=debug)
    created = Column(DATETIME, nullable=debug)
    serviceType = Column(Integer, ForeignKey("serviceTypes.id"), nullable=debug)
    legalRole = Column(String(760), nullable=debug)
    contract_terms = Column(String(760), nullable=debug)
    intended_use = Column(String(760), nullable=debug)
    validity_period = Column(String(760), nullable=debug)

    @property
    def tojson(self):
        creat = self.created
        if creat is None:
            creat = datetime.now()
        js = {"id": self.id,
              "status_id": self.status_id,
              "userAccount_id": self.userAccount_id,
              "services_id": self.services_id,
              "serviceType": self.serviceType,
              "created": creat.strftime('%d/%m/%Y'),
              "legalRole": self.legalRole,
              "contract_terms": self.contract_terms,
              "intended_use": self.intended_use,
              "validity_period": self.validity_period}
        return dumps(js, indent=3)

class ConsentReceiptsLinks(Base):
    debug = False
    __tablename__ = "consent_receiptsLinks"
    id = Column(Integer, primary_key=True)
    source_receipt = Column(Integer, ForeignKey("consent_receipts_for_source.id"), nullable=debug)
    sink_receipt = Column(Integer, ForeignKey("consent_receipts_for_sink.id"), nullable=debug)
    source_contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=debug)
    sink_contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=debug)

    @property
    def tojson(self):
        js = {"id": self.id,
              "source_receipt": self.source_receipt,
              "sink_receipt": self.sink_receipt,
              "source_contract_id": self.source_contract_id,
              "sink_contract_id": self.sink_contract_id}
        return dumps(js, indent=3)

class ContractDataTypes(Base):
    debug = False
    __tablename__ = "contractDataTypes"
    id = Column(Integer, primary_key=True)
    contracts_id = Column(Integer, ForeignKey("contracts.id"), nullable=debug)
    categories_id = Column(Integer, ForeignKey("categories.id"), nullable=debug)

    @property
    def tojson(self):
        js = {"id": self.id,
              "contracts_id": self.contracts_id,
              "categories_id": self.categories_id}
        return dumps(js, indent=3)

class SummaryDataTypes(Base):
    debug = False
    __tablename__ = "summaryDataTypes"
    id = Column(Integer, primary_key=True)
    summaries_id = Column(Integer, ForeignKey("summaries.id"), nullable=debug)
    categories_id = Column(Integer, ForeignKey("categories.id"), nullable=debug)

    @property
    def tojson(self):
        js = {"id": self.id,
              "summaries_id": self.services_id,
              "categories_id": self.categories_id}
        return dumps(js, indent=3)

class Ext_ids(Base):
    debug = False
    __tablename__ = "ext_ids"
    id = Column(Integer, primary_key=True)
    services_id = Column(Integer, ForeignKey("services.id"), nullable=debug)
    userAccounts_id = Column(Integer, ForeignKey("userAccounts.id"), nullable=debug)
    ext_id = Column(String(760), nullable=debug, unique=True)

    @property
    def tojson(self):
        js = {"id": self.id,
              "services_id": self.services_id,
              "userAccounts_id": self.userAccounts_id,
              "ext_id": self.ext_id}
        return dumps(js, indent=3)


class ResourceSets(Base):
    debug = False
    __tablename__ = "resourceSets"
    id = Column(Integer, primary_key=True)
    contracts_id = Column(Integer, ForeignKey("contracts.id"), nullable=debug)
    categories_id = Column(Integer, ForeignKey("categories.id"), nullable=debug)
    rs_id = Column(String(760), nullable=debug)

    @property
    def tojson(self):
        js = {"id": self.id,
              "contracts_id": self.contracts_id,
              "categories_id": self.categories_id,
              "rs_id": self.rs_id}
        return dumps(js, indent=3)
