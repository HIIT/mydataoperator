__author__ = 'Aleksi'
import json
'''Storage for some templates used'''

#Some of these are not even supposed to work like they are written.
def Template_tests(self):
    variable_list = {}
    variable_list2 = {}
    object_name = "Template"
    self.info("Running tests on '"+currentframe().f_code.co_name+"' for class Basic")
    self.info("Creating "+object_name+" object 1.")
    Object = Templates(**variable_list)
    self.info("Creating "+object_name+" object 2.")
    Object2 = Templates(**variable_list2)
    self.info(object_name+" 1 with id {} in JSON:\n".format(Object.id)+Object.tojson+
              "\n"+object_name+" 2 with id {} in JSON:\n".format(Object2.id)+Object2.tojson)
    try:
        self.info("Adding "+object_name+" to the Database.")
        self.db.add_template(Object.tojson)
    except Exception as e:
        self.db.delete_template(Object.id)
        self.db.add_template(Object.tojson)
    templates = self.db.get_templates()
    self.info("Printing out all nationalities in DB.")
    for x in templates:
        self.info("\n"+x.tojson)
    Object = templates[-1]
    self.info("Testing fetching "+object_name+" based on id and showing its info as JSON:\n"
              + self.db.get_template(Object.id).tojson)
    self.info("Testing fetching another "+object_name+" which hasn't been added yet.")
    self.db.get_template(Object2.id)
    self.info("Testing deleting "+object_name+" with id {}".format(Object.id))
    self.db.delete_template(Object.id)
    self.info("Testing fetching "+object_name+" who we just deleted with id {}".format(Object.id))
    self.db.get_template(Object.id)

myServices_dummy_json = '''
{
"1":{
    "category": [
"sports",
"health"
],
    "connections": {
        "ReceivingData": {
"Sink_name": {
"serviceID": "1234",
"img_url_logo": "http://url.to.something/logo.png",
"description": {
"short": "Short and compact description"
},
"consentActive": "True"
}
},
"DataShared": {
"Source_name": {
"serviceID": "1234",
"img_url_logo": "http://url.to.something/logo.png",
"description": {
"short": "Short and compact description"
},
"consentActive": "True"
}
}
}
},
"2":{
    "category": [
"food"
],
    "connections": {
        "ReceivingData": {
"Sink_name": {
"serviceID": "1234",
"img_url_logo": "http://url.to.something/logo.png",
"description": {
"short": "Short and compact description"
},
"consentActive": "False"
}
},
"DataShared": {
"Source_name": {
"serviceID": "1234",
"img_url_logo": "http://url.to.something/logo.png",
"description": {
"short": "Short and compact description"
},
"consentActive": "False"
}
}
}
}
}

'''
'''

{"sink": {
      "name": "Polar",
      "service_id": "id",
      "img_url_logo": "logourl.png",
      "licenses": ["list","of","licenses"],
      "selected_licenses": ["list of licenses"]
       },
"source":{
      "name": "FitMeals",
      "service_id": "id",
      "img_url_logo": "logourl.png",
      "categories":[
              ["Nutritional Information",Vitamin Information"],
              ["Nutritional Information",Caloric values of meal"],
              ["Health"],
              ["Fitness", "Running", "Distance"],
              ["Fitness", "Running", "Speed"]
                     ],
              "Meal information":
                     {
                     "Delivery intervals": "True"
                     }
                   }
          }
}





'''