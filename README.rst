taskcluster-util-python
=======================

Python Taskcluster Utilities.


taskcluster_download
--------------------
.. code-block:: bash

    usage: taskcluster_download [-h] [--credential CREDENTIAL]
                                (-n NAMESPACE | -t TASK_ID) [-a ARITFACT_NAME]
                                [-d DEST_DIR]
    
    The simple download tool for Taskcluster.
    
    optional arguments:
      -h, --help            show this help message and exit
      --credential CREDENTIAL
                            The credential JSON file (default: credential.json)
      -n NAMESPACE, --namespace NAMESPACE
                            The namespace of task
      -t TASK_ID, --taskid TASK_ID
                            The taskId of task
    
    Download Artifact:
      The artifact name and dest folder
    
      -a ARITFACT_NAME, --artifact ARITFACT_NAME
                            The artifact name on Taskcluster
      -d DEST_DIR, --dest-dir DEST_DIR
                            The dest folder
