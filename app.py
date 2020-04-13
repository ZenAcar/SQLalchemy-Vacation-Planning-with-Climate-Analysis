import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

import datetime as dt
import numpy as np

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model

Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def Home():
    """List available API routes."""
    return (
        f"List available API routes.<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/start_end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """The query results to a dictionary using date as the key and prcp as the value."""
    last_year = dt.date(2017, 8, 23) - dt.timedelta(365)    
    session = Session(engine)
    prcp_query = (session
                .query(Measurement.date, Measurement.prcp)
                .filter(Measurement.date>dt.datetime(2016, 8, 23))
                .all())
    session.close()
    prcp_dict = {}
    for data in prcp_query:
        prcp_dict[data[0]] = data[1]
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    """JSON list of stations from the dataset."""
    station = session.query(Station.station).all()
    station_list = list(np.ravel(station))
    return jsonify(station_list)



@app.route("/api/v1.0/tobs")
def tobs():
    """The dates and temperature observations of the most active station for the last year of data."""
    last_year = dt.date(2017, 8, 23) - dt.timedelta(365)
    session = Session(engine)
    station_temp_obsrv=(session
                        .query(Measurement.tobs)
                        .filter(Measurement.station == "USC00519281")
                        .filter(Measurement.date >= last_year)
                        .all()
                        )
    session.close()
    return jsonify(station_temp_obsrv)


@app.route("/api/v1.0/<start>")
def startdate(start):
    session = Session(engine)
    result = (
        session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs),
        )
        .filter(Measurement.date >= start)
        .all()
    )
    session.close()
    return jsonify(startdate)


@app.route("/api/v1.0/start_end")
def start_and_end(start_end):
    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date > start, Measurement.date < end).all()
    session.close()
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, port=9999)