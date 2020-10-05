import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

import datetime as dt
from datetime import datetime
import numpy as np
import pandas as pd

from flask import Flask, jsonify



# import numpy as np
# import datetime as dt

# import sqlalchemy
# from sqlalchemy.ext.automap import automap_base
# from sqlalchemy.orm import Session
# from sqlalchemy import create_engine, func, distinct

# from flask import Flask, jsonify
# from datetime import datetime

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
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<h2>Welcome to Hawaii Weather and Precipitation Analysis API!!</h2>"
        f"<img src='https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcTO439TqwtP2-lT9BRYjiAFi2j-ji53dzKIrA&usqp=CAU'"
        f"<br/><br/><h3>Available Routes:</h3>"
        f"<ul>"
        f"<li><a href='http://127.0.0.1:5000/api/v1.0/precipitation'>Precipitation data</a><br/>"
        f"<i>Usage: Append /api/v1.0/precipitation to the URL </i></li><br/>"       
        f"<li><a href='http://127.0.0.1:5000/api/v1.0/stations'>Stations in the dataset</a><br/>"
        f"<i>Usage: Append /api/v1.0/stations to the URL </i></li><br/>"
        f"<li><a href='http://127.0.0.1:5000/api/v1.0/tobs'>Temperature observations of the most active station for the previous year </a><br/>"
        f"<i>Usage: Append /api/v1.0/tobs to the URL </i></li><br/>"
        f"<li><a href='http://127.0.0.1:5000/api/v1.0/2015-01-01'>Minimum, average and maximum temperatures for a given start date, as 2010-01-01</a><br/>"
        f"<i>Usage: Append a start date to URL such as /api/v1.0/startdate<br/>"
        f"Enter dates only between 2010-01-01 and 2017-08-23 </i></li><br/>"
        f"<li><a href='http://127.0.0.1:5000/api/v1.0/2015-01-01/2015-01-10'>Minimum, average and maximum temperatures for a given date range, as 2010-01-01/2010-01-10</a><br/>"
        f"<i>Usage: Append start and end dates to URL such as /api/v1.0/startdate/enddate<br/>"
        f"Enter dates only between 2010-01-01 and 2017-08-23</i></li><br/>"
        f"</ul>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    """The query results to a dictionary using date as the key and prcp as the value."""
    last_year = dt.date(2017, 8, 23) - dt.timedelta(365)    
    
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
    session = Session(engine)

    """JSON list of stations from the dataset."""
    station = session.query(Station.name, Station.station).all()

    session.close()

    return jsonify(station)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    """The dates and temperature observations of the most active station for the last year of data."""
    last_year = dt.date(2017, 8, 23) - dt.timedelta(365)
    
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
def temp_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return TMIN, TAVG, TMAX."""
    # Query most active station

    start_dt = datetime.strptime(start, "%Y-%m-%d")
    start_dt = datetime.date(start_dt)
    first_dt = datetime.strptime('2010-01-01', "%Y-%m-%d")
    first_dt = datetime.date(first_dt)
    last_dt = datetime.strptime('2017-08-23', "%Y-%m-%d")
    last_dt = datetime.date(last_dt)
    print("Start Date: ", start_dt)
    if ((start_dt > last_dt) | (start_dt < first_dt)): 
        return "Date not found in dataset"
    else:
    # Query minimum,average and maximum temperature for a given start date
        temps = (session
            .query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs))
            .filter(Measurement.date >= start_dt)).all()

        print(temps)
 
        session.close()

    # Create a dictionary from the row data and append to a list 
        temp_stats = []
        for temp in temps:
            temps_dict = {}
            temps_dict["Min.Temp"] = round(temps[0][0],2)
            temps_dict["Avg.Temp"] = round(temps[0][1],2)
            temps_dict["Max.Temp"] = round(temps[0][2],2)
            temp_stats.append(temps_dict)

        return jsonify(temps_dict)



@app.route("/api/v1.0/<start>/<end>")
def temp_date_range(start,end):
    
    session = Session(engine)

    """Return TMIN, TAVG, TMAX."""
    # Query most active station

    start_dt = datetime.strptime(start, "%Y-%m-%d")
    start_dt = datetime.date(start_dt)
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    end_dt = datetime.date(end_dt)
    print("Start Date: ", start_dt)
    print("End Date: ", end_dt)
    
    last_dt = datetime.strptime('2017-08-23', "%Y-%m-%d")
    last_dt = datetime.date(last_dt)
    first_dt = datetime.strptime('2010-01-01', "%Y-%m-%d")
    first_dt = datetime.date(first_dt)
    print("Start Date: ", start_dt)
    
    if ((start_dt > last_dt) | (start_dt < first_dt)): 
        return "Date not found in dataset"
    if ((end_dt > last_dt) | (end_dt < first_dt)): 
        return "Date not found in dataset"
    else:
    # Query minimum,average and maximum temperature for a given date range
        temps = (session
            .query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs))
            .filter(Measurement.date >= start_dt)
            .filter(Measurement.date <= end_dt)).all()

        print(temps)
 
        session.close()

    #Convert list of tuples into normal list
        #temp_stats = list(np.ravel(temps))

    # Create a dictionary from the row data and append to a list 
        temp_stats = []
        for temp in temps:
            temps_dict = {}
            temps_dict["Min.Temp"] = round(temps[0][0],2)
            temps_dict["Avg.Temp"] = round(temps[0][1],2)
            temps_dict["Max.Temp"] = round(temps[0][2],2)
            temp_stats.append(temps_dict)

        return jsonify(temps_dict)
        #return jsonify(temp_stats)



if __name__ == "__main__":
    app.run(debug=True)
