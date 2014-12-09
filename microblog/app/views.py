from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid, models
from .forms import LoginForm, EditForm, RatingsForm, MessagesForm, SearchForm
from .models import User, AreaOfInterests
from datetime import datetime

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
    
@app.route('/')
@app.route('/index', methods = ['GET'])
def index():
    user = g.user
    form = SearchForm()
    if form.validate_on_submit():
        s=str.strip(form.state.data)
        c=str.strip(form.city.data)
        a=str.strip(form.activity.data)
        query = [s, c, a]
    #if not form.validate_on_submit():
    #    return redirect(url_for('search'))
   #return render_template('index.html', form=form)
    if g.user.is_authenticated():
        # whether guser has new messages
        messages = user.get_new_messages().all()
        newmessage = 0
        for message in messages:
            if message.readstamp == 0:
                newmessage = 1
        return render_template('index.html',
        newmessage = newmessage,
        user = user, form = form)        
    return render_template('index.html', newmessage = 0, form = form)

#@app.route('/')
#@app.route('/search', methods= ['GET'])
#def search():
#   form = SearchForm()
#    if form.validate_on_submit():
#        s=str.strip(form.state.data)
#        c=str.strip(form.city.data)
#        a=str.strip(form.activity.data)
#        query = [s, c, a]
    #if not form.validate_on_submit():
    #    return redirect(url_for('search'))
#    return render_template('search.html', form=form)

@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname = nickname, email = resp.email)
        db.session.add(user)
        db.session.commit()
        aoi=models.AreaOfInterests(user_id=user.id, country=' ',state=' ',city=' ',area=' ')
        db.session.add(aoi)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    
@app.route('/user/<nickname>', methods = ['GET', 'POST'])
@login_required
def user(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    # posts = [
    #     { 'author': user, 'body': 'Test post #1' },
    #     { 'author': user, 'body': 'Test post #2' }
    # ]
    comments = user.get_comments().all()
    averagerate = 0
    if len(comments) != 0:
        for comment in comments:
            averagerate = averagerate + comment.rates
        averagerate = averagerate / len(comments)
    #
    useraoi = user.get_aoi().all()
    #rating other users
    form = RatingsForm()
    if form.validate_on_submit():
        # users should chat with each other first
        messagesbetween = user.get_user_messages(g.user).all()
        if len(messagesbetween) != 0:
            rating = models.Ratings(rater_id = g.user.id,
                rated_id = user.id,
                comment = form.comment.data, 
                rates= form.rates.data,
                timestamp = datetime.now())
            db.session.add(rating)
            db.session.commit()
            flash('Your rating is now live!')
            return redirect(url_for('user', nickname=nickname))
        flash('Chat with each other first!')    
    # limitation of ratings    
    ratingsbetween=models.Ratings.query.filter_by(rater_id=g.user.id).filter_by(rated_id=user.id).order_by('timestamp').all()
    if len(ratingsbetween):
        print 'ratingsbetween',ratingsbetween[-1]
        duration = (datetime.now() - ratingsbetween[-1].timestamp).days
        print 'duration', duration
        if duration < 1:
            return render_template('user.html',
            title= user.nickname,
            user = user,
            comments = comments,
            useraoi = useraoi,
            form = None,
            nickname = nickname,
            averagerate =  "%.1f" % averagerate)
    return render_template('user.html',
        title= user.nickname,
        user = user,
        comments = comments,
        useraoi = useraoi,
        form = form,
        nickname = nickname,
        averagerate =  "%.1f" % averagerate)

@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    guseraoi=g.user.get_aoi().first()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.firstname = form.firstname.data
        g.user.lastname = form.lastname.data
        g.user.phone = form.phone.data
        g.user.about_me = form.about_me.data
        guseraoi.country = form.country.data
        guseraoi.state = form.state.data
        guseraoi.city = form.city.data
        guseraoi.area = form.area.data
        db.session.add(g.user)
        db.session.commit()
        db.session.add(guseraoi)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    elif request.method != "POST":
        form.nickname.data = g.user.nickname
        if form.about_me.data: 
            form.about_me.data = g.user.about_me
        if form.firstname.data: 
            form.firstname.data = g.user.firstname
        if form.lastname.data: 
            form.lastname.data = g.user.lastname
        if form.phone.data: 
            form.phone.data = g.user.phone
        if form.country.data: 
            form.country.data = guseraoi.country
        if form.state.data: 
            form.state.data = guseraoi.state
        if form.city.data: 
            form.city.data = guseraoi.city
        if form.area.data: 
            form.area.data = guseraoi.area
    return render_template('edit.html',
        form = form)

@app.route('/message/<nickname>', methods = ['GET', 'POST'])
@login_required
def sendMessage(nickname):
    #if browse his or her own profile
    if g.user.nickname == nickname:
        user = g.user
        messages = user.get_guser_messages().all()
        print user.nickname
        # templist for storing user 
        lists = []
        for message in messages:
            tempusers = message.get_guserconncector().all()
            for tempuser in tempusers:
                lists.append(tempuser.nickname)
        n = len(lists) - 1
        m = len(lists) - 2
        while n>=0:
            print lists
            print 'n=', n
            if lists[n] == user.nickname:
                print 'here!'
                lists.pop(n)
            n = n - 1
        lists = list(set(lists))
        print lists
        connectors=[]
        if lists:
            for l in lists:
                connector = models.User.query.filter_by(nickname=l).first()
                # a = connector.user_new(user)
                # print 'a=',a
                # print connector
                connectors.append(connector)
            print connectors
        return render_template('gusermessage.html',
            lists = connectors,
            user = g.user)
    else: 
    #if browse other's profile    
        user = User.query.filter_by(nickname = nickname).first()
        if user == None:
            flash('User ' + nickname + ' not found.')
            return redirect(url_for('index'))
        messages = user.get_user_messages(g.user).all()
        for message in messages:
            print 'before read',message
            message.readstamp = 1
            print 'after read', message
            db.session.commit()
        form = MessagesForm()
        if form.validate_on_submit():
            message = models.Messages(sender_id = g.user.id,
                receiver_id = user.id,
                text = form.text.data, 
                time = datetime.now(),
                readstamp = 0)
            db.session.add(message)
            db.session.commit()
            flash('Your message has been sent!')
            return redirect(url_for('user', nickname=nickname))
        return render_template('message.html',
            form = form,
            messages = messages)


@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500  


#non whoosh search
@app.route('/search_results/', methods= ['GET', 'POST'])
def search_results():
    form = SearchForm()
    if form.validate_on_submit():
        print 'fromsub'
        s=str.strip(str(form.state.data))
        c=str.strip(str(form.city.data))
        a=str.strip(str(form.activity.data))
        query = [s, c, a]
        # print 'new query', query

    s = str.strip(str(request.form['state']))
    c = str.strip(str(request.form['city']))
    a = str.strip(str(request.form['activity']))

    primary = User.query.join(AreaOfInterests, (AreaOfInterests.user_id == User.id)).filter_by(state=s, city=c, area=a).all()
    secondary = User.query.join(AreaOfInterests, (AreaOfInterests.user_id == User.id)).filter(AreaOfInterests.state == s, AreaOfInterests.area != a, AreaOfInterests.city==c).all()
    tertiary = User.query.join(AreaOfInterests, (AreaOfInterests.user_id == User.id)).filter(AreaOfInterests.state==s, AreaOfInterests.city != c, AreaOfInterests.area==a).all()
    quaternary = User.query.join(AreaOfInterests, (AreaOfInterests.user_id == User.id)).filter(AreaOfInterests.city==c, AreaOfInterests.area==a, AreaOfInterests.state != s).all()
    if (len(primary)+len(secondary)+len(tertiary)+len(quaternary) == 0):
        #flash does not work on Vivian computer, noresults template is backup
        flash('There is no result!')
        return redirect(url_for('index'))
    return render_template('search_results.html', query=query,
                            primary=primary,
                            secondary=secondary,
                            tertiary=tertiary,
                            quaternary=quaternary, form = form)



