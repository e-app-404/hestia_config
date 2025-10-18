# RESTFul API Support
AppDaemon supports a simple RESTFul API to enable arbitrary HTTP connections to pass data to Apps and trigger actions via GET or POST requests. API Calls can be anything, and the response will be JSON encoded. The RESTFul API is disabled by default, but is enabled by setting up the http component in the configuration file. The API can run http or https if desired, separately from the dashboard.

To call into a specific App, construct a URL, use the regular AppDaemon URL, and append /api/appdaemon, then add the name of the endpoint as registered by the App on the end, for example:

`http://192.168.1.20:5050/api/appdaemon/hello_endpoint`
This URL will call into an App that registered an endpoint named hello_endpoint.

Within the App, a call must be made to register_endpoint() to tell AppDaemon that the App is expecting calls on that endpoint. When registering an endpoint, the App supplies a function to be called when a request comes into that endpoint and an optional name for the endpoint. If not specified, the name will default to the name of the App as specified in the configuration file.

Apps can have as many endpoints as required, however, the names must be unique across all of the Apps in an AppDaemon instance.

It is also possible to remove endpoints with the deregister_endpoint() call, making the endpoints truly dynamic and under the control of the App.

Here is an example of an App using the API:

```
from appdaemon.plugins.hass import Hass


class API(Hass):
    def initialize(self):
        self.register_endpoint(my_callback, "test_endpoint")

    def my_callback(self, json_obj, **kwargs):
        self.log(json_obj)

        response = {"message": "Hello World"}

        return response, 200
```

The callback will accept GET or POST requests. If the request is a POST AppDaemon will attempt to decode JSON arguments and supply them in the args parameter. If the method is GET, any arguments will also be supplied via the args parameter. **kwargs will be supplied with any parameters defined at the time of the register_endpoint().

The response must be a python structure that can be mapped to JSON, or can be blank, in which case specify "" for the response. You should also return an HTML status code, that will be reported back to the caller, 200 should be used for an OK response.

As well as any user specified code, the API can return the following codes:

- 400 - JSON Decode Error
- 401 - Unauthorized
- 404 - App not found
- 500 - Internal Server Error

Below is an example of using curl to call into the App shown above:

```
$ curl -i -X POST -H "Content-Type: application/json" http://192.168.1.20:5050/api/appdaemon/test_endpoint -d '{"type": "Hello World Test"}'
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 26
Date: Sun, 06 Aug 2017 16:38:14 GMT
Server: Python/3.5 aiohttp/2.2.3

{"message": "Hello World"}hass@Pegasus:~$
```
