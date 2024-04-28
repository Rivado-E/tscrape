import pandas as pd
from datetime import datetime

df = pd.read_csv("sub_sections.csv")


def query_rows_by_start_time_gen(start_time, data=df):
    start_time_dt = datetime.strptime(start_time, "%I:%M%p").time()
    return data[data['start_time'].apply(lambda x: datetime.strptime(x, "%I:%M%p").time() == start_time_dt)].to_dict(orient="records")


def verify_conflict_gen(start_time, end_time, data=df):
    start_time_dt = datetime.strptime(start_time, "%I:%M%p").time()
    end_time_dt = datetime.strptime(end_time, "%I:%M%p").time()
    first = data[data['start_time'].apply(lambda x: datetime.strptime(x, "%I:%M%p").time() <= start_time_dt)]
    second = first[first['end_time'].apply(lambda x: datetime.strptime(x, "%I:%M%p").time() >= end_time_dt)]
    return second.to_dict(orient="records")


def subset_school(school, data=df):
    return data[data['course_code'].apply(lambda x: school in x)]


def query_rows_by_start_time(start_time, school, data=df):
    start_time_dt = datetime.strptime(start_time, "%I:%M%p").time()
    return data[data['start_time'].apply(lambda x: datetime.strptime(x, "%I:%M%p").time() == start_time_dt)].to_dict(orient="records")


def verify_conflict(start_time, end_time, school, data=df):
    data = subset_school(school, data)
    start_time_dt = datetime.strptime(start_time, "%I:%M%p").time()
    end_time_dt = datetime.strptime(end_time, "%I:%M%p").time()
    first = data[data["start_time"].apply(lambda x: datetime.strptime(x, "%I:%M%p").time() < end_time_dt)]
    first = first[first["end_time"].apply(lambda x: datetime.strptime(x, "%I:%M%p").time() > start_time_dt)]
    return first.to_dict(orient="records")
