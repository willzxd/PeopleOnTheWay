Travel Connection&copy;
=================
Upadate:08/12/2014

Overview
--------
This is a flask web app that helps traveler connect with local people. 
You can login with OpenID and edit your own profile.
You can search the people who live in the place you plan to go and have same interests with you.
Then you can see others' profile and send message to them.
Also after talked, you can give rates and comments to each other.

How to set up
-------------
In Mac OS X, input commands below:
> * $ mkdir microblog
> * $ cd microblog
> * $ sudo easy_install virtualenv
> * $ virtualenv flask
> * $ flask/bin/pip install flask
> * $ flask/bin/pip install flask-login
> * $ flask/bin/pip install flask-openid
> * $ flask/bin/pip install flask-mail
> * $ flask/bin/pip install flask-sqlalchemy
> * $ flask/bin/pip install sqlalchemy-migrate
> * $ flask/bin/pip install flask-whooshalchemy
> * $ flask/bin/pip install flask-wtf
> * $ flask/bin/pip install flask-babel
> * $ flask/bin/pip install guess_language
> * $ flask/bin/pip install flipflop
> * $ flask/bin/pip install coverage
Then copy all the files to this microblog folder.

How to create database
----------------------
In Mac OS X, input following commands under your path of microblog folder:
> * $ chmod a+x db_create.py db_migrate.py db_upgrade.py
> * $ ./db_create.py
> * $ ./db_migrate.py
> * $ ./db_upgrade.py

How to generate sample database
-------------------------------
In Mac OS X, input following commands under your path of microblog folder:
> * $ flask/bin/python enteruser.py
> * $ flask/bin/python enteraoi.py

How to run the app
------------------
In Mac OS X, input following commands under your path of microblog folder:
$ ./run.py
And open your browser, enter the URL: http://127.0.0.1:5000/.

Limitations in our current implementation
------------------------------------------
1. Error messages showed on the top of the page. However, they should be in proper areas.
2. Search of area of interests is not user-friendly. It cannot insert mulitple area of interests or experts area. 
3. Live chat is not implemented. 
4. Search results cannot be sorted by ratings or other choices.
5. No feedbacks can be replied to comments. 
6. When editing the profile, eventhing is required, which should be improved in the future. 

Team
-----
[Xiaodan Zhu](https://github.com/willzxd/), [Yongjiao Yu](https://github.com/Yongjiao), Yan Huang, Vivian Li

Reference
---------
[flask](http://flask.pocoo.org)<br />
[flask-WTF](https://flask-wtf.readthedocs.org/en/latest/)<br />
[flask tutorial(chinese version, but out of date)](http://www.pythondoc.com/flask-mega-tutorial/index.html)<br />
[jinja2](http://jinja.pocoo.org)<br />
[SQLalchemy](http://www.sqlalchemy.org)<br />
[Bootstrap](http://getbootstrap.com)<br />

