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
Amazon SES

## Running on local machine
### Server and Database (Backend)
1. `git clone https://github.com/Denniswillie/SitSmart.git <folderName>`
2. `cd <folderName>`
3. Create Python virtual environment and load pip dependencies:
     - `python -m venv venv` (if `python` doesn't automatically refer to python 3, use `python3` instead, same for all usages of `python` below.)
     - `python -m pip install --upgrade pip`
     - `pip install flask flask-cors flask-session flask-mysqldb authlib python-dotenv pubnub flask-mail`
4. Create a database for the project on a local MySQL server. 
5. Setup PubNub account, turn on access manager
6. [Setup Google Client ID and client secret](https://www.balbooa.com/gridbox-documentation/how-to-get-google-client-id-and-client-secret)
7. Create a file called `.env` like below: (replace all occurrences of `<...>` with the appropriate values)
```
MYSQL_HOST=<mysql_host_name>
MYSQL_USER=<mysql_user>
MYSQL_PASSWORD=<mysql_password>
MYSQL_DB=<mysql_db>
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

## Developers
This project was developed by [Dennis](https://github.com/Denniswillie), [Ethan](https://github.com/EthanSia), [Jeremy](https://github.com/lonerly666), and [Kevin](https://github.com/kevmcenroe).
