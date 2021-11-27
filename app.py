import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#Routes

engine = create_engine("sqlite://../Resources/hawaii.sqlite")

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
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd/<br/>"
    )


#percipitation route
@app.route("/api/v1.0/precipitation")
def percipitation():
    """Convert the query results to a dictionary using date as the key and prcp as the value"""
    session = Session(engine)
    percipitation_query = session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date).all()
    session.close()

    #create dictionary
    prcpbydate = []
    for date in percipitation_query:
        precipitation_dict = {percipitation_query.date: percipitation_query.prcp}
        precipitation_dict["prcp"] = Measurement.prcp
        prcpbydate.append(precipitation_dict)
    return jsonify(prcpbydate)

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
    for obs in active_station:
        station_dict = {active_station.date: active_station.tobs, "Station": active_station.station}
        station_dict["Date"] = Measurement.date
        station_dict["Station"] = Measurement.station
        station_dict["Temp"] = int(Measurement.tobs)
        temp_list.append(station_dict)

    return jsonify(temp_list)


#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
@app.route("/api/v1.0/<start>")
def givendate(date):
    session = Session(engine)
    givendate_query = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= date).\
        group_by(Measurement.date).all()
    session.close()

    ##create dictionary and change jsonify
    dates = []                       
    for result in givendate_query:
        date_dict = {}
        date_dict["Date"] = givendate_query.date
        date_dict["Low Temp"] = givendate_query[1]
        date_dict["Avg Temp"] = givendate_query[2]
        date_dict["High Temp"] = givendate_query[3]
        dates.append(date_dict)
    return jsonify(dates)


###When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route('/api/v1.0/<start_date>/<end_date>/')
def dates(start_date, end_date):
    """Return the avg, max, min, temp over a specific time period"""
    dates_query = session.query(Measurement.date, func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).\
        group_by(Measurement.date).all()
    session.close()


    ##create dictionary and change jsonify
    dates = []                       
    for result in dates_query:
        date_dict = {}
        date_dict["Date"] = dates_query[0]
        date_dict["Low Temp"] = dates_query[1]
        date_dict["Avg Temp"] = dates_query[2]
        date_dict["High Temp"] = dates_query[3]
        dates.append(date_dict)
    return jsonify(dates)


if __name__ == '__main__':
    app.run(debug=True)