import base64
import requests
from requests.exceptions import Timeout
import json
import datetime
from sigfoxapiv2.helper import make_sigfox_url, try_add_optional_arg
from enum import Enum


class CallbackChannel(str, Enum):
    URL = ("URL",)
    BatchURL = ("BATCH_URL",)
    Email = "EMAIL"


class HTTPMethod(str, Enum):
    Get = ("GET",)
    Put = ("PUT",)
    Post = "POST"


class CallbackType(Enum):
    Data = 0
    Service = 1
    Error = 2


class CallbackSubtype(Enum):
    Status = 0
    GeoLocation = 1
    Uplink = (2,)
    Bidirectional = (3,)
    Acknowledge = (4,)
    Repeater = (5,)
    DataAdvanced = 6


class Sigfox:
    """
    API wrapper functions to query SigFox backend using the newer
    V2 API
    """

    def __init__(self, user, password):
        self.user = user
        self.passwd = password
        self._timeout = (3.05, 27)

    @property
    def timeout(self):
        # Gets requests.timeout tupple(connect, response)
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        # Sets requests.timeout tupple(connect, response)
        s = "expected a tuple(connect_T, repsonse_T) of types: (float, int)"
        assert isinstance(value, tuple), s
        assert isinstance(value[0], float), s
        assert isinstance(value[1], int), s
        self._timeout = value


    # ====================================
    #
    #   Helper functions
    #
    # ====================================

    def _make_auth_header(self):
        """
        Creates an auth header using the user and pass provided
        :return: dict that is the auth header
        """
        auth_str = "{}:{}".format(self.user, self.passwd).encode("utf-8")
        user_pass = base64.b64encode(auth_str).decode("ascii")
        auth_header = "Authorization:Basic {}".format(user_pass).split(":")
        return {auth_header[0]: auth_header[1]}

    def _make_api_post(self, url: str, payload: dict):
        """
        Send PUT request to Sigfox backend API endpoint
        :param url:  API endpoint RESTful request URL
        :param payload:  The JSON to send to the Sigfox backend
        :return: json response data
        """
        # Create headers
        headers = self._make_auth_header()
        headers["Content-type"] = "application/json"
        headers["Accept"] = "application/json"

        # Make request
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=self.timeout)
            data = None
            if response.content:
                data = json.loads(response.content)
            return response.status_code, data
        except Timeout:
            return 408, {"error": "Sigfox.server - POST request timeout"}

    def _make_api_put(self, url: str, payload: dict):
        """
        Send PUT request to Sigfox backend API endpoint
        :param url:  API endpoint RESTful request URL
        :param payload:  The JSON to send to the Sigfox backend
        :return: json response data
        """
        # Create headers
        headers = self._make_auth_header()
        headers["Content-type"] = "application/json"
        headers["Accept"] = "application/json"

        # Make request
        try:
            response = requests.put(url, headers=headers, data=json.dumps(payload), timeout=self.timeout)
            data = None
            if response.content:
                data = json.loads(response.content)
            return response.status_code, data
        except Timeout:
            return 408, {"error": "Sigfox.server - PUT request timeout"}

    def _make_api_get(self, url: str):
        """
        Send GET request to Sigfox backend API endpoint
        :param url:  API endpoint RESTful request URL
        :return: json response data
        """
        try:
            response = requests.get(url, headers=self._make_auth_header(), timeout=self.timeout)
            data = None
            if response.content:
                data = json.loads(response.content)
            return response.status_code, data
        except Timeout:
            return 408, {"error": "Sigfox.server - GET request timeout"}

    # ====================================
    #
    #   Sigfox Device Endpoint
    #
    # ====================================

    def get_device_types(self):
        """
        Get all the device types registerted on the Sigfox backend
        :return: json response containing device types
        """
        return self._make_api_get(make_sigfox_url("/device-types"))

    def get_device(self, device_id: str):
        """
        Retrieve information about a given device
        https://support.sigfox.com/apidocs#operation/getDevice
        :param device_id The ID of the Sigfox device
        :return: json response containing device data
        """
        return self._make_api_get(make_sigfox_url("/devices/{deviceid}", fargs={"deviceid": device_id}))

    def get_devices(self, device_type_id: str):
        """
        Gets all the devices of a particular device type
        /devices/ endpoint
        https://support.sigfox.com/apidocs#operation/listDevices
        :param device_type_id The ID of the Sigfox device type
        :return: json response containing devices of the device type
        """
        return self._make_api_get(make_sigfox_url("/devices?deviceTypeId={sfid}", fargs={"sfid": device_type_id}))

    def get_device_messages(self, device_id: str, since: datetime.datetime = None):
        """
        Gets all the devices of a particular device type
        /devices/{id}/messages/ endpoint
        https://support.sigfox.com/apidocs#operation/getDeviceMessagesListForDeviceType
        :param device_type_id The ID of the Sigfox device type
        :param since The time to get the messages since
        :return: json response containing device messages
        """
        if since:
            return self._make_api_get(
                make_sigfox_url(
                    "/devices/{sfid}/messages?since={timestamp}", fargs={"sfid": device_id, "timestamp": since}
                )
            )
        return self._make_api_get(make_sigfox_url("/devices/{sfid}/messages", fargs={"sfid": device_id}))

    def create_device(self, id: str, name: str, device_type_id: str, pac_code: str):
        """
        Creates a new Sigfox device.
        https://support.sigfox.com/apidocs#operation/createDevice
        :param device_id The device's identifier (hexadecimal format)
        :param name The device's name, can be custom
        :param device_type_id The ID of the type of device
        :param pac_code The device's PAC (Porting Access Code)
        :return: json response containing new id
        """
        payload = {"id": id, "name": name, "deviceTypeId": device_type_id, "pac": pac_code}
        return self._make_api_post(make_sigfox_url("/devices"), payload)

    def bulk_create_devices(self, device_type_id: str, device_list: list):
        """
        Create multiple new devices with asynchronous job
        https://support.sigfox.com/apidocs#operation/createBulkDevice
        :param device_type_id The device's identifier (hexadecimal format)
        :param device_list Devices to add with format [{"id": "<sigfox_id>", "pac": <pac string>, "name": "<name string>"}
        :return: json response containing new id
        """
        payload = {"deviceTypeId": device_type_id, "data": device_list}
        return self._make_api_post(make_sigfox_url("/devices"), payload)

    def update_device(
        self, id, name: str = None, latitude: str = None, longitude: str = None, certificate: str = None
    ):
        """
        Updates an exsisting Sigfox device.
        https://support.sigfox.com/apidocs#operation/updateDevice
        :param id The device's identifier (hexadecimal format) to update
        :param latitude The new latitude of the device
        :param longitude The new longitude of the device
        :param certificate The certificate name
        :return: json response 
        """
        payload = {}
        payload = try_add_optional_arg(payload, "name", name)
        payload = try_add_optional_arg(payload, "lat", latitude)
        payload = try_add_optional_arg(payload, "lng", longitude)
        if certificate is not None:
            payload["productCertificate"] = {"key": certificate}
        return self._make_api_put(make_sigfox_url("/devices/{}", fargs={"sfid": id}), payload)

    def bulk_update_devices(self, device_list: list):
        """
        Update Sigfox devices in bulk
        https://support.sigfox.com/apidocs#operation/deviceBulkEditAsync
        :param device_list List containing sigfox devices to update eg [{"id": "0FD32", name: "abc"}, etc]
        :return: json response containing number of devices being updated
        """
        payload = {"data": device_list}
        return self._make_api_put(make_sigfox_url("/devices/bulk"), payload)

    def transfer_device(
        self, new_device_type_id: str, device_id: list, keep_history: bool = True, activable: bool = True
    ):
        """
        Transfer a device to another device type
        https://support.sigfox.com/apidocs#operation/deviceBulkTransfer
        :param new_device_type_id The device type where new devices will be transfered
        :param device_id The sigfox id of the device
        :param keep_history_for_all Whether to keep the device history or not
        :param activable_for_all True if all the devices are activable and can take a token. Not used if the device has already a token and if the transferred is intra-order.
        :return: json response containing "total" number of devices being transfered and the "jobId"
        """
        return self.bulk_transfer_devices(new_device_type_id, [device_id], keep_history, activable)

    def bulk_transfer_devices(
        self,
        new_device_type_id: str,
        device_list: list,
        keep_history_for_all: bool = True,
        activable_for_all: bool = True,
    ):
        """
        Transfer multiple devices to another device type
        https://support.sigfox.com/apidocs#operation/deviceBulkTransfer
        :param new_device_type_id The device type where new devices will be transfered
        :param device_list A list of devices to transfer using the format EG [{"id": "<sigfox id>"}] or  [{"id": "133FE31", "activable": false, "keepHistory": true}]
        :param keep_history_for_all Whether to keep all of the devices histories or not
        :param activable_for_all True if all the devices are activable and can take a token. Not used if the device has already a token and if the transferred is intra-order.
        :return: json response containing "total" number of devices being transfered and the "jobId"
        """
        if keep_history_for_all:
            for device in device_list:
                device["keep_history"] = True
        if activable_for_all:
            for device in device_list:
                device["activable"] = True
        payload = {"deviceTypeId": new_device_type_id, "data": device_list}
        return self._make_api_post(make_sigfox_url("/devices/bulk/transfer"), payload)

    # ====================================
    #
    #   Sigfox Device Types Endpoint
    #
    # ====================================
    def create_device_type_callback(
        self,
        id: str,
        callback_channel: CallbackChannel,
        callback_type: CallbackType,
        callback_subtype: CallbackSubtype,
        is_enabled: bool,
        url: str,
        http_method: HTTPMethod,
        headers: str = None,
        body_template: str = None,
        content_type: str = None,
    ):
        """
        Creates a callback for a device type
        https://support.sigfox.com/apidocs#operation/createCallback
        :param id The device type identifier (hexadecimal format) to add a callback
        :param callback_channel The callback's channel, "URL", "BATCH_URL", or EMAIL"
        :param callback_type The callback's type, 0 for DATA, 1 for SERVICE, 2 for ERRROR
        :param callback_subtype The callback's subtype, 0 for STATUS, 1 for GEOLOC, 2 for UPLINK, 3 for BIDIR (bidirectional), 4 for ACKNOWLEDGE, 5 for REPEATER, 6 for DATA_ADVANCED
        :param is_enabled True to enable the callback, otherwise false
        :param url The callback's url
        :param http_method The http method used to send a callback, "GET", "PUT", or "POST"
        :param headers The headers of the http request to send, as an object with key:value.
        :param body_template The body template of the request, eg "{id: {id}}
        :param content_type The body media type of the request, eg "application/json"
        :return: json containing an "id" field of the newly created callback ID
        """
        payload = {
            "channel": callback_channel,
            "callbackType": callback_type,
            "callbackSubtype": callback_subtype,
            "is_enabled": is_enabled,
            "url": url,
            "http_method": http_method,
        }
        try_add_optional_arg(payload, "headers", headers)

        # HTTP POST and HTTP PUT require the callback to have a body and content type
        if http_method == "POST" or http_method == "PUT":
            if body_template is None or content_type is None:
                # To do: Throw an error
                pass
            else:
                try_add_optional_arg(payload, "bodyTemplate", body_template)
                try_add_optional_arg(payload, "contentType", content_type)

        return self._make_api_post(make_sigfox_url("/device_types/{}/callbacks", fargs={"id": id}), payload)

    def update_device_type_callback(
        self,
        id: str,
        callback_id: str,
        callback_channel: CallbackChannel,
        callback_type: CallbackType,
        callback_subtype: CallbackSubtype,
        is_enabled: bool,
        url: str,
        http_method: HTTPMethod,
        headers: str = None,
        body_template: str = None,
        content_type: str = None,
    ):
        """
        Updates a callback for a device type
        https://support.sigfox.com/apidocs#operation/createCallback
        :param id The device type identifier (hexadecimal format) to update the callback for
        :param callback_id The callback identifier
        :param callback_channel The callback's channel, "URL", "BATCH_URL", or EMAIL"
        :param callback_type The callback's type, 0 for DATA, 1 for SERVICE, 2 for ERRROR
        :param callback_subtype The callback's subtype, 0 for STATUS, 1 for GEOLOC, 2 for UPLINK, 3 for BIDIR (bidirectional), 4 for ACKNOWLEDGE, 5 for REPEATER, 6 for DATA_ADVANCED
        :param is_enabled True to enable the callback, otherwise false
        :param url The callback's url
        :param http_method The http method used to send a callback, "GET", "PUT", or "POST"
        :param headers The headers of the http request to send, as an object with key:value.
        :param body_template The body template of the request, eg "{id: {id}}
        :param content_type The body media type of the request, eg "application/json"
        :return: json containing an "id" field of the newly created callback ID
        """
        payload = {}
        try_add_optional_arg(payload, "channel", callback_channel)
        try_add_optional_arg(payload, "callbackType", callback_type)
        try_add_optional_arg(payload, "callback_subtype", callback_subtype)
        try_add_optional_arg(payload, "is_enabled", is_enabled)
        try_add_optional_arg(payload, "url", url)
        try_add_optional_arg(payload, "http_method", http_method)
        try_add_optional_arg(payload, "headers", headers)

        # HTTP POST and HTTP PUT require the callback to have a body and content type
        if http_method == "POST" or http_method == "PUT":
            if body_template is None or content_type is None:
                # To do: Throw an error
                pass
            else:
                try_add_optional_arg(payload, "bodyTemplate", body_template)
                try_add_optional_arg(payload, "contentType", content_type)

        return self._make_api_put(
            make_sigfox_url("/device_types/{id}/callbacks/{callbackId}", fargs={"id": id, "callbackId": callback_id}),
            payload,
        )

    def get_device_type_callbacks(self, device_type_id: str):
        """
        Gets all the device callbacks of a particular type
        /device-types/{id}/callbacks/ endpoint
        https://support.sigfox.com/apidocs#operation/listCallbacks
        :param device_type_id The ID of the Sigfox device type
        :return: json response containing device type callbacks
        """
        return self._make_api_get(make_sigfox_url("/device-types/{sfid}/callbacks", fargs={"sfid": device_type_id}))

    def get_device_type_list(self, name: str = None):
        """
        Retrieve a list of device types according to visibility permissions and request filters.
        https://support.sigfox.com/apidocs#operation/listDeviceTypes
        :param name Search returns all Device Type names containing the value. Example: ?name=sig
        :return: json response containing device type information
        """
        if name is not None:
            return self._make_api_get(make_sigfox_url("/device-types?name={name}", fargs={"name": name}))
        return self._make_api_get(make_sigfox_url("/device-types"))

    def create_device_type(
        self, name: str, group_id: str, contracts: str, geoloc_payload_config_id: str, description: str = None
    ):
        """
        Create a new device type
        https://support.sigfox.com/apidocs#operation/listDeviceTypes
        :param name The device type's name
        :param group_id The device type's group identifier
        :param contracts The device type's contract identifiers
        :param geoloc_payload_config_id The geoloc payload configuration identifier. Required if the payload type is Geolocation, else ignored.
        :param description The device type's description
        :return: json response containing the newly created device type id
        """
        payload = {
            "id": id,
            "name": name,
            "group_id": group_id,
            "contracts": contracts,
            "geoloc_payload_config_id": geoloc_payload_config_id,
        }
        try_add_optional_arg(payload, "description", description)
        return self._make_api_post(make_sigfox_url("/devices"), payload)

    # ====================================
    #
    #   Sigfox contract endpoint
    #
    # ====================================

    def get_contract_information(self):
        """
        Retrieve a list of Sigfox Device contracts
        :return: json response containing contracts
        """
        return self._make_api_get(make_sigfox_url("/contract-infos"))
