from setuptools import setup


VERSION='0.0.1'

install_requires = [
  'taskcluster>=0.0.20',
]

if __name__ == '__main__':
  setup(
    name='taskcluster_util',
    version=VERSION,
    description='Taskcluster Utilities',
    author='Askeing Yen',
    author_email='askeing@gmail.com',
    url='https://github.com/askeing/taskcluster-util-python',
    packages=['taskcluster_util'],
    package_data={},
    install_requires=install_requires,
    zip_safe=False,
  )
