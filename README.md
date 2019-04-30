# Cache management project

### Installation and Setup

* Install [Python 2.7](https://www.python.org/download/releases/2.7/) and [pip](https://pypi.python.org/pypi/pip)


* Clone the project


* Set up virtual environment:

    $ pip install virtualenv
    $ virtualenv venv
    $ source venv/bin/activate
    
    
* Install project dependencies:
    
    $ pip install -r requirements.txt


* Install [mysql 5.7](https://dev.mysql.com/downloads/mysql/5.7.html) and run the server:

    $ mysql.server start

* Create database:

    $ mysql -u root
    mysql> create database cache
 
 
* Start server on your local machine:

    $ python app.py