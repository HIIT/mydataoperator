# Stand alone setup
The stand alone setup wont include DataOperator UI, DataSink or DataSource, just the DataOperator Backend.
 
 ---
 
###Prerequisites:
```
Python 2.7
Flask
Flask-Restful
Flask-Cache
Flask-Cors
PyJWT
PassLib
Cryptography
Requests
SQLAlchemy
MySQL-python

MySQL compliant Server
```
### Cloning the repository and initial configuration.

```
git clone https://github.link.to.this.repository/
cd dhr-poc-1
```

Edit the DataBase credentials in db_handler.py near line 67 to match your setup
```python
self.engine = create_engine('mysql+mysqldb://root:XmNT86Pi@127.0.0.1/dataoperator',
```

### Running the service
```
python DO/app.py
```
