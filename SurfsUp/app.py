# Import the dependencies.
 #import dependencies
import numpy as np

import datetime as dt
from dateutil.relativedelta import relativedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
        f"NOTICE:<br/>"
        f"Please input the query date in ISO date format(YYYY-MM-DD),<br/>"
        f"and the start date should not be later than 2017-08-23."
    )

#route /api/v1.0/precipitation

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB and fetch precipitation and date from Measurement table.
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    
    # Create a dictionary from the row data and append to a list of precipitation
    precipitation_list= []
    for date, prcp in results:
        date_prcp_dict = {}
        date_prcp_dict[date] = prcp
        precipitation_list.append(date_prcp_dict)

    return jsonify(precipitation_list)

#route /api/v1.0/stations

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB 
    session = Session(engine) 
    #query all stations name
    results=session.query(Station.name).all()
    session.close()
    
    #convert to normal list
    all_stations=list(np.ravel(results))
    
    return jsonify(all_stations)
    
#route /api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def tempature():
    
    #Query the dates and temperature observations of the most-active station for the previous year of data.
    session=Session(engine)
    a_year_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    results=session.query(Measurement.date , Measurement.tobs).filter(Measurement.station == "USC00519281").filter(Measurement.date >= a_year_date).all()
    session.close()
    #Return a JSON list of temperature observations for the previous year.
    all_temp=[]
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        all_temp.append(tobs_dict)     
    return jsonify(all_temp)




@app.route('/api/v1.0/<start>')
def get_t_start(start):
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    all_tobs= []
    for min,avg,max in result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route('/api/v1.0/<start>/<stop>')
def get_temp_start_stop(start,stop):
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    all_tobs = []
    for min,avg,max in result:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

if __name__ == '__main__':
    app.run(debug=True)