from hashlib import md5
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index=True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    firstname = db.Column(db.String(32), index=True, nullable=True)
    lastname = db.Column(db.String(32), index=True, nullable = True)
    phone = db.Column(db.String(32), nullable=True)
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    aoi = db.relationship('AreaOfInterests', backref = 'person', lazy = 'dynamic')
    about_me = db.Column(db.String(300))
    last_seen = db.Column(db.DateTime)
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)
    
    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname = nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname

    # get area of interests of user
    def get_aoi(self):
        return AreaOfInterests.query.join(User, (User.id == AreaOfInterests.user_id)).filter(self.id == AreaOfInterests.user_id)

    # get comments of user
    def get_comments(self):
        return Ratings.query.join(User, (User.id == Ratings.rated_id)).filter(self.id == Ratings.rated_id).order_by(Ratings.timestamp.desc())

    # get all messages of guser
    def get_guser_messages(self):
        send = Messages.query.join(User, (User.id == Messages.sender_id)).filter(self.id == Messages.sender_id)
        receive = Messages.query.join(User, (User.id == Messages.receiver_id)).filter(self.id == Messages.receiver_id)
        return send.union(receive).order_by('messages_time')

    # get all messages between guser and some user
    def get_user_messages(self, user):
        send = Messages.query.join(User, (User.id == Messages.sender_id)).filter(self.id == Messages.sender_id).filter(user.id == Messages.receiver_id)
        receive = Messages.query.join(User, (User.id == Messages.sender_id)).filter(user.id == Messages.sender_id).filter(self.id == Messages.receiver_id)
        return send.union(receive).order_by('messages_time') 
    # judge whether there is any new messages
    # guser is the receiver, and if any messages readstamp is 0, there should me some new messages
    def get_new_messages(self):
        receive = Messages.query.join(User, (User.id == Messages.receiver_id)).filter(self.id == Messages.receiver_id)
        return receive

    #judge the new messages from which user
    def user_new(self, user):
        news = Messages.query.filter_by(sender_id=self.id).filter_by(receiver_id=user.id).all()
        newornot = False
        for new in news:
            print 'user_new',new 
            if new.readstamp == 0:
                newornot = True
        return newornot

    # get user's state
    def get_user_state(self):
        return AreaOfInterests.query.join(User,(User.id==AreaOfInterests.user_id)).filter(self.id == AreaOfInterests.user_id).first().state

        # get user's state
    def get_user_city(self):
        return AreaOfInterests.query.join(User,(User.id==AreaOfInterests.user_id)).filter(self.id == AreaOfInterests.user_id).first().city

        # get user's state
    def get_user_area(self):
        return AreaOfInterests.query.join(User,(User.id==AreaOfInterests.user_id)).filter(self.id == AreaOfInterests.user_id).first().area

    def __repr__(self):
        return '<User %r %r %r %r %r %r %r>' % (self.id, self.nickname, self.email, self.firstname, self.lastname, self.phone, self.about_me)    
        
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)

class AreaOfInterests(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    country = db.Column(db.String(64))
    state = db.Column(db.String(64))
    city = db.Column(db.String(64))
    area = db.Column(db.String(120), nullable=True)
    #area is things like fishing, retaurant, hiking, etc.
    
    def __repr__(self):
        return '<AreaOfInterests %r %r %r %r %r %r>' % (self.id, self.user_id, self.country, self.state, self.city, self.area)

class Ratings(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    rater_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    rated_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    rates = db.Column(db.Float, nullable = False)
    comment = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime)

    rater = db.relationship('User', foreign_keys = 'Ratings.rater_id')
    rated = db.relationship('User', foreign_keys = 'Ratings.rated_id')

    def get_rater(self):
        return User.query.filter_by(id=self.rater_id).first()

    def __repr__(self):
        return '<Ratings %r %r %r %r %r %r>' % (self.id, self.rater_id, self.rated_id, self.rates, self.comment, self.timestamp)

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    text = db.Column(db.Text, nullable = False)
    time = db.Column(db.DateTime)
    readstamp = db.Column(db.Integer, nullable = False)
    
    sender = db.relationship('User', foreign_keys = 'Messages.sender_id')
    receiver = db.relationship('User', foreign_keys = 'Messages.receiver_id')

    # When view messages history, we need this function to find who send the message.
    def get_sender(self):
        return User.query.filter_by(id=self.sender_id).first()

    def get_guserconncector(self):
        a = User.query.filter_by(id=self.sender_id) 
        b = User.query.filter_by(id=self.receiver_id)
        return a.union(b)

    def __repr__(self):
        return '<Messages %r %r %r %r %r %r>' % (self.id, self.sender_id, self.receiver_id, self.text, self.time,self.readstamp)
