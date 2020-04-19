import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

import datetime as dt
import numpy as np
import pandas as pd

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Create Session
#################################################
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List available API routes."""
    return (
        f"List available API routes.<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """The query results to a dictionary using date as the key and prcp as the value."""
    last_year = dt.date(2017, 8, 23) - dt.timedelta(365)    
    
    prcp_query = (
        session
        .query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date>=last_year)
        .all()
        )
  
    
    precipitation_list=[]
    for data in prcp_query:
        prcp_dict = {}
        prcp_dict[data[0]] = data[1]
        precipitation_list.append(prcp_dict)
    
    return jsonify(precipitation_list)


@app.route("/api/v1.0/stations")
def stations():
    """JSON list of stations from the dataset."""
    
    station = session.query(Station.name, Station.station).all()
    
    
    return jsonify(station)


@app.route("/api/v1.0/tobs")
def tobs():
    """The dates and temperature observations of the most active station for the last year of data."""
    last_year = dt.date(2017, 8, 23) - dt.timedelta(365)
    
    station_temp_obsrv=(session
                    .query(Measurement.date, Measurement.tobs)
                    .filter(Measurement.station == "USC00519281")
                    .filter(Measurement.date >= last_year)
                    .all()
                    )
 

    sto_list = []
    for data in station_temp_obsrv:
        sto_dict = {}
        sto_dict["date"] = data[0]
        sto_dict["prcp"] = data[1]
        sto_list.append(sto_dict)
    
    return jsonify(sto_list)
   


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [
        func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)
        ]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)