"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(app)

api = openaq.OpenAQ()


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'Record: {self.id}, {self.datetime}, {self.value}'


def get_results():
    """Fetch data from OpenAQ and return a list of tuples (datetime, value)."""
    status, body = api.measurements(parameter='pm25')
    results = [
        (result['date']['utc'], result['value']) for result in body['results']
    ]
    return results


@app.route('/')
def root():
    """Base view."""
    records = Record.query.filter(Record.value >= 10).all()
    results = [(record.datetime, record.value) for record in records]
    return f'Records: {str(results)}'


@app.route('/refresh')
def refresh():
    """Pull fresh data from OpenAQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    results = get_results()
    for datetime, value in results:
        record = Record(datetime=datetime, value=value)
        DB.session.add(record)
    DB.session.commit()
    return 'Data refreshed! Records updated.'


if __name__ == '__main__':
    app.run(debug=True)
