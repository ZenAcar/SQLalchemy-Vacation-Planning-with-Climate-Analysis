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
        f"/api/v1.0/<start></br>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """The query results to a dictionary using date as the key and prcp as the value."""
    last_year = dt.date(2017, 8, 23) - dt.timedelta(365)    
    session = Session(engine)
    prcp_query = (
        session
        .query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date>=last_year)
        .all()
        )
    session.close()
    
    precipitation_list=[]
    for data in prcp_query:
        prcp_dict = {}
        prcp_dict[data[0]] = data[1]
        precipitation_list.append(prcp_dict)
    
    return jsonify(precipitation_list)


@app.route("/api/v1.0/stations")
def stations():
    """JSON list of stations from the dataset."""
    session = Session(engine)
    station = session.query(Station.name, Station.station).all()
    session.close()
    
    return jsonify(station)


@app.route("/api/v1.0/tobs")
def tobs():
    """The dates and temperature observations of the most active station for the last year of data."""
    last_year = dt.date(2017, 8, 23) - dt.timedelta(365)
    session = Session(engine)
    station_temp_obsrv=(session
                    .query(Measurement.date, Measurement.tobs)
                    .filter(Measurement.station == "USC00519281")
                    .filter(Measurement.date >= last_year)
                    .all()
                    )
    session.close()

    sto_list = []
    for data in station_temp_obsrv:
        sto_dict = {}
        sto_dict["date"] = data[0]
        sto_dict["prcp"] = data[1]
        sto_list.append(sto_dict)
    
    return jsonify(sto_list)
   

@app.route("/api/v1.0/<start>")
def start_date(start=None):
    session = Session(engine) 
    start_guery= (
            session
            .query(
                func.min(Measurement.tobs), 
                func.avg(Measurement.tobs), 
                func.max(Measurement.tobs)
            )
            .filter(Measurement.date >= start_date)
            .all()
        )
    session.close()

    temp_list = []
    for Tmin, Tavg, Tmax in start_guery:
        temp_dict = {}
        temp_dict["Min Temp"] = Tmin
        temp_dict["Max Temp"] = Tmax
        temp_dict["Avg Temp"] = Tavg
        temp_list.append(temp_dict)
 
    return jsonify(temp_list)



@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start_date, end_date):
    session = Session(engine) 
    start_end_guery= (
            session
            .query(
                func.min(Measurement.tobs), 
                func.avg(Measurement.tobs), 
                func.max(Measurement.tobs)
            )
            .filter(Measurement.date >= start_date)
            .filter(Measurement.date <= end_date)
            .all()
        )
    session.close()

    start_end_list =[]
    for Tmin, Tavg, Tmax in start_end_guery:
        start_end_dict = {}
        start_end_dict["Min Temp"] = Tmin
        start_end_dict["Max Temp"] = Tmax
        start_end_dict["Avg Temp"] = Tavg
        start_end_list.append(start_end_dict)

    return jsonify(start_end_list)

if __name__ == "__main__":
    app.run(debug=True)