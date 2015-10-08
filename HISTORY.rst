Release History
---------------

0.0.15 (2015-10-08)
+++++++++++++++++++

**Features and Improvements**

- Upgrade the taskcluster library to 0.0.27, which fixed the bewit issue.
- Download artifacts by Signed URL, not API method.

0.0.14 (2015-10-01)
+++++++++++++++++++

**Bugfixes**

- Fix the internal server error (cause by taskcluster v0.0.21).

0.0.13 (2015-09-07)
+++++++++++++++++++

**Features and Improvements**

- Refactoring.
- Using the prograssbar package to display the download progress.
- Add hooking point 'do_after_download' after downloading.

0.0.12 (2015-09-04)
+++++++++++++++++++

**Bugfixes**

- Fix some description error.

0.0.11 (2015-09-04)
+++++++++++++++++++

**Features and Improvements**

- Add taskcluster_traverse.
- Modify setup.py, HISTORY, and README.
- Add more function of TaskFinder.
- Add Makefile and travis ci settings.
- Add unittest cases.

**Bugfixes**

- Fix the temp folder deleted issue when downloading multiple times.

0.0.10 (2015-08-04)
+++++++++++++++++++

**Features and Improvements**

- Download artifacts from taskcluster.

0.0.1 (2015-07-15)
++++++++++++++++++
- Initiate the project.
