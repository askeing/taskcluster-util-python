import os
from setuptools import setup, find_packages


VERSION='0.0.9'

# TODO:
# Bug 1184209 - reference-format: Handle end-points that returns a stream (Discussion)
# when Bug 1184209 is fixed, then modify the taskcluster version to >=0.0.21
install_requires = [
  'taskcluster==0.0.21',
]

here = os.path.dirname(os.path.abspath(__file__))
# get documentation from the README
try:
    with open(os.path.join(here, 'README.rst')) as doc:
        long_description = doc.read()
except:
    long_description = ''


if __name__ == '__main__':
  setup(
    name='taskcluster_util',
    version=VERSION,
    description='Taskcluster Utilities',
    long_description=long_description,
    keywords='taskcluster utilities download ',
    author='Askeing Yen',
    author_email='askeing@gmail.com',
    url='https://github.com/askeing/taskcluster-util-python',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    package_data={},
    install_requires=install_requires,
    zip_safe=False,
    entry_points="""
        # -*- Entry points: -*-
        [console_scripts]
        taskcluster_download = taskcluster_util.taskcluster_download:main
        """,
  )
