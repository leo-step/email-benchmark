import os
from flask import Flask, redirect, url_for, render_template, request
from models import db, Email, Label
from datetime import datetime
import json

app = Flask(__name__)

# Ensure the database file is created in a 'data' directory
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data', 'train.db')

db.init_app(app)

# Create the database if it doesn't exist
with app.app_context():
    if not os.path.exists(os.path.join(basedir, 'data', 'train.db')):
        db.create_all()  # This will create the tables based on your models
        with open('data/train.json') as f:
            emails = json.load(f)

            for item in emails:
                email = Email(
                    id=item['_id'],
                    text=item['text'],
                    time=item['time']
                )
                db.session.add(email)

            db.session.commit()

@app.route('/')
def index():
    email = Email.query.filter_by(discarded=False).outerjoin(Label).filter(Label.id.is_(None)).first()

    if email:
        email_date = datetime.fromtimestamp(email.time).strftime('%A, %m-%d-%Y %H:%M')
        return render_template('index.html', email=email, email_date=email_date)
    else:
        return "All emails have been processed!"

@app.route('/label', methods=['POST'])
def label():
    email_id = request.form['email_id']
    action = request.form['action']
    email = Email.query.get(email_id)

    if action == 'discard':
        email.discarded = True
    else:
        # Process labels
        events = request.form.getlist('events[]')
        start_datetimes = request.form.getlist('start_datetimes[]')
        end_datetimes = request.form.getlist('end_datetimes[]')

        for event_name, start_dt, end_dt in zip(events, start_datetimes, end_datetimes):
            label = Label(
                email_id=email.id,
                event_name=event_name,
                start_datetime=datetime.strptime(start_dt, '%Y-%m-%dT%H:%M'),
                end_datetime=datetime.strptime(end_dt, '%Y-%m-%dT%H:%M')
            )
            print(label.start_datetime, label.end_datetime)
            db.session.add(label)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
