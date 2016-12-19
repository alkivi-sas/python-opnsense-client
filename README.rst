Lightweight wrapper around OPNSense API.

Inspired from https://github.com/ovh/python-ovh

.. code:: python

    # -*- encoding: utf-8 -*-

    import opnsense

    client = opnsense.Client(
        endpoint='10.0.0.1',
        application_key='<api key>',
        application_secret='<api secret>',
    )

    # Print nice welcome message
    print "Welcome", client.get('/core/firmware/status')
