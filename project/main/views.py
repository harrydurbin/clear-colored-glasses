# project/main/views.py


#################
#### imports ####
#################
# from flask_bootstrap import Bootstrap
from flask import render_template, Blueprint, url_for, \
    redirect, flash, request
from flask.ext.login import login_user, logout_user, \
    login_required, current_user

from project.models import User,Event
# from project.email import send_email
from project import db, bcrypt, app
# from .forms import LoginForm, RegisterForm, ChangePasswordForm


################
#### config ####
################
# bootstrap = Bootstrap(app)
main_blueprint = Blueprint('main', __name__,)


################
#### routes ####
################

@main_blueprint.route('/')
@login_required
def home():
    return render_template('main/index.html')


@main_blueprint.route("/events/",methods=['GET','POST'])
@login_required
def events():
    if request.form:
        event = Event(desc=request.form.get("desc"),want=request.form.get("want"),
        likelihood=request.form.get("likelihood"),happened=request.form.get("happened"))
        db.session.add(event)
        db.session.commit()
        flash('The event has been created.')
        events = Event.query.all()
        return render_template('main/events.html',events=events)
    event = Event(desc=request.form.get("desc"))
    events = Event.query.all()
    return render_template('main/events.html',events=events)


@main_blueprint.route("/events/update/", methods=["POST"])
def update():
    newdesc = request.form.get("newdesc")
    olddesc = request.form.get("olddesc")
    newhappened = request.form.get("newhappened")
    oldhappened = request.form.get("oldhappened")
    event = Event.query.filter_by(desc=olddesc).first()
    event.happened = newhappened
    db.session.commit()
    flash('The event has been updated.')
    return redirect("main/events")


@main_blueprint.route("/events/delete", methods=["POST"])
def delete():
    desc = request.form.get("desc")
    event = Event.query.filter_by(desc=desc).first()
    db.session.delete(event)
    db.session.commit()
    return redirect("main/events")
