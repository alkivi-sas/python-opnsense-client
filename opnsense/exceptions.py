# -*- encoding: utf-8 -*-

"""
All exceptions used in OPNSense SDK derives from `APIError`
"""


class APIError(Exception):
    """Base OPNSense API exception."""

    def __init__(self, *args, **kwargs):
        self.response = kwargs.pop('response', None)
        if self.response is not None:
            self.query_id = self.response.headers.get("X-OPNSense-QUERYID")
        else:
            self.query_id = None
        super(APIError, self).__init__(*args, **kwargs)

    def __str__(self):
        if self.query_id:
            error = super(APIError, self).__str__()
            return "{} \nOPNSense-Query-ID: {}".format(error, self.query_id)
        else:
            return super(APIError, self).__str__()
