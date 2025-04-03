# Welcome to the Open Data Hub Bootcamp 2025!
This repo will guide you through the challenge 3, in which you will implement a prediction engine for parking areas.

The goal of this bootcamp is to foster our community around the Open Data Hub, to get to know each other, the technology, but also for you to just learn stuff and make friends. This is not a competition, so don't be afraid to make mistakes and try out new stuff. Our Open Data Hub team is there to help and support you.

You will also have an opportunity to present the results to the public at our upcoming event, the Open Data Hub Day

# The challenge
Your challenge will be to implement an prediction of parking station occupancy using time series data from the Open Data Hub.

# Tech stack
You are free to use whatever programming language best fits your group, but with it being a data analysis / stats heavy topic, python is probably a good choice

# Dataset
For this challenge you will use the parking dataset, which is part of the Open Data Hub's mobility domain.  
You can explore it using the
[databrowser](https://databrowser.opendatahub.com/dataset-overview/178ea911-cc54-418e-b42e-52cad18f1ec1) or our [analytics frontend](https://analytics.opendatahub.com/) (under "Parking")

The stations are of type `ParkingStation`.

Not all parking stations have their time series data publicly accessible, and not all have the same data types and fields.

To guarantee data consistency, you should limit your dataset to one or more `origins` by using the `where` filter. Stations from the same origin all have uniform metadata fields and data types.

Generally, our parking stations provide at a minimum the following fields:
- `smetadata.capacity` The maximum capacity
- datatype `occupied` the number of occupied spots 
- datatype `free` the number of free spots

# APIs
There are two APIs you will interact with:
- **Open Data Hub Time series API** [mobility.api.opendatahub.com](mobility.api.opendatahub.com)
 to retrieve the time series data both for training your algorithm and making the prediction
- **Keycloak** [auth.opendatahub.com/auth/](https://auth.opendatahub.com/auth/) to obtain an authorization token, needed for access to large time series datasets (not mandatory)

Note that for this challenge you will interact with the `Time Series / Mobility` APIs, and not it's sibling, the `Content / Tourism` domain

## Keycloak
Keycloak is an Open Source Identity and Access management server (keycloak.org).
We use it to authenticate and authorize our services via the OAuth2 standard.
For you, this boils down to making a REST call supplying your credentials (which we will provide to you), and you get back an authorization token.

You then have to pass this token as `Authorization: Bearer <token>` HTTP header on every call to our Open Data Hub APIs.
>[!IMPORTANT]
>If you don't pass a token, you are limited to 5 days of time series history per call, or 100 days if you pass a `Referer` http header.  
>Request beyond that limit will result in a HTTP 429 Too Many Requests
See [quota limits](https://github.com/noi-techpark/opendatahub-docs/wiki/Historical-Data-and-Request-Rate-Limits) and [Http Referer](https://github.com/noi-techpark/opendatahub-docs/wiki/Http-Referer)
## Time Series Objects and Concepts
Time series data takes the form of `Measurements` attached to `Stations`  

>[!NOTE]
>A measurement is a data point with a timestamp.

Each measurement has exactly one
- `mvalidtime`, the timestamp of the measurement
- `mvalue` the value of the measurement
- `mperiod`, the timeframe (in seconds) that the measurement references, and the periodicity with which it is updated. e.g. a temperature sensor that sends us it's data every 60 seconds has a period of 60.  
- `station`, a geographical point with an ID, name and some additional information. It's the location where measurements are made.
Fields referring to the station are prefixed with `s*`
- `data type`, which identifies what type of measurement it actually is. Is it a temperature in degrees Celsius? Is it the number of available cars? Is it the current occupancy of a parking lot?  
Fields referring to the data type are prefixed with `t*`

A **Station** might have multiple time series (list of measurements) of 0-n **Data types**, for example a weather station could have both `temperature` and `humidity` measurements.  
An e-charging station that we know exists, but doesn't provide any real time data, probably has no measurements at all.  
Stations may exist independently of measurements.
Stations have a `metadata` object, that contains additional information about the station.

This is a real world example of a parking station that has two data types, `free` and `occupied`, both with period 300. Some field's have been omitted for clarity's sake:
https://mobility.api.opendatahub.com/v2/tree/ParkingStation/*/latest?where=scode.eq.%22107%22,sactive.eq.true
```json
{
  "offset": 0,
  "data": {
    "ParkingStation": {
      "stations": {
        "107": {
          "sactive": true,
          "savailable": true,
          "scode": "107",
          "scoordinate": {
            "x": 11.351793,
            "y": 46.502958,
            "srid": 4326
          },
          "sdatatypes": {
            "free": {
              "tdescription": "free",
              "tmeasurements": [
                {
                  "mperiod": 300,
                  "mvalidtime": "2025-04-03 05:30:11.000+0000",
                  "mvalue": 144
                }
              ],
              "tname": "free",
              "ttype": "Instantaneous",
              "tunit": ""
            },
            "occupied": {
              "tdescription": "occupied",
              "tmeasurements": [
                {
                  "mperiod": 300,
                  "mvalidtime": "2025-04-03 05:30:11.000+0000",
                  "mvalue": 1
                }
              ],
              "tname": "occupied",
              "ttype": "Instantaneous",
              "tunit": ""
            }
          },
          "smetadata": {"capacity": 145, "municipality": "Bolzano - Bozen"},
          "sname": "P07 - Mareccio via C. de Medici",
          "sorigin": "FAMAS",
          "stype": "ParkingStation"
        }
      }
    }
  },
  "limit": 200
}
```
### Representation
All requests made against the Time Series API have to specify a `representation`, which is either `flat` or `tree`.  

`tree` displays the reponse in a structured tree format:
```
stationtype
  '─ station
    '─ datatype
      '─ [measurements]
```
`flat` flattens this tree structure, resulting in a list of measurements, where each measurement has it's station and datatype information repeated 

>[!TIP]
>Generally, `tree` is useful for initial exploration, while `flat` is better once you have tuned in your `where` and `select` parameters to give you exactly the data you want.

### More information
You can find more information on the API format here:  
[Swagger Ninja API](https://mobility.api.opendatahub.com)  
[Open Data Hub documentation](https://opendatahub.readthedocs.io/en/latest/mobility-tech.html)  
[Time series API README](https://github.com/noi-techpark/opendatahub-timeseries-api/blob/main/README.md)  