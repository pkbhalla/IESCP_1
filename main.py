import os
from flask import Flask 
from flask import render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


curr_dir=os.path.abspath(os.path.dirname(__file__))

#Creating a Flask instance
app=Flask(__name__, template_folder="templates")
app.secret_key="letsencrypt"


#adding the database
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(curr_dir,'iescp.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(30), nullable = False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_sponsor = db.Column(db.Boolean, default=False)
    is_influencer = db.Column(db.Boolean, default=False)
    sp_industry = db.Column(db.String(30), nullable=True)
    inf_category = db.Column(db.String(30),nullable=True)
    inf_niche = db.Column(db.String(30), nullable=True)
    inf_reach = db.Column(db.Integer, nullable=True)
    sp_budget = db.Column(db.Integer, nullable=True)
    campaigns = db.relationship('Campaign', back_populates='sponsor', cascade="all, delete-orphan")
    ad_requests = db.relationship('AdRequest', back_populates='influencer', cascade="all, delete-orphan")

# Campaign model
class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=datetime.now().date())
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    visibility = db.Column(db.String(10), nullable=False, default='public')
    goals = db.Column(db.Text, nullable=True)
    status_camp = db.Column(db.String(10), nullable=False, default='ongoing') #ongoing, completed, cancelled
    sponsor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sponsor = db.relationship('User', back_populates='campaigns')
    ad_requests = db.relationship('AdRequest', back_populates='campaign', cascade="all, delete-orphan")

# AdRequest model
class AdRequest(db.Model):
    __tablename__ = 'ad_requests'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    messages = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.String(10), nullable=False, default='sponsor')  # 'sponsor' or 'influencer'
    status_adreq = db.Column(db.String(10), nullable=False, default='pending')  #pending, accepted, rejected
    campaign = db.relationship('Campaign', back_populates='ad_requests')
    influencer = db.relationship('User', back_populates='ad_requests')


#initialising database
db.init_app(app)
app.app_context().push()


#creating database if not already exists
if os.path.exists("iescp.sqlite3")==False:
    db.create_all()


@app.route("/")
def home():
    return render_template('index.html')

@app.route("/register/<user_type>", methods=['GET', 'POST'])
def register(user_type):
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, salt_length = 16)
        user_name_exist = User.query.filter_by(username=username).first()
        if user_name_exist:
            flash('This username already exists. Please use other username.', 'danger')
            return render_template('register.html', user_type = user_type)
        email_exist = User.query.filter_by(email=email).first()
        if email_exist:
            flash('This username already exists. Please use other username.', 'danger')
            return render_template('register.html', user_type = user_type)
        
        if user_type == "admin":
            user = User(name = name, username=username, email=email, password=hashed_password, is_admin = True )
        if user_type == "sponsor":
            sp_industry = request.form.get('sp_industry')
            sp_budget = request.form.get('sp_budget')
            user = User(name = name, username=username, email=email, password=hashed_password, is_sponsor = True, sp_industry=sp_industry, sp_budget = sp_budget)
        if user_type == "influencer":
            inf_category = request.form.get('inf_category')
            inf_niche = request.form.get('inf_niche')
            inf_reach = request.form.get('inf_reach')
            user = User(name = name, username=username, email=email, password=hashed_password, is_influencer = True , 
                    inf_category = inf_category, inf_niche=inf_niche, inf_reach = inf_reach)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', user_type = user_type)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            session['is_sponsor'] = user.is_sponsor
            session['is_influencer'] = user.is_influencer
            flash('Login successful!', 'success')
            if user.is_admin:
                user_type="admin"
                return redirect('/'+user_type+'/dashboard')
            if user.is_sponsor:
                user_type="sponsor"
                return redirect('/'+user_type+'/dashboard')
            if user.is_influencer:
                user_type="influencer"
                return redirect('/'+user_type+'/dashboard')
        flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')



@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    session.pop('is_sponsor', None)
    session.pop('is_influencer', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/<user_type>/dashboard', methods=['GET', 'POST'])
def dashboard(user_type):
    if request.method == "GET":
        if 'user_id' in session:
            if user_type=="admin" and session["is_admin"]:
                ongoing_campaigns = Campaign.query.join(User).filter(Campaign.status_camp=='ongoing').all()
                all_users = User.query.all()
                all_campaigns = Campaign.query.join(User).all()
                all_ad_reqs = AdRequest.query.join(Campaign).all()
                return render_template(user_type + '_dashboard.html', ongoing_campaigns=ongoing_campaigns, all_users=all_users, all_campaigns=all_campaigns, all_ad_reqs = all_ad_reqs)
 
            if user_type=="sponsor" and session["is_sponsor"]:
                ongoing_campaigns = Campaign.query.filter(Campaign.status_camp=='ongoing',Campaign.sponsor_id==session["user_id"]).all()
                received_ad_requests = AdRequest.query.filter((AdRequest.created_by == 'influencer') & (AdRequest.status_adreq == 'pending') & (AdRequest.campaign_id == Campaign.id) & (Campaign.sponsor_id == session["user_id"])).all()
                return render_template(user_type + '_dashboard.html', ongoing_campaigns=ongoing_campaigns, ad_requests=received_ad_requests)
            ad_requests=[]
            if user_type=="influencer" and session["is_influencer"]:
                influencer = User.query.filter(User.id == session["user_id"]).first()
                ongoing_campaigns = Campaign.query.join(Campaign.ad_requests).filter(Campaign.status_camp == 'ongoing',AdRequest.influencer_id == session["user_id"],AdRequest.status_adreq == 'accepted').distinct(Campaign.id).all()
                ad_requests = AdRequest.query.join(Campaign).filter(Campaign.status_camp == 'ongoing',AdRequest.influencer_id == session["user_id"],AdRequest.status_adreq == 'pending', AdRequest.created_by=="sponsor").all()
                return render_template(user_type + '_dashboard.html', ongoing_campaigns=ongoing_campaigns, ad_requests=ad_requests, influencer=influencer)
            flash('Invalid user', 'danger')
            return redirect('/login')
        flash('Please login first', 'danger')
        return redirect('/login')





@app.route("/<user_type>/campaigns", methods=['GET', 'POST'])
def campaigns(user_type):
    if request.method == "GET":
        if 'user_id' in session:
            if user_type=="sponsor" and session["is_sponsor"]:
                campaigns = Campaign.query.filter(Campaign.sponsor_id==session["user_id"]).all()
                return render_template(user_type + '_campaigns.html', campaigns=campaigns)
            if user_type=="influencer" and session["is_influencer"]:
                search_query=request.args.get('search_query')
                if search_query:
                    search_filter = f"%{search_query}%"
                    public_campaigns = Campaign.query.filter(Campaign.visibility=="public", (Campaign.name.ilike(search_filter) | Campaign.description.ilike(search_filter) | Campaign.goals.ilike(search_filter))).all()
                else:
                    public_campaigns = Campaign.query.filter(Campaign.status_camp == 'ongoing',Campaign.visibility == 'public').all()  
                return render_template(user_type + '_campaigns.html', campaigns=public_campaigns)
            flash('Invalid user', 'danger')
            return redirect('/login')
        flash('Please login first', 'danger')
        return redirect('/login')


@app.route("/sponsor/create_campaign", methods=['GET', 'POST'])
def create_campaign():
    if request.method == "GET":
        if 'user_id' in session:
            if session["is_sponsor"]:
                return render_template('create_campaign.html')
            flash('Invalid user', 'danger')
            return redirect('/login')
        flash('Please login first', 'danger')
        return redirect('/login')
    if request.method == "POST":
        if 'user_id' in session:
            if session["is_sponsor"]:
                name = request.form.get('name')
                description = request.form.get('description')
                end_date = request.form["deadline"]
                budget = request.form.get('budget')
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                visibility = request.form.get('visibility')
                goals = request.form.get('goals')
                sponsor_id = session["user_id"]
                campaign = Campaign(name=name, description=description, end_date=end_date_obj, budget=budget,sponsor_id=sponsor_id, visibility=visibility, goals=goals)
                db.session.add(campaign)
                db.session.commit()
                flash('Your campaign has been created!', 'success')
                return redirect("/sponsor/campaigns")
            flash('Invalid user', 'danger')
            return redirect('/login') 
        flash('Please login first', 'danger')
        return redirect('/login')


@app.route("/<user_type>/campaigns/<int:campaign_id>", methods=['GET', 'POST'])
def campaign(user_type, campaign_id):
    if request.method == "GET":
        if 'user_id' in session:
            if user_type=="sponsor" and session["is_sponsor"]:
                campaign = Campaign.query.get_or_404(campaign_id)
                ad_requests = AdRequest.query.filter(AdRequest.campaign_id==campaign_id).all()
                return render_template(user_type + '_view_campaign.html', campaign=campaign, ad_requests=ad_requests)
            if user_type=="influencer" and session["is_influencer"]:
                campaign = Campaign.query.get_or_404(campaign_id)
                ad_requests = AdRequest.query.filter(AdRequest.campaign_id==campaign_id, AdRequest.influencer_id==session["user_id"]).all()
                return render_template(user_type + '_view_campaign.html', campaign=campaign, ad_requests=ad_requests)
            flash('Invalid user', 'danger')
            return redirect('/login')
        flash('Please login first', 'danger')
        return redirect('/login')



#creating a route to edit the created campaign by the sponsor
@app.route("/sponsor/campaigns/<int:campaign_id>/edit", methods=['GET', 'POST'])
def campaign_edit(campaign_id):
    if request.method == "GET":
        if 'user_id' in session:
            if session["is_sponsor"]:
                campaign = Campaign.query.get_or_404(campaign_id)
                return render_template('edit_campaign.html', campaign=campaign)
            flash('Invalid user', 'danger')
            return redirect('/login')
        flash('Please login first', 'danger')
        return redirect('/login')
    if request.method=="POST":
        if 'user_id' in session:
            if session["is_sponsor"]:
                name = request.form.get('name')
                description = request.form.get('description')
                end_date = request.form["deadline"]
                budget = request.form.get('budget')
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                visibility = request.form.get('visibility')
                goals = request.form.get('goals')
                campaign = Campaign.query.get_or_404(campaign_id)
                campaign.name = name
                campaign.description = description
                campaign.end_date = end_date_obj
                campaign.budget = budget
                campaign.visibility = visibility
                campaign.goals = goals
                db.session.commit()
                flash('Your campaign has been updated', 'success')
                return redirect("/sponsor/campaigns")
            flash('Invalid user', 'danger')
            return redirect('/login') 
        flash('Please login first', 'danger')
        return redirect('/login')


#creating a route to delete the campaign created by the sponsor
@app.route("/sponsor/campaigns/<int:campaign_id>/delete", methods=['GET', 'POST'])
def campaign_delete(campaign_id):
    if request.method == "GET":
        if 'user_id' in session:
            if session["is_sponsor"]:
                campaign = Campaign.query.get_or_404(campaign_id)
                db.session.delete(campaign)
                db.session.commit()
                flash('Your campaign has been deleted', 'success')
                return redirect("/sponsor/campaigns")
            flash('Invalid user', 'danger')
            return redirect('/login')
        flash('Please login first', 'danger')
        return redirect('/login')
    

#creating a route to create ad requests inside a particular campaign by the sponsor
@app.route("/sponsor/campaigns/<int:campaign_id>/create_adrequest", methods=['GET', 'POST'])
def create_adrequest(campaign_id):
    if request.method == "GET":
        if 'user_id' in session:
            if session["is_sponsor"]:
                influencers = User.query.filter_by(is_influencer=True).all()
                return render_template('create_adrequest.html', campaign_id=campaign_id,influencers=influencers)
            flash('Invalid user', 'danger')
            return redirect('/login')
        flash('Please login first', 'danger')
        return redirect('/login')
    if request.method=="POST":
        if 'user_id' in session:
            if session["is_sponsor"]:
                influencer_name = request.form.get("influencer_name")
                influencer_id = User.query.filter_by(name=influencer_name).first().id
                messages = request.form.get('messages')
                requirements = request.form.get('requirements')
                payment_amount = request.form.get('payment_amount')
                ad_request = AdRequest(campaign_id = campaign_id, influencer_id=influencer_id, messages=messages, requirements=requirements, payment_amount=payment_amount)
                db.session.add(ad_request)
                db.session.commit()
                flash('Your ad request has been created and sent to selected influencer', 'success')
                return redirect("/sponsor/campaigns/"+str(campaign_id)+"/adrequests")
            flash('Invalid user', 'danger')
            return redirect('/login') 
        flash('Please login first', 'danger')
        return redirect('/login')


#creating a route to view the ad requests created by the sponsor inside a particular campaign
@app.route("/sponsor/campaigns/<int:campaign_id>/adrequests", methods=['GET', 'POST'])
def adrequests(campaign_id):
    if request.method == "GET":
        if 'user_id' in session:
            if session["is_sponsor"]:
                ad_requests = AdRequest.query.join(AdRequest.influencer).filter(AdRequest.campaign_id == campaign_id).all()
                return render_template('all_adrequests.html', ad_requests=ad_requests, campaign_id=campaign_id)
            flash('Invalid user', 'danger')
            return redirect('/login')
        flash('Please login first', 'danger')
        return redirect('/login')
    
#creating a route to edit the ad requests created by the sponsor inside a particular campaign
@app.route("/sponsor/campaigns/<int:campaign_id>/adrequests/<int:ad_request_id>/edit", methods=['GET', 'POST'])
def adrequest_edit(campaign_id, ad_request_id):
    if request.method == "GET":
        if 'user_id' in session:
            if session["is_sponsor"]:
                adrequest = AdRequest.query.get_or_404(ad_request_id)
                influencer_id = adrequest.influencer_id
                influencer_name = User.query.get_or_404(influencer_id).name
                return render_template('edit_adrequest.html', adrequest=adrequest, ad_request_id=ad_request_id, campaign_id=campaign_id, influencer_name=influencer_name)
            flash('Invalid user', 'danger')
            return redirect('/login')
        flash('Please login first', 'danger')
        return redirect('/login')
    if request.method=="POST":
        if 'user_id' in session:
            if session["is_sponsor"]:
                messages = request.form.get('messages')
                requirements = request.form.get('requirements')
                payment_amount = request.form.get('payment_amount')
                ad_request = AdRequest.query.get_or_404(ad_request_id)
                ad_request.messages = messages
                ad_request.requirements = requirements
                ad_request.payment_amount = payment_amount
                db.session.commit()
                flash('Your ad request has been updated', 'success')
                return redirect("/sponsor/campaigns/" + str(campaign_id)+"/adrequests")
            flash('Invalid user', 'danger')
            return redirect('/login')
        flash('Please login first', 'danger')
        return redirect('/login')
    

#creating app route to delete an ad request created by sponsor inside a particular campaign
@app.route("/sponsor/campaigns/<int:campaign_id>/adrequests/<int:ad_request_id>/delete", methods=['GET', 'POST'])
def adrequest_delete(campaign_id, ad_request_id):
    if request.method == "GET":
        if 'user_id' in session:
            if session["is_sponsor"]:
                ad_request = AdRequest.query.get_or_404(ad_request_id)
                db.session.delete(ad_request)
                db.session.commit()
                flash('Your ad request has been deleted', 'success')
                return redirect("/sponsor/campaigns/" + str(campaign_id)+"/adrequests")
            flash('Invalid user', 'danger')
            return redirect('/login')
        flash('Please login first', 'danger')
        return redirect('/login')
    


#create route to accept an ad request by the influencer
@app.route("/adrequests/<int:ad_request_id>/accept", methods=['GET', 'POST'])
def adrequest_accept(ad_request_id):
    if request.method == "GET":
        if 'user_id' in session:
            if session["is_influencer"]:
                ad_request = AdRequest.query.get_or_404(ad_request_id)
                if ad_request.influencer_id == session["user_id"]:
                    ad_request.status_adreq = "accepted"
                    db.session.commit()
                    flash('Your have successfully accepted the ad request', 'success')
                    return redirect("/influencer/dashboard")
                flash('Invalid user', 'danger')
                return redirect('/login')
            if session["is_sponsor"]:
                ad_request = AdRequest.query.get_or_404(ad_request_id)
                if ad_request.created_by == "influencer":
                    ad_request.status_adreq = "accepted"
                    db.session.commit()
                    flash('Your have successfully accepted the ad request', 'success')
                    return redirect("/sponsor/campaigns")
                flash('Request not sent by Influencer', 'danger')
                return redirect('/login')
            flash('Invalid user', 'danger')
            return redirect('/login')
        flash('Please login first', 'danger')
        return redirect('/login')



@app.route("/adrequests/<int:ad_request_id>/reject", methods=['GET', 'POST'])
def adrequest_reject(ad_request_id):
    if request.method == "GET":
        if 'user_id' in session:
            if session["is_influencer"]:
                ad_request = AdRequest.query.get_or_404(ad_request_id)
                if ad_request.influencer_id == session["user_id"]:
                    ad_request.status_adreq = "rejected"
                    db.session.commit()
                    flash('Your have successfully accepted the ad request', 'success')
                    return redirect("/influencer/dashboard")
                flash('Invalid user', 'danger')
                return redirect('/login')
            if session["is_sponsor"]:
                ad_request = AdRequest.query.get_or_404(ad_request_id)
                if ad_request.created_by == "influencer":
                    ad_request.status_adreq = "rejected"
                    db.session.commit()
                    flash('Your have successfully accepted the ad request', 'success')
                    return redirect("/sponsor/campaigns")
                flash('Request not sent by Influencer', 'danger')
                return redirect('/login')
            flash('Invalid user', 'danger')
            return redirect('/login')
        flash('Please login first', 'danger')
        return redirect('/login')




#create a route to view all the influencers by the sponsor
@app.route("/sponsor/influencers", methods=['GET'])
def view_influencers():
    if 'user_id' in session:
        if session["is_sponsor"]:
            search_query=request.args.get('search_query')
            if search_query:
                search_filter = f"%{search_query}%"
                influencers = User.query.filter(User.is_influencer == True,(User.name.ilike(search_filter) | User.inf_category.ilike(search_filter) | User.inf_niche.ilike(search_filter))).all()
            else:
                influencers = User.query.filter_by(is_influencer=True).all()
            return render_template('view_influencers.html', influencers=influencers)
        flash('Invalid user', 'danger')
        return redirect('/login')
    flash('Please login first', 'danger')
    return redirect('/login')


#create app route to view the profile of influencer by the sponsor
@app.route("/sponsor/influencers/<int:influencer_id>", methods=['GET', 'POST'])
def influencer_profile(influencer_id):
    if request.method == "GET":
        if 'user_id' in session:
            if session["is_sponsor"]:
                if User.query.get_or_404(influencer_id).is_influencer:
                    influencer = User.query.get_or_404(influencer_id)
                    return render_template('influencer_profile.html', influencer=influencer)
                flash('Invalid user', 'danger')
                return redirect('/login')
            flash('Invalid user', 'danger')
            return redirect('/login')
        flash('Please login first', 'danger')
        return redirect('/login')





@app.route('/influencer/send_ad_request/<int:campaign_id>', methods=["GET",'POST'])
def send_ad_request(campaign_id):
    if request.method == "GET":
        if 'user_id' in session:
            if session["is_influencer"]:
                return render_template('send_adrequest.html', campaign_id=campaign_id)
            flash('Invalid user', 'danger')
            return redirect('/login')
        flash('Please login first', 'danger')
        return redirect('/login')
    if request.method=="POST":
        if 'user_id' in session and session['is_influencer']:
            messages = request.form.get('messages')
            requirements = request.form.get('requirements')
            payment_amount = request.form.get('payment_amount')
            new_ad_request = AdRequest(campaign_id=campaign_id,influencer_id=session['user_id'],messages=messages,requirements= requirements,payment_amount=payment_amount, created_by='influencer')
            db.session.add(new_ad_request)
            db.session.commit()
            flash('Ad request sent successfully', 'success')
            return redirect(url_for('dashboard', user_type='influencer'))
        flash('You need to be logged in as an influencer to send an ad request', 'danger')
        return redirect('/login')





@app.route("/influencer/campaigns/<int:campaign_id>/adrequests", methods=['GET', 'POST'])
def influencer_adrequests(campaign_id):
    if request.method == "GET":
        if 'user_id' in session:
            if session["is_influencer"]:
                campaign_name = Campaign.query.get_or_404(campaign_id).name
                ad_requests = AdRequest.query.join(AdRequest.campaign).filter(AdRequest.campaign_id == campaign_id,AdRequest.influencer_id == session["user_id"]).all()
                return render_template('influencer_adrequests.html', ad_requests=ad_requests, campaign_id=campaign_id, campaign_name = campaign_name)
            flash('Invalid user', 'danger')
            return redirect('/login')
        flash('Please login first', 'danger')
        return redirect('/login')









if __name__ == '__main__':
    app.run(debug=True)