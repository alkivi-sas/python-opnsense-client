Lightweight wrapper around OPNSense API.


.. code:: python

    # -*- encoding: utf-8 -*-

    import opnsense

    client = opnsense.Client(
        endpoint='10.0.0.1',
        application_key='<api key>',
        application_secret='<api secret>',
        consumer_key='<consumer key>',
    )

    # Print nice welcome message
    print "Welcome", client.get('/core/firmware/status')
