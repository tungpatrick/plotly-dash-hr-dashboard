import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import matplotlib.pyplot as plt
plt.style.use("tableau-colorblind10")

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True
#
# colors = {
#     'background': 'white',
#     'text': '#7FDBFF'
# }

def generate_table(dataframe):
    return html.Div([
        html.Div(
            html.Table(
                # Header
                [html.Tr([html.Th(col) for col in dataframe.columns])] +

                # Body
                [html.Tr([
                    html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
                ]) for i in range(len(dataframe))]
            ), style={"width":"100%", "overflow":"scroll"}
        )
    ], style={"height": "100%"})


# data = go.Bar(y=employee_source.index,
#              x=employee_source.values, orientation="h")
#
# layout = go.Layout(title="Recruitment Source",
#                   plot_bgcolor="rgb(230,230,230)", bargap=0.2)
#
# fig = go.Figure(data=[data], layout=layout)

df = pd.read_csv("data/HRDataset_v9.csv")

employee_source = df["Employee Source"].value_counts(ascending=True)

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])

recruit = html.Div([
    html.Div([
        html.H1("HR Dashboard", style={"textAlign": "center"}),
        html.Img(src="assets/logo.png")
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
            id="filter_value",
            options = [
                {"label": "Department", "value": "Department"},
                {"label": "State", "value": "State"}
            ], value="Department"
        )
    ]),

    html.Div([
        html.Div([
            dcc.Graph(
                id="Recruitment Source by Department",
                figure = px.histogram(df, x="Employee Source", color="Department",
                    histfunc="count", barnorm="percent", barmode="group", orientation="v",
                    title="Details by Department").update_yaxes(title="Percentage of Recruitments"))
                ])
    ], className="row")
])

data = html.Div([
    generate_table(df)
])

data_table = html.Div([
    dash_table.DataTable(
        id = "datatable-paging",
        columns = [{"id": c, "name": c} for c in df.columns],
        style_table = {"overflowX": "scroll",
                        "maxHeight": "100%"},
        style_cell={
            "whiteSpace": "normal",
            "overflow": "hidden",
            "textOverflow": "ellipses",
            "textAlign": "left"
        },
        style_header = {"fontWeight": "bold"},
        css = [{"selector": ".dash-cell div.dash-cell-value",
                "rule": "display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;"}],
        page_current = 0,
        page_size = 15,
        page_action = "custom"
    )
], style={"width": "100%"})

@app.callback(Output("datatable-paging", "data"),
            [Input("datatable-paging", "page_current"),
             Input("datatable-paging", "page_size")])
def update_table(page_current, page_size):
    return df.iloc[
        page_current*page_size:(page_current+1)*page_size
    ].to_dict("records")


@app.callback(Output("Recruitment Source by Department", "figure"),
            [Input("filter_value", "value")])
def update_recruit_source(filter_value_name):
    figure = px.histogram(df, x="Employee Source", color=filter_value_name,
        histfunc="count", barnorm="percent", barmode="group", orientation="v",
        title="Details by {}".format(filter_value_name)).update_yaxes(title="Percentage of Recruitments")
    return figure

# update page
@app.callback(Output("page-content", "children"),
            [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/":
        return recruit
    elif pathname == "/data/":
        return data
    elif pathname == "/data-table/":
        return data_table
    else:
        return 404

if __name__ == '__main__':
    app.run_server(debug=True)
