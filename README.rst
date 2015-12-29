taskcluster-util-python
=======================
.. image:: https://travis-ci.org/askeing/taskcluster-util-python.svg
    :target: https://travis-ci.org/askeing/taskcluster-util-python

Python `Taskcluster <http://docs.taskcluster.net/>`_ Utilities.


Installation
------------

To install **taskcluster_util**, simply:

.. code-block:: bash

    $ pip install -U taskcluster_util


Tools Usages
------------

Temporary Credentials
+++++++++++++++++++++

You can get your temporary credentials from https://auth.taskcluster.net/ (using Persona with LDAP account).

The temporary credentials will remain valid for 31 days.

Or you can just run **taskcluster_login** to get your credentials. (Note: it will remove your old credentials file.)

tc_credentials.json
~~~~~~~~~~~~~~~~~~~

You can put the credentials into **tc_credentials.json** file under your home folder.

.. code-block:: bash

    $ <YOUR_EDITOR> ~/tc_credentials.json

The file format will be:

.. code-block::

    {
        "clientId": "<YOUR_CLIENTID>",
        "accessToken": "<YOUR_ACCESSTOKEN>",
        "certificate": <YOUR_CERTIFICATE>
    }

Here's a simple example:

.. code-block::

    {
        "clientId": "foo-XXX",
        "accessToken": "hello-world-XXX",
        "certificate": {"version":1,"scopes":["*"],"start":1,"expiry":9,"seed":"hello","signature":"world="}
    }


taskcluster_download
++++++++++++++++++++

Download artifacts from command line.

.. code-block:: bash

    usage: taskcluster_download [-h] [--credentials CREDENTIALS]
                                (-n NAMESPACE | -t TASK_ID) [-a ARITFACT_NAME]
                                [-d DEST_DIR] [-v]

    The simple download tool for Taskcluster.

    optional arguments:
      -h, --help            show this help message and exit
      --credentials CREDENTIALS
                            The credential JSON file
                            (default: <YOUR_HOME>/tc_credentials.json)
      -n NAMESPACE, --namespace NAMESPACE
                            The namespace of task
      -t TASK_ID, --taskid TASK_ID
                            The taskId of task
      -v, --verbose         Turn on verbose output, with all the debug logger.

    Download Artifact:
      The artifact name and dest folder

      -a ARITFACT_NAME, --artifact ARITFACT_NAME
                            The artifact name on Taskcluster
      -d DEST_DIR, --dest-dir DEST_DIR
                            The dest folder (default: current working folder)
      -u, --signed-url-only
                            Retrieve the signed url and display it.
                            No download is done.

    The tc_credentials.json Template:
        {
            "clientId": "",
            "accessToken": "",
            "certificate": {
                "version":1,
                "scopes":["*"],
                "start":xxx,
                "expiry":xxx,
                "seed":"xxx",
                "signature":"xxx"
            }
        }


taskcluster_traverse
++++++++++++++++++++

Travese namespace and download artifacts from GUI.

.. code-block:: bash

    usage: taskcluster_traverse [-h] [--credentials CREDENTIALS] [-n NAMESPACE]
                                [-d DEST_DIR] [-v]

    The simple GUI traverse and download tool for Taskcluster.

    optional arguments:
      -h, --help            show this help message and exit
      --credentials CREDENTIALS
                            The credential JSON file
                            (default: <YOUR_HOME>/tc_credentials.json)
      -n NAMESPACE, --namespace NAMESPACE
                            The namespace of task
      -d DEST_DIR, --dest-dir DEST_DIR
                            The dest folder (default: current working folder)
      -v, --verbose         Turn on verbose output, with all the debug logger.

    The tc_credentials.json Template:
        {
            "clientId": "",
            "accessToken": "",
            "certificate": {
                "version":1,
                "scopes":["*"],
                "start":xxx,
                "expiry":xxx,
                "seed":"xxx",
                "signature":"xxx"
            }
        }


taskcluster_login
+++++++++++++++++

Login Taskcluster, get Temporary Credentials, and save to home directory.

.. code-block:: bash

    usage: taskcluster_login [-h] [-a ADDRESS] [-p PORT] [--file CREDENTIALS_FILE]
                             [-v]

    The simple login tool for Taskcluster.

    optional arguments:
      -h, --help            show this help message and exit
      -a ADDRESS, --address ADDRESS
                            Specify the server address. (default: localhost)
      -p PORT, --port PORT  Specify the server port. (default: 0)
      --file CREDENTIALS_FILE
                            The credentials file. It will be overwritten if it
                            already exist. (default:
                            /Users/Askeing/tc_credentials.json)
      -v, --verbose         Turn on verbose output, with all the debug logger.
                            (default: False)


SSL InsecurePlatformWarning
---------------------------

If you got the following error message when running the tools, please install **requests[security]** package.

.. code-block:: bash

    InsecurePlatformWarning: A true SSLContext object is not available.
    This prevents urllib3 from configuring SSL appropriately and may cause certain SSL connections to fail.
    For more information, see https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning.


Install package by pip install. Please note it's not required for Python 2.7.9+.

.. code-block:: bash

    pip install requests[security]

If you got **Setup script exited with error: command 'gcc' failed with exit status 1** error when install **requests[security]**, please install **libffi-dev**. (Ubuntu)

.. code-block:: bash

    sudo apt-get install libffi-dev


The Other Issues
----------------

If you meet any issues related to urllib3, SSL, or tk, please install following packages. (Ubuntu)

.. code-block:: bash

    sudo apt-get install python python-dev python-setuptools libffi-dev libssl-dev python-tk
    sudo easy_install pip
    sudo pip install -U pip setuptools
    sudo pip install -U requests
    sudo pip install -U requests[security]
