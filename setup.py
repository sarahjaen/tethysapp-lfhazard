from setuptools import setup, find_namespace_packages
from tethys_apps.app_installation import find_resource_files

# -- Apps Definition -- #
app_package = 'lfhazard'
release_package = 'tethysapp-' + app_package

# -- Python Dependencies -- #
dependencies = []

# -- Get Resource File -- #
resource_files = find_resource_files('tethysapp/' + app_package + '/templates', 'tethysapp/' + app_package)
resource_files += find_resource_files('tethysapp/' + app_package + '/public', 'tethysapp/' + app_package)
resource_files += find_resource_files('tethysapp/' + app_package + '/workspaces', 'tethysapp/' + app_package)


setup(
    name=release_package,
    version='2.0',
    description='A tool for retrieving liquefaction hazard parameters in the Unites States',
    long_description='A tool for retrieving liquefaction hazard parameters based on Standard or Cone Penetration Tests',
    keywords='Liquefaction, Geotechnical',
    author='Riley Hales, Tylor Bayer, Kevin Liang',
    author_email='',
    url='',
    license='BSD Clear 3 Clause',
    packages=find_namespace_packages(),
    package_data={'': resource_files},
    include_package_data=True,
    zip_safe=False,
    install_requires=dependencies,
)