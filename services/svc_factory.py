""" So you wanna add a service? These instructions should help you get started:
1.First thing first, update your my_cfg.py file to include the API keys or DB keys
    a.Follow the format in my_cfg_example.py when adding your keys
    b.Update my_cfg_example.py to include generic data so others can see what other services have been added
2.Next in our_envs.py add the base url to LOCALHOST, STAGING, and PROD in alphabetical order
3.Add Host to env_enums.py
4.Add your service to std_env.py in alphabetical order
    a.For services with credentials
        i.Add to the first part of prep_common_services
    b.Add service to svc_factory.add_service
5.Add new service method to svc_factory.py
6.Create service file under the services folder
    a.All service classes must contain a def teardown method
"""
import traceback

import imap_svc
import tracker_svc
import recorder_svc
import wikipedia_svc


class ServiceFactory(object):
    """Factory for creating service instances."""

    def __init__(self, data_builder):
        self.data_builder = data_builder
        self.generated_services = []
        self.service_data = {}
        self.tracker = None

    def add_service(self, name, **kwargs):
        self.service_data[name] = kwargs

    def teardown_all(self):
        """Performs a teardown of all services created by the factory."""
        print "----------Begin Service Teardown----------"
        teardown_success = True

        for service in reversed(self.generated_services):
            try:
                print "Tearing down: %s VVVVVVVVVVVVV" % repr(service)
                teardown_success = teardown_success and service.teardown()
            except Exception, exc:
                teardown_success = False
                traceback.print_exc()
        print "-----------End Service Teardown-----------"
        assert teardown_success, "Teardown steps within some services encountered errors. (See above teardown output)"

    def publish_to_all(self, pubsub_item, **kwargs):
        print "Publishing", pubsub_item, "with", kwargs

        for service in self.generated_services:
            callable = service.pubsub_items.get(pubsub_item, None)
            if callable:
                callable(**kwargs)

    def _remember_service(self, service):
        service.factory = self
        print "Creating %s" % repr(service)
        self.generated_services.append(service)
        return service

    # This method gives the user the ability to overwrite the default our_envs value for the current environment.
    # if the parameter writes_allowed passed into this function is None it will use the default from our_envs
    # however supplying True or False will use those values instead.
    # Ex:
    #       make_abyss_svc(writes_allowed=True)
    def _choose_writes_allowed(self, svc_name, writes_allowed=None):
        if writes_allowed is not None:
            return writes_allowed
        else:
            return self.service_data[svc_name]["writes_allowed"]

    def _choose_user(self, svc_name, user=None):
        if user is not None:
            return user
        else:
            return self.service_data[svc_name]["user"]

    def _choose_password(self, svc_name, password=None):
        if password is not None:
            return password
        else:
            return self.service_data[svc_name]["password"]

    def make_email_svc(self, user=None, password=None, writes_allowed=True):
        """Generates a new IMAP E-mail Service."""
        email_svc = imap_svc.MailBox(self.service_data["email"]["base_url"],
                                     self.service_data["email"]["port"],
                                     self._choose_user("email", user),
                                     self._choose_password("email", password),
                                     self._choose_writes_allowed("email", writes_allowed))
        return self._remember_service(email_svc)

    def make_recorder_svc(self, auto, writes_allowed=None):
        self.recorder = recorder_svc.StubRecorderSvc(auto,
            None,  # self.service_data["recorder"]["base_url"],
            None,  # self.service_data["recorder"]["verbose"],
            self._choose_writes_allowed("recorder", writes_allowed))
        return self._remember_service(self.recorder)

    def make_tracker(self, auto, recorder_svc):
        self.tracker = tracker_svc.TrackerSvc(auto, recorder_svc,
                [tracker_svc.WriteAsYouGo,
                ],
                self.service_data["tracker"]["additions"],
                self.service_data["tracker"]["subtractions"]
                )
        return self._remember_service(self.tracker)

    def make_wikipedia_svc(self, writes_allowed=True):
        """Generates a new Wikipedia API Service."""
        wiki_svc = wikipedia_svc.WikipediaService(self.service_data["wikipedia_api"]["base_url"],
                                     self._choose_writes_allowed("wikipedia_api", writes_allowed))
        return self._remember_service(wiki_svc)


