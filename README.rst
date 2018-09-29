Email Parser
===========
(Maintainer: ThreatLead)

Parses email, extracts attachment. Written to parse emails uploaded to VT.

Example:

.. code-block:: python

    >>> import emailparser
    >>> email_file = 'test.msg' or 'test.eml'
    >>> e = emailparser.parse(email_file)
    >>> print(vars(e))
    {'attachments': [AttachmentObject, ...],
     'body': ...,
     'receiver': ...,
     'sender': ...,
     'sha_256': ...,
     'subject': ...,
     'timestamp': datetimeObject
    }
    >>> a = e.attachments[0]
    >>> print(a.name)
    INVOICE_.zip
    >>> temp_folder = os.path.join(tempfile.gettempdir(), a.sha256))
    >>> print(a.unpack(outdir=temp_folder))
    ['/tmp/7cb1ea71c373c890d7a1c2e38f57fa3a862332c14798e58a569529c49573073e/document_copy.js']
    >>>
