import requests
from json import loads, dumps
from requests.auth import HTTPBasicAuth
auth = HTTPBasicAuth('testuser', 'Hello')
backend_ip = "http://127.0.0.1:8080"
sink_id = 4
source_id = 1
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("Blah")
info = logger.info
debug = logger.debug
error = logger.error


info("This UI emulator uses template JSON UI would send to the Backend and tests all the SRC&SINK API's")
login_src = {
    "service_id": source_id,
    "username": "datasource",
    "password": "dhroulu"
}
login_sink = {
    "service_id": sink_id,
    "username": "test",
    "password": "123456"
}
debug("Generated the following JSON for Source:\n{}\n\n and following JSON to Sink:\n{}".format
      (dumps(login_src, indent=3), dumps(login_sink, indent=3)))

info("Sending DataOperator backend login information for Source and excepting SCT back.")

# Foreign login: Login with Services Credentials --> Get ext_id (links Account Owner to specific user at the Service)
# ---> When DO-backend has ext_id it fetches SCT from api/v0.1/contract
# ---> Do-backend return SCT to DO-UI
request = requests.post(backend_ip+"/ui/foreign_login", json=login_src, auth=auth)
src_lg = loads(request.text)
if not request.__bool__():
    error("Failed to receive OK from Source")


info("Received Source SCT")
debug(src_lg)

info("Sending DataOperator backend login information for Sink and excepting SCT back.")

request = requests.post(backend_ip+"/ui/foreign_login", json=login_sink, auth=auth)
sink_lg = loads(request.text)
if not request.__bool__():
    error("Failed to receive OK from Sink")
    debug(sink_lg)
    exit()

info("Received Sink SCT")
debug(sink_lg)

info("Now UI can show the user the SCT(or interface to edit it somehow) and allow making some changes.")
info("Sending the 'accepted' versions of SCT back to services.")
# DO-UI accepts the SCT of a Service
src_accepted_contract = requests.post(backend_ip+"/ui/accept_contract", auth=auth, json=src_lg).text
info("Reply from Source:\n{}".format(src_accepted_contract))
sink_accepted_contract = requests.post(backend_ip+"/ui/accept_contract", auth=auth, json=sink_lg).text
debug("Reply from Sink:\n{}".format(sink_accepted_contract))

info("Now the Service Contracts has been made and we move on to selecting resources and a source to make ResourceSet")

rs_set_creation = {
                    "service_id": source_id,
                    "categories": ["Health", "Fitness"]
                    }
debug(rs_set_creation)

request = requests.post(backend_ip+"/protection/resourceSets", auth=auth, json=rs_set_creation)
debug(request.text)
rs_id = {"rs_id": loads(request.text)["rs_id"]}
info("Added ResourceSet to the Source successfully")
info("Now user can select Source gets to select the ResourceSet made and select Sink to give consent to it.")
cons = {
         "source_id": source_id,
         "sink_id": sink_id,
         "rs_id": rs_id,
         "usage_license": [1,2,3],
         "status": "active"
        }
# DO-UI Gives a Consent for this Source and this Sink
request = requests.post(backend_ip+"/ui/give_consent", auth=auth, json=cons)
debug(request.text)
