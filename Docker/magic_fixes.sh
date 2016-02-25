#!/bin/sh
EXTERNAL_IP="178.62.244.150"

#We want to make sure mysql is running while we run this!
/etc/init.d/mysql start
# Fix some ip's pointing to DigitalOcean dev servers
echo "Fixing ip's pointing to wrong places!"

find ./mydataoperatorui/ -type f -exec     sed -i 's/127.0.0.1:10000/'"$EXTERNAL_IP"':8080/g' {} +
find ./mydataoperatorui/ -type f -exec     sed -i 's/127.0.0.1:8080/'"$EXTERNAL_IP"':8080/g' {} +
find ./mydataoperatorui/ -type f -exec     sed -i 's/178.62.244.150:10000/'"$EXTERNAL_IP"':8080/g' {} +
find ./mydataoperatorui/ -type f -exec     sed -i 's_127.0.0.1/assets_'"$EXTERNAL_IP"'/assets_g' {} +

find ./mydataoperator -type f -exec     sed -i 's/95.85.39.236/127.0.0.1/g' {} +
find ./mydataoperator -type f -exec     sed -i 's/178.62.229.148/127.0.0.1/g' {} +
find ./mydataoperator -type f -exec     sed -i 's/178.62.244.150/127.0.0.1/g' {} +
sed -i 's_127.0.0.1:80/assets_'"$EXTERNAL_IP"'/assets_g' ./mydataoperator/DO/GenericConfigFile.json

find ./ -type f -exec     sed -i 's/95.85.39.236/127.0.0.1/g' {} +
find ./mydatasink -type f -exec     sed -i 's/178.62.229.148/127.0.0.1/g' {} +
find ./mydatasource -type f -exec     sed -i 's/178.62.229.148/127.0.0.1/g' {} +
find ./mydatasink -type f -exec     sed -i 's/178.62.244.150/127.0.0.1/g' {} +
find ./mydatasource -type f -exec     sed -i 's/178.62.244.150/127.0.0.1/g' {} +

echo "Setting database script in Sink executable!"
chmod +x ./mydatasink/DataSink/scripts/create_db.sh

echo "Creating database for Operator"
echo create database IF NOT EXISTS dataoperator | mysql -h127.0.0.1 -P3306 -uroot -pXmNT86Pi
sleep 1
echo "Initializing operator database!"
cd mydataoperator
nohup python DO/app.py &
echo "Started DO, waiting a little while..."
sleep 10
echo "Requesting RESET"
wget http://localhost:8080/RESET
cat RESET
echo "DONE!"
cd ..
# Make folders for few sample sinks & sources and configure them



echo "Setting up SWH-Sink"
mkdir -p SWH-Sink
cp -r mydatasink/DataSink/* SWH-Sink
cd SWH-Sink
find ./ -type f -exec sed -i 's/APP_GLOBAL_ID = '"'4'"'/APP_GLOBAL_ID = '"'6'"'/g' {} +
find ./ -type f -exec sed -i 's/DATASINKID="5"/DATASINKID="6"/g' {} +
find ./ -type f -exec sed -i 's/APP_NAME = '"'"'DataSink'"'"'/APP_NAME = "DataSink6"/g' {} +
find ./ -type f -exec sed -i 's/PORT = '"'"'20000'"'"'/PORT = '"'"'20003'"'"'/g' {} +
echo create database IF NOT EXISTS datasink6 | mysql -h127.0.0.1 -P3306 -uroot -pXmNT86Pi
cd ..



echo "Setting up PHR"
mkdir -p PHR
cp -r mydatasink/DataSink/* PHR
cd PHR
find ./ -type f -exec sed -i 's/APP_GLOBAL_ID = '"'4'"'/APP_GLOBAL_ID = '"'5'"'/g' {} +
find ./ -type f -exec sed -i 's/DATASINKID="5"/DATASINKID="5"/g' {} +
find ./ -type f -exec sed -i 's/APP_NAME = '"'"'DataSink'"'"'/APP_NAME = "DataSink5"/g' {} +
find ./ -type f -exec sed -i 's/PORT = '"'"'20000'"'"'/PORT = '"'"'20001'"'"'/g' {} +
echo create database IF NOT EXISTS datasink5 | mysql -h127.0.0.1 -P3306 -uroot -pXmNT86Pi
cd ..



echo "Setting up SWH-Source"
echo create database IF NOT EXISTS datasource4 | mysql -h127.0.0.1 -P3306 -uroot -pXmNT86Pi
mkdir -p SWH-Source
cp -r mydatasource/DataSource/* SWH-Source
echo "Done making clone of source directory!"
cd SWH-Source
find ./ -type f -exec sed -i 's/dsource:123456@localhost\/datasource/root:XmNT86Pi@localhost\/datasource4/g' {} +
find ./ -type f -exec sed -i 's/SERVICE_ID = '"'1'"'/SERVICE_ID = '"'4'"'/g' {} +
echo "Done making replace magic"
nohup python run.py &
echo "Started Source, waiting 10 sec"
sleep 10
echo "Running Init script"
sh init.sh
echo "Done running Init script!"
cd ..
echo "Done!"

echo "Setting up Sesko"
echo create database IF NOT EXISTS datasource3 | mysql -h127.0.0.1 -P3306 -uroot -pXmNT86Pi
mkdir -p Sesko
cp -r mydatasource/DataSource/* Sesko
cd Sesko
find ./ -type f -exec sed -i 's/dsource:123456@localhost\/datasource/root:XmNT86Pi@localhost\/datasource3/g' {} +
find ./ -type f -exec sed -i 's/SERVICE_ID = '"'1'"'/SERVICE_ID = '"'3'"'/g' {} +
nohup python run.py &
sleep 10
sh init.sh
cd ..


echo "Setting up MyLocation"
echo create database IF NOT EXISTS datasource2 | mysql -h127.0.0.1 -P3306 -uroot -pXmNT86Pi
mkdir -p MyLocation
cp -r mydatasource/DataSource/* MyLocation
cd MyLocation
find ./ -type f -exec sed -i 's/dsource:123456@localhost\/datasource/root:XmNT86Pi@localhost\/datasource2/g' {} +
find ./ -type f -exec sed -i 's/SERVICE_ID = '"'1'"'/SERVICE_ID = '"'2'"'/g' {} +
nohup python run.py &
sleep 10
sh init.sh
cd ..


echo "Setting up RunningFree"
echo create database IF NOT EXISTS datasource1 | mysql -h127.0.0.1 -P3306 -uroot -pXmNT86Pi
mkdir -p RunningFree
cp -r mydatasource/DataSource/* RunningFree
cd RunningFree
find ./ -type f -exec sed -i 's/dsource:123456@localhost\/datasource/root:XmNT86Pi@localhost\/datasource1/g' {} +
find ./ -type f -exec sed -i 's/SERVICE_ID = '"'1'"'/SERVICE_ID = '"'1'"'/g' {} +
nohup python run.py &
sleep 10
sh init.sh
cd ..
echo "bash" >> /etc/rc.local
