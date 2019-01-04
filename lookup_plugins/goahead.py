from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
lookup: goahead
author: madonius <info@kampitakis.de>
version_added: "0.9"
short_description: query goahead for reboot
description:
    - This lookup returns a boolean describing whether a reboot/restart is required and safely possible
options:
  fqdn:
    description: requested service/server's fqdn
    required: True
  uptime:
    description: service/server's uptime
    required: True
  goahead_url:
    description: goahead service URL
    required: True
  goahead_url_ca_file:
    description: goahead service certificate file
    required: False
notes:
  - merely goahead is beeing queried. Local checks, eg. needrestart, still have to be done locally. 
"""

EXAMPLES = """
tasks:
  - debug:
      msg: "I may now reboot"
    until: "{{ lookup("goahead", fqdn=ansible_fqdn, goahead_url=goahead_service_url, goahead_url_ca_file=goahead_service_url_ca_file) }}"
    retries: 10
    delay: 60
    ignore_errors: yes
"""

RETURN = """
_raw:
  description: whether the server/service needs to and may be restarted
"""

import requests
import json
from ansible.plugins.lookup import LookupBase

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()


class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):
        should_restart = self.__request_reboot__(**kwargs, api_path="/v1/inquire/restart/")
        may_restart = self.__request_reboot__(**kwargs, api_path="/v1/inquire/restart/os")

        if should_restart:
            return should_restart
        else:
            return may_restart

    @staticmethod
    def __request_reboot__(fqdn, goahead_url, goahead_url_ca_file, api_path):
        """
         :param fqdn: requested service/server's fqdn
         :type fqdn: str
         :param goahead_url: goahead service URL
         :type goahead_url: str
         :param goahead_url_ca_file: goahead service certificate file
         :type goahead_url_ca_file: str
         :return: None
         """

        certificate_path = None
        goahead_inquiry = None

        if goahead_url_ca_file:
            certificate_path = goahead_url_ca_file

        goahead_payload = {
            'fqdn': fqdn,
            'uptime': uptime
        }

        try:
            goahead_inquiry = requests.get(
                url=goahead_url+api_path,
                verify=certificate_path,
                date=json.dumps(goahead_payload)
            )
        except Exception as (_, e):
            msg = (
                "Received error %s while contacting %s" % (e, goahead_url)
            )
            display.error(msg)
            return False

        return LookupModule.__validate_goahead(goahead_inquiry)

    @staticmethod
    def __validate_goahead(inquiry):
        """
        :param inquiry: Request towards goahead service
        :type inquiry: requests.models.Response
        :return: return validity
        :rtype: bool
        """

        expected_keys = (
            "error",
            "timestamp",
            "go_ahead",
            "unknown_host",
            "ask_again_in",
            "request_id",
            "found_cluster",
            "requesting_fqdn",
            "message"
        )

        if inquiry.status_code != requests.codes.ok:
            msg = (
                "Received status code %s" % goahead_inquiry.status_code
            )
            display.warning(msg)
            return False

        try:
            inquiry = inquiry.json()
        except json.JSONDecodeError as (_, e):
            msg = (
                "The API did not return valid json:\n %s" % e
            )
            display.warning(msg)
            return False

        if not set(expected_keys) < set(inquiry.keys()):
            msg = (
                "Expected API dictionary keys %s \n" % (",".join(expected_keys)),
                "are not a subset of the returned keys %s \n" % (",".join(inquiry.keys()))
            )
            display.warning(msg)
            return False

        if inquiry['unknown_host']:
            msg = (
                "The host %s is not known to the server" % inquiry['requesting_fqdn']
            )
            display.warning(msg)

        return inquiry['go_ahead']
