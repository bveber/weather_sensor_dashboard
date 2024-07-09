import os
import psycopg2
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output


# Connect to the PostgreSQL database
def get_data(sensor_id=None, start_date=None, end_date=None):
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    query = "SELECT * FROM sensor_data WHERE 1=1"
    params = []
    if sensor_id:
        query += " AND sensor_id = %s"
        params.append(sensor_id)
    if start_date:
        query += " AND time >= %s"
        params.append(start_date)
    if end_date:
        query += " AND time <= %s"
        params.append(end_date)
    df = pd.read_sql(query, conn, params=params)
    df["temperature_fahrenheit"] = df["temperature"] * 9 / 5 + 32
    df["time_tz"] = df["time"].dt.tz_convert("US/Central")
    conn.close()
    return df


app = Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Sensor Data Dashboard"),
        dcc.Dropdown(
            id="sensor_id",
            options=[
                {"label": "Sensor 1", "value": "1"},
                {"label": "Sensor 2", "value": "2"},
            ],
            placeholder="Select a sensor",
        ),
        dcc.DatePickerRange(
            id="date_range",
            start_date_placeholder_text="Start Date",
            end_date_placeholder_text="End Date",
        ),
        dcc.Graph(id="temperature_graph"),
        dcc.Graph(id="humidity_graph"),
    ]
)


@app.callback(
    [Output("temperature_graph", "figure"), Output("humidity_graph", "figure")],
    [
        Input("sensor_id", "value"),
        Input("date_range", "start_date"),
        Input("date_range", "end_date"),
    ],
)
def update_graph(sensor_id, start_date, end_date):
    df = get_data(sensor_id, start_date, end_date)
    temp_fig = px.line(
        df, x="time_tz", y="temperature_fahrenheit", title="Temperature Over Time"
    )
    humidity_fig = px.line(df, x="time_tz", y="humidity", title="Humidity Over Time")
    return temp_fig, humidity_fig


debug = False
dev_tools_hot_reload = False
if os.environ.get("ENV") == "dev":
    debug = True
    dev_tools_hot_reload = True

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8050,
        debug=debug,
        dev_tools_hot_reload=dev_tools_hot_reload,
    )
