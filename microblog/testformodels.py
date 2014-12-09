from app import db,models
from datetime import datetime, timedelta

user=models.User.query.filter_by(id=1).first()

a=models.Messages(sender_id=1, receiver_id =2, text='hello, 2nd user.',time=datetime.now())
db.session.add(a)
db.session.commit()
a=models.Messages(sender_id=1, receiver_id =2, text='hello, 2nd message from 1.',time= datetime.now() + timedelta(seconds=1))
db.session.add(a)
db.session.commit()
a=models.Messages(sender_id=2, receiver_id =1, text='hello, 1nd user.',time=datetime.now() + timedelta(seconds=2))
db.session.add(a)
db.session.commit()
a=models.Messages(sender_id=2, receiver_id =1, text='hello, 2nd message from 2.',time=datetime.now() + timedelta(seconds=3))
db.session.add(a)
db.session.commit()

messages = models.Messages.query.all()
print messages
