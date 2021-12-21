# SitSmart

## About
This project is a smart hot desking system. It allows users to book based on their preferences. Currently, these "preferences" include **air quality**, **noisiness**, and **temperature levels**. Users are able to book the desks from the booking website.<br/><br/>
This project integrates the software components with IoT components (sensors and Raspberry Pi) to be able to get the environment data of the desks.

## Architecture
![Technical Architecture](https://i.ibb.co/1XqVznD/Use-case-diagram-9.png)
### Hardware
For the hardware component, we are using the following sub-components:
1. SGP30 CO2 sensor
2. DHT11 temperature sensor
3. LM386 sound sensor
4. 10k Ohm resistor
5. Raspberry Pi
6. Breadboard
7. Jumper wires
### Backend
AWS EC2 instance (with Nginx as the web server and MySQL as the database server).
### DNS
AWS Route 53
### Email Service
Amazon SES. Currently, Our Amazon SES is not working since it's still not permitted for production access (i.e. every destination email address should be registered and verified first in our internal Amazon SES console, which is not really feasible in production).
### PubSub
For the publisher-subscriber component, we're using PubNub. 

## Running on local machine
**Please follow the sections IN-ORDER, otherwise some components will complain if a pre-requisite component is not yet initialized**
### Server and Database (Backend)
1. open terminal
2. `git clone https://github.com/Denniswillie/SitSmart.git <folderName>`
3. `cd <folderName>`
4. Create Python virtual environment and load pip dependencies:
     - `python -m venv venv` (if `python` doesn't automatically refer to python 3, use `python3` instead, same for all usages of `python` below.)
     - `python -m pip install --upgrade pip`
     - `pip install flask flask-cors flask-session flask-mysqldb authlib python-dotenv pubnub flask-mail`
5. Turn on `Apache` and `MySql` on xampp control panel.
6. Create a database for the project on a local MySQL server. (below is a guide if you're using terminal)
     - `mysql -u root` if you haven't set a password, otherwise, `mysql -u root -p`. It will prompt you to enter a password.
     - `CREATE DATABASE <your_database_name>;`
     - `use <your_database_name>;`
     - copy the content of `database.sql` (the whole file) and paste it in the mysql console, press enter.
     - `exit`
7. Setup PubNub account, turn on access manager. Below is a short guide on how to set it up:
     - Create a PubNub account if you haven't.
     - Once logged in, click `Apps` on side navigation bar
     - Click `Create New App` and then enter the name of the new app
     - Click the newly created app
     - In the Configuration panel, turn on access manager.
8. [Setup Google Client ID and client secret](https://www.balbooa.com/gridbox-documentation/how-to-get-google-client-id-and-client-secret)
9. Create a file called `.env` like below: (replace all occurrences of `<...>` with the appropriate values)
```
MYSQL_HOST=<mysql_host_name>
MYSQL_USER=<mysql_user>
MYSQL_PASSWORD=<mysql_password>
MYSQL_DB=<your_database_name>
MAIL_DEFAULT_SENDER=<mail_default_sender>
MAIL_PASSWORD=<mail_password>
MAIL_USERNAME=<mail_username>
PUBNUB_PUBLISH_KEY=<pubnub_publish_key>
PUBNUB_SUBSCRIBE_KEY=<pubnub_subscribe_key>
PUBNUB_SECRET_KEY=<pubnub_secret_key>
GOOGLE_CLIENT_ID=<google_client_id>
GOOGLE_CLIENT_SECRET=<google_client_secret>
REDIRECT_URI=http://127.0.0.1:5000/authorize
```
8. `python app.py` (make sure to run it in `<folderName>`
9. Go to [localhost](http://127.0.0.1:5000). You should see the SitSmart's start screen.

### Sensors and Raspberry Pi (Hardware)
_This part assumes that:_
<br/>
_1. The Raspberry Pi is already connected to the internet. Make sure your network allows communications using PubNub._
<br/>
_2. You have already setup a PubNub account_
<br/>
_3. The server is running (i.e. ready to receive PubNub messages sent by `sensors.py`)_
<br/>
If all the steps above has already been completed, let's get into the "meat" of this section.
1. Wire the components as shown in the diagram below.
![Fritzing Diagram](https://i.ibb.co/DY9N5Cz/unknown.png)
2. Open terminal on Raspberry Pi
3. `git clone https://github.com/Denniswillie/SitSmart.git <folderName>` (we will need `sensors.py` and `admin_program.py`)
4. [Enable I2C](https://www.raspberrypi-spy.co.uk/2014/11/enabling-the-i2c-interface-on-the-raspberry-pi/). If you're having trouble with I2C not being connected after setting it up, refer to [this link](https://stackoverflow.com/questions/42904712/i2c-not-detecting-issues-in-hardware-or-any-other).
5. create `.env` file which looks like below (replace all occurrences of `<...>` with the appropriate values)
```
PUBNUB_PUBLISH_KEY=<pubnub_publish_key>
PUBNUB_SUBSCRIBE_KEY=<pubnub_subscribe_key>
BASE_URL=http://127.0.0.1:5000
```
6. `pip install pubnub python-dotenv adafruit-circuitpython-sgp30 adafruit-circuitpython-dht`
7. Setting up location and/or study table using the admin console program:
     - `python admin_program.py`
     - follow the prompts to create a location and/or study table
8. `python sensors.py` to run `sensors.py`. Please be aware that this program by default sends the data every 1 hour. If you want to modify the frequency, change the following line. After it sends the data, you should be able to see new `TableStats` table entries in the database:
```
if currTime - lastTime > 3600:  #Change 3600 to whatever frequency you want. Note that 3600 stands for 3600 seconds (1 hour)
```

## Developers
This project was developed by [Dennis](https://github.com/Denniswillie), [Ethan](https://github.com/EthanSia), [Jeremy](https://github.com/lonerly666), and [Kevin](https://github.com/kevmcenroe).
