UNICEF Geotpatial Server
========================


Prerequisites
-------------

 - [pipenv](https://github.com/pypa/pipenv) (better with [pipsi](https://github.com/mitsuhiko/pipsi))
 - [postgis](https://postgis.net/)
 
 - optional [docker](https://www.docker.com/)
  
Contribute
----------

    $ git clone https://github.com/unicef/unicef-geospatial.git
    $ cd unicef-geospatial
    $ make develop
    $ pipenv shell


Quickstart Demo Server
----------------------


GDM3-6 import
----------------------

    $ python manage.py import-global gadm3-6