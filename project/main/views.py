# project/main/views.py


#################
#### imports ####
#################
# from flask_bootstrap import Bootstrap
from flask import render_template, Blueprint, url_for, \
    redirect, flash, request
from flask.ext.login import login_user, logout_user, \
    login_required, current_user

# import pandas as pd
import sqlite3
import pandas as pd
import datetime

from project.models import User,Event, Score
# from project.email import send_email
from project import db, bcrypt, app
# from .forms import LoginForm, RegisterForm, ChangePasswordForm

from bokeh.plotting import figure, show, output_file, output_notebook
from bokeh.palettes import Spectral11, colorblind, Inferno, BuGn, brewer
from bokeh.models import HoverTool, value, LabelSet, Legend, ColumnDataSource,LinearColorMapper,BasicTicker, PrintfTickFormatter, ColorBar
import json
import bokeh
from bokeh.plotting import figure, gridplot
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8

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
    # userid = User.get_id
    if request.form:
        event = Event(desc=request.form.get("desc"),want=request.form.get("want"),
        likelihood=request.form.get("likelihood"),happened=request.form.get("happened"),author=current_user._get_current_object())
        db.session.add(event)
        db.session.commit()
        flash('The event has been created.')
        events = Event.query.all()
        events = Event.query.filter_by(user_id = current_user.id)
        return render_template('main/events.html',events=events)

    event = Event(desc=request.form.get("desc"))
    events = Event.query.filter_by(user_id = current_user.id)
    return render_template('main/events.html',events=events)


@main_blueprint.route("/events/update", methods=["POST"])
def update():
    newid = request.form.get("newid")
    oldid = request.form.get("oldid")
    newdesc = request.form.get("newdesc")
    olddesc = request.form.get("olddesc")
    newwant = request.form.get("newwant")
    oldwant = request.form.get("oldwant")
    newlikelihood = request.form.get("newlikelihood")
    oldlikelihood = request.form.get("oldlikelihood")
    newhappened = request.form.get("newhappened")
    oldhappened = request.form.get("oldhappened")

    event = Event.query.filter_by(id=oldid).first()
    event.happened = newhappened
    event.desc = newdesc
    event.want = newwant
    event.likelihood = newlikelihood

    db.session.commit()
    flash('The event has been updated.')
    return redirect("events")


@main_blueprint.route("/events/delete", methods=["POST"])
def delete():
    desc = request.form.get("desc")
    event = Event.query.filter_by(desc=desc).first()
    db.session.delete(event)
    db.session.commit()
    return redirect("events")

@main_blueprint.route("/evaluation/",methods=['GET'])
@login_required
def evaluation():
    events = Event.query.filter_by(user_id = current_user.id).filter(
    Event.happened.like('Yes') | Event.happened.like('No'))

    db_file = "project/data-dev.sqlite"
    con = sqlite3.connect(db_file)
    cur = con.cursor()
    query = "SELECT * FROM Event WHERE user_id = ? and happened != 'Not yet';"
    param = (current_user.id,)
    df  = pd.read_sql_query(query, con=con, params = param)

    def is_accurate(x):
        if x.likelihood > 50 and x.happened==1:
            return 1
        elif x.likelihood < 50 and x.happened==0:
            return 0
        else:
            return 0.5

    if df.happened.count()>0:
        df.happened = df.happened.replace('No',0)
        df.happened = df.happened.replace('no',0)
        df.happened = df.happened.replace('Yes',1)
        df.happened = df.happened.replace('yes',1)
        # df['accuracy'] =df['name'].map(capitalizer)
        df['accuracy'] = df.apply(is_accurate, axis=1)
        expected = int(round(df.likelihood.mean()/100,2)*100)
        actual = int(round((df.happened.sum()) / (df.happened.count()),2)*100)
        reality_score = int(round((expected - actual),2))
        accuracy = int(round((df.accuracy.sum()) / (df.accuracy.count()),2)*100)
        num = df.happened.count()
        scored_on = datetime.datetime.now()

        score = Score(scored_on=scored_on,reality=reality_score,accuracy=accuracy,num=num,author=current_user._get_current_object())
        db.session.add(score)
        db.session.commit()

        # plot scores
        query1 = "SELECT * FROM Score WHERE user_id = ?;"
        param = (current_user.id,)
        # cur.execute(query1,param)
        # scores = cur.fetchall()
        df_scores  = pd.read_sql_query(query1, con=con, params = param)
        df_scores['dt']=pd.to_datetime(df_scores.scored_on)
        TOOLS = 'crosshair,save,pan,box_zoom,reset,wheel_zoom'
        p = figure(title="", y_axis_type="linear",x_axis_type='datetime', tools = TOOLS,width=1000, height=300)
        p.line(df_scores['dt'], df_scores.accuracy, legend="Accuracy %", line_color="magenta", line_width = 3)
        p.line(df_scores['dt'], df_scores.reality, legend="Differential %", line_color="blue", line_width = 3)
        p.circle(df_scores['dt'], df_scores.accuracy, line_color='magenta',fill_color="white", size=8)
        p.circle(df_scores['dt'], df_scores.reality, line_color='blue',fill_color="white", size=8)
        # p.line(stolen_property['Date'], stolen_property.IncidntNum, legend="stolen_property", line_color="blue", line_width = 3)
        p.legend.location = "top_left"
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Value'
        p.sizing_mode="scale_both"
        # output_file("multiline_plot.html", title="Multi Line Plot")
        # show(p)  # open a browser
        # script, div = components(p)
        # return render_template('main/evaluation.html',script1=script,div1=div)
        # grab the static resources
        js_resources = INLINE.render_js()
        css_resources = INLINE.render_css()

        # render template
        script, div = components(p)
        html = render_template(
            'main/evaluation.html',
            events=events,
            expected=expected,
            actual=actual,
            score=reality_score,
            accuracy=accuracy,
            plot_script=script,
            plot_div=div,
            js_resources=js_resources,
            css_resources=css_resources,
        )
        return encode_utf8(html)
        # return render_template('main/evaluation.html',events=events,expected=expected,actual=actual,score=reality_score,accuracy=accuracy,script=script,div=div)
    return render_template('main/evaluation1.html')

@main_blueprint.route("/about/",methods=['GET'])
def about():
    return render_template('main/about.html')

@main_blueprint.route("/gauge/",methods=['GET'])
def gauge():
    return render_template('main/gauge.html')
