# DataOperator Backend

This repository holds DataOperator Backend, it is a part of 4 pieces consisting of DataSink, DataSource, DataOperator UI and this DataOperator Backend.
This piece alone doesn't do much.

### Relevant Resources

[MyData Architecture](https://github.com/HIIT/mydata-stack)

---

## Getting started

###Docker setup

Docker Image is the preferred way to test this Demo.

---
### 1. Install Docker
#### for ubuntu
> sudo apt-get install docker.io

#### for centos
> sudo yum install docker

> sudo service docker start

### 2. Download docker images
> sudo docker pull dhrpoc/dhr

### 3. Start docker
> sudo docker run --name dhr -m 512m -it -p 10000:10000 -p 10001:10001 -p 10002:10002 -p 10003:10003 -p 10004:10004 -p 20001:20001 -p 20002:20002 dhrpoc/dhr

now you will have a docker shell
> service mysql start
> cd　~
> ./run_all.sh

Everything should running , you can visit
[http://127.0.0.1:10000](http://127.0.0.1:10000) to check it.

---
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
│   ├── GenericConfigFile.json      # Config file setting up the Demo (DO_backend doesn't utilize everything it could from there yet)
│   ├── Initdb.py                   # Class holding Database initialization code for the Demo
│   ├── Json2Swag.py                # Tool to create swagger documentation definitions based on existing JSON.
│   ├── README.md
│   ├── resources
│   │   ├── __init__.py
│   │   └──  Resources.py           # Descriptions of Database objects for SQLAlchemy.
│   │  
│   └── Templates.py                # Old file which used to hold template Data structures
├── doc
│   └── swagger.yml                 # Swagger Documentation YML of the API for parts that are used.
├── operator_private_key.pem        # Private key for signing and verifying JWT tokens
├── operator_public_key.pem         # Public key for signing and verifying JWT tokens
└── tools
    ├── ui_emulator.py              # Testing tool, may not be updated to work with latest version
    └── ui_makeContract.py          # Testing tool, may not be updated to work with latest version

```


ASCII structure of the project, how do we represent the branches in the final structure if its done using folders?

### Documentation

Documentation of API's used by DataOperator UI, Sink and Source can be found in file swagger.yml in /doc as well as instructions for stand alone setup without docker.

### Copying and License

This code is licensed under MIT