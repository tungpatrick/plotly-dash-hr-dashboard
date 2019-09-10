import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#
# colors = {
#     'background': 'white',
#     'text': '#7FDBFF'
# }

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )



# data = go.Bar(y=employee_source.index,
#              x=employee_source.values, orientation="h")
#
# layout = go.Layout(title="Recruitment Source",
#                   plot_bgcolor="rgb(230,230,230)", bargap=0.2)
#
# fig = go.Figure(data=[data], layout=layout)

df = pd.read_csv("data/HRDataset_v9.csv")

employee_source = df["Employee Source"].value_counts(ascending=True)

app.layout = html.Div(children=[

    html.Div([
        html.H1("HR Dashboard", style={"textAlign": "center"}),
        html.Img(src="assets/logo.png"),
        html.P("Note: All the data represented here is mock data.", style={"textAlign":"center"}),
    ], className="banner"),

    html.Div([
        dcc.Graph(
            id="Recruitment Source",
            figure = px.histogram(df, y="Employee Source", histfunc="count", orientation="h",
                       title="Recruitment Source").update_yaxes(categoryorder="total ascending")\
                        .update_xaxes(title="Number of Recruitments")
        )
    ], className="row"),

    html.Div([
        html.Label("Filter by:"),
        dcc.Dropdown(
            options = [
                {"label": "Department", "value": "Department"},
                {"label": "Location", "value": "Location"}
            ]
        )
    ]),

    html.Div([
        html.Div([
            dcc.Graph(
                id="Recruitment Source by Department",
                figure = px.histogram(df, x="Employee Source", color="Department",
                           histfunc="count", barmode="group", orientation="v",
                           title="Details by Department").update_yaxes(title="Number of Recruitments"))
                ])
    ], className="row"),

    html.Hr(),
    generate_table(df)

])

if __name__ == '__main__':
    app.run_server(debug=True)
