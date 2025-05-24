# import os
# import csv
# import pandas as pd
# from .client import make_request
#
# def get_data(station_code, start_date, end_date) -> pd.DataFrame:
#     from datetime import datetime
#     station_code = str(station_code)
#
#     if not isinstance(start_date, str):
#         start_date = start_date.strftime("%Y-%m-%d")
#     if not isinstance(end_date, str):
#         end_date = end_date.strftime("%Y-%m-%d")
#
#     url = (
#         f"https://mobility.api.opendatahub.com/v2/flat/ParkingStation/"
#         f"free,occupied/{start_date}/{end_date}"
#         f"?where=and%28sorigin.eq.FAMAS%2Cscode.eq.%22{station_code}%22%29"
#         f"&select=mvalue,mvalidtime,sname,scode,sorigin,tname&limit=-1"
#     )
#
#     response = make_request(url)
#     if response is None or not response.get("data"):
#         return pd.DataFrame(columns=["mvalidtime", "free", "occupied"])
#
#     csv_filename = "parking.csv"
#     data_dict = {}
#
#     for row in response["data"]:
#         ts, tname, mvalue = row.get("mvalidtime"), row.get("tname"), row.get("mvalue")
#         if ts and tname and mvalue is not None:
#             data_dict.setdefault(ts, {})[tname] = mvalue
#
#     with open(csv_filename, "w", newline="") as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(["mvalidtime", "free", "occupied"])
#         for ts, vals in data_dict.items():
#             writer.writerow([ts, vals.get("free"), vals.get("occupied")])
#
#     try:
#         return pd.read_csv(csv_filename)
#     except Exception as e:
#         print(f"CSV read error: {e}")
#         return pd.DataFrame(columns=["mvalidtime", "free", "occupied"])
