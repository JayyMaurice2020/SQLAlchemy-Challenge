# Dependencies
from flask import Flask, jsonify
import datetime as dt
from datetime import datetime, date, time
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Database setup, connection
connection_string = "sqlite:///Resources/hawaii.sqlite"
engine = create_engine(connection_string)

Base = automap_base()
Base.prepare(engine, reflect=True)

# Print all of the classes mapped to the Base
print(Base.classes.keys())

Measurement = Base.classes.measurement
Station = Base.classes.station


# Create app
app = Flask(__name__)

# List all routes that are available


@app.route("/")
def home():
    return """
        Available routes:<br/>
        /api/v1.0/precipitation<br/>
        /api/v1.0/stations<br/>
        /api/v1.0/tobs<br/>
        /api/v1.0/start=YYYY-MM-DD<br/>
        /api/v1.0/start=YYYY-MM-DD/end=YYYY-MM-DD;
    """

# Precipitation route


@app.route("/api/v1.0/precipitation")
def percipitation():
    """
        Return a dictionary using date as the key & prcp as the value
    """
    # Create session link from python to DB
    session = Session(engine)

    # Query results for dates & prcp
    latest_date = session.query(Measurement.date)\
        .order_by(Measurement.date.desc())\
        .first()
    end_date = dt.datetime(2017, 8, 23)
    target_date = dt.date(2017, 8, 23)
    delta = dt.timedelta(days=365)
    query_date = target_date - delta

    results = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= query_date)\
        .filter(Measurement.date <= end_date)\
        .all()

    session.close()

    precipitation_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation_data.append(prcp_dict)

    return jsonify(precipitation_data)

# Stations route


@app.route("/api/v1.0/stations")
def station():
    """
        Return a list of all stations from database.
    """
    session = Session(engine)
    results = session.query(Station.name).all()
    session.close()

    station_dict = list(np.ravel(results))

    return jsonify(station_dict)


# Tobs route


@app.route("/api/v1.0/tobs")
def tobs():
    """
        Return temperature observation of the most
        active station for the last year
    """
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == 'USC00519281')\
        .filter(Measurement.date.between('2016-08-23', '2017-08-23'))\
        .order_by(Measurement.date).all()
    session.close()

    temp_data = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temperature"] = tobs
        temp_data.append(tobs_dict)

    return jsonify(temp_data)

# Start Date route:


@app.route("/api/v1.0/start=<start>")
def start(start):
    """
        start (string): A date string in the format %Y-%m-%d
        Return a list of TMIN, TMAX, & TAVG for all dates >= to start date.
    """
    session = Session(engine)
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))\
        .filter(Measurement.date >= start_date).all()
    session.close()

    start_tobs_data = []
    for min, max, avg in results:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Max"] = max
        tobs_dict["Avg"] = avg
        start_tobs_data.append(tobs_dict)

    return jsonify(start_tobs_data)


if __name__ == '__main__':
    app.run(debug=True)