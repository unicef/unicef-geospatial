UNICEF Geospatial Server Docker image
=====================================

[![](https://images.microbadger.com/badges/version/unicef/geospatial.svg)](https://microbadger.com/images/unicef/geospatial)

To build docker image simply cd in `docker` directory and run 

    make build
    
default settings are for production ready environment, check `run` target in 
the `Makefile` to see how to run the container with debug/less secure configuration

Image provides following services:

    - geospatial   
    - celery workers
    - celery beat

to configure which services should be started, set `SERVICES` appropriately, ie:


    docker run \
        ...
        -e SERVICES="redis,workers,beat,geospatial,flower"
        
**Note** If `SERVICES` is empty internal `supervisord` daemon does not start. 
