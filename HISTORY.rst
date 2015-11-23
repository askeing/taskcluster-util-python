Release History
---------------

0.0.24 (2015-11-23)
+++++++++++++++++++

**Features and Improvements**

- Add taskcluster_login for getting credentials.

0.0.23 (2015-11-23)
+++++++++++++++++++

**Features and Improvements**

- Check the credentials does or doesn't expired, and print on console.

**Bugfixes**

- Raise exception when loading credentials file error.

0.0.22 (2015-11-06)
+++++++++++++++++++

**Bugfixes**

- Clean the cache of dest_dir and download_file_list after downloading.

0.0.21 (2015-11-04)
+++++++++++++++++++

**Features and Improvements**

- Provide a way to give TaskCluster builds to Bitbar (Bug 1189354).

0.0.20 (2015-11-02)
+++++++++++++++++++

**Features and Improvements**

- Modify the class for inheritance.

0.0.19 (2015-10-30)
+++++++++++++++++++

**Features and Improvements**

- Modify the logger and gui of taskcluster_traverse.

0.0.18 (2015-10-30)
+++++++++++++++++++

**Features and Improvements**

- Move tc_credentials.json to User's Home folder.
- Update README file.
- Update usage.
- Modify the Credentials input GUI of taskcluster_traverse.

0.0.17 (2015-10-27)
+++++++++++++++++++

**Features and Improvements**

- Add the credentials information.

0.0.16 (2015-10-13)
+++++++++++++++++++

**Bugfixes**

- Fix the issue of downloading public artifact when no credentials

0.0.15 (2015-10-02)
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
