# DataOperator Backend

This is a part of proof-of-concept implementation of [MyData Architecture](https://github.com/HIIT/mydata-stack). 
This repository holds DataOperator Backend, it is a part of 4 pieces consisting of [DataSink](https://github.com/dhrproject/mydatasink), [DataSource](https://github.com/dhrproject/mydatasource), [DataOperator UI](https://github.com/dhrproject/mydataoperatorui) and this DataOperator Backend.

---

## Getting started

###Docker setup

Docker Image is the preferred way to test this POC.

### Prerequisites

 [Docker] (https://www.docker.com/)
 
### 1. Build docker image
You need the following files that are shipped in folder 'Docker' on this repository:

```
DockerFile
magic_fixes.sh
run_all.sh
services.sh
```

Go to the folder with the files and run the following command

```
docker build --no-cache -f DockerFile  -t dhrtest .
```

The command will take a while to run, you can now go get a new cup of coffee.
When the command is done you will see line similar to:

```
Successfully built d061ec09e273
```

We will now call the ID above <ID>

Now run:

```
docker run -p 127.0.0.1:80:80 -p 127.0.0.1:8080:8080 -i -t <ID> /etc/rc.local
```

This will start the container including the PoC environment ending with bash prompt.

When you see lines:

```
Finished starting up the PoC environment!
root@127:/~#
```
The container is ready and PoC environment running.
Once this has been done you can press Ctrl+P+Q to detach the container without closing it.
At this point the Testing Environment is available on localhost.

Everything should running , you can visit
[http://127.0.0.1/](http://127.0.0.1/) to check it.


## DataOperator Backend

### Repository structure

```

├── DO
│   ├── app.py                      # API
│   ├── base.py
│   ├── contributors.txt            # Contributors to the Project
│   ├── custom_errors.py            # Custom HTTPException for inserting relevant debug info to replies to clients.
│   ├── db_handler_Basic.py         # Basic class for DB handling. Simple functions for interacting with DataOperator Backend specific DB model. Based on Core class
│   ├── db_handler_High.py          # High class for DB handling. Complex functions for API. Based on Basic class
│   ├── db_handler.py               # Core class for DB handling. Simple functions and initialization for DB.
│   ├── GenericConfigFile.json      # Config file setting up the POC (DO_backend doesn't utilize everything it could from there yet)
│   ├── Initdb.py                   # Class holding Database initialization code for the POC
│   ├── README.md
│   └── resources
│       ├── __init__.py
│       └──  Resources.py           # Descriptions of Database objects for SQLAlchemy.
├── doc
│   └── swagger.yml                 # Swagger Documentation YML of the API for parts that are used.
├── operator_private_key.pem        # Private key for signing and decrypting JWT tokens
├── operator_public_key.pem         # Public key for encrypting and verifying JWT tokens
└── tools
    ├── Json2Swag.py                # Tool to create swagger documentation definitions based on existing JSON.
    ├── ui_emulator.py              # Testing tool, may not be updated to work with latest version
    └── ui_makeContract.py          # Testing tool, may not be updated to work with latest version

```


### Documentation

Documentation of API's used by DataOperator UI, Sink and Source can be found in file swagger.yml in /doc as well as instructions for stand alone setup without docker.

### Copying and License

This code is licensed under [MIT](https://github.com/dhrproject/mydataoperator/blob/master/LICENSE.md)
