import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#Routes

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#flask set up
app = Flask(__name__)

#Home page. #List all routes that are available.
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd</br>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd/<br/>"
    )


#percipitation route
@app.route("/api/v1.0/precipitation")
def percipitation():
    """Convert the query results to a dictionary using date as the key and prcp as the value"""
    prevyear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    session = Session(engine)
    percipitation_query = session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date >= prevyear).all()
    session.close()

    #create dictionary
    
    precipitation = {date: prcp for date, prcp in percipitation_query}
    return jsonify(precipitation)

#station route
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    session = Session(engine)
    station_query = session.query(Station).all()
    session.close()


    #create dictionary and change jsonify
    stations_list = []
    for station in station_query:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        stations_list.append(station_dict)

    return jsonify(stations_list)

#temp route
@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most active station for the last year of data"""
    session = Session(engine)
    year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    active_station = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= year).\
        order_by(Measurement.date).all()
    session.close()

    ##create dictionary and change jsonify
    temp_list = []
    for station, date, tobs in active_station:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Date"] = date
        station_dict["Temp"] = tobs
        temp_list.append(station_dict)

    return jsonify(temp_list)


#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
@app.route("/api/v1.0/<start_date>")
def start_date(start_date):
    session = Session(engine)
    givendate_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    session.close()

    ##create dictionary and change jsonify
    dates = []                       
    for min, avg, max in givendate_query:
        date_dict = {}
        date_dict["Low Temp"] = min
        date_dict["Avg Temp"] = avg
        date_dict["High Temp"] = max
        dates.append(date_dict)
    return jsonify(dates)


###When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route('/api/v1.0/<start_date>/<end_date>/')
def dates(start_date, end_date):
    session = Session(engine)
    """Return the avg, max, min, temp over a specific time period"""
    dates_query = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    session.close()


    ##create dictionary and change jsonify
    date = []                       
    for min, avg, max in dates_query:
        dates_dict = {}
        dates_dict["Low Temp"] = min
        dates_dict["Avg Temp"] = avg
        dates_dict["High Temp"] = max
        date.append(dates_dict)
    return jsonify(date)


if __name__ == '__main__':
    app.run(debug=True)
    app.run()

   