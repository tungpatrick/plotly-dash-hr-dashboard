import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

# data
df = pd.read_csv("data/data.csv")
df["Date of Hire"] = pd.to_datetime(df["Date of Hire"])
df["Date of Termination"] = pd.to_datetime(df["Date of Termination"])

employee_source = df["Employee Source"].value_counts(ascending=True)

tab_style = {'fontSize':18}
tab_selected_style = {'fontSize':20}

app.layout = html.Div([
    html.Div([
        html.H2("HR Dashboard", style={"textAlign": "center"}),
        html.Img(src="assets/logo.png")
    ], className="banner"),
    dcc.Tabs(id="tabs", value='head_count', children=[
        dcc.Tab(label="Head Count & Attrition", value="head_count", style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label="Diversity Profile", value="diversity", style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label="Recruitment", value="recruit", style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label="Data Table", value="data_table", style=tab_style, selected_style=tab_selected_style),
    ]),
    html.Div(id="page-content")
])

# recruitment sources
recruit = html.Div([
    html.Div([
        dcc.Graph(
            id="Recruitment Source",
            figure = px.histogram(df, y="Employee Source", histfunc="count", orientation="h",
                       title="Recruitment Source").update_yaxes(categoryorder="total ascending")\
                        .update_xaxes(title="Number of Recruitments")
        )
    ], className="row"),

    html.Div([
        html.Label("Filter details by:"),
        dcc.Dropdown(
            id="filter_value",
            options = [
                {"label": "Department", "value": "Department"},
                {"label": "State", "value": "State"}
            ], value="Department"
        )
    ], className="row", style={"width": "15%"}),

    html.Div([
        html.Div([
            dcc.Graph(
                id="Recruitment Source by Department",
                # figure = px.histogram(df, x="Employee Source", color="Department",
                #     histfunc="count", barnorm="percent", barmode="group", orientation="v",
                #     title="Details by Department").update_yaxes(title="Percentage of Recruitments")
                figure={"data": [go.Histogram(name=i,
                                    x=df[df["Department"]==i]["Employee Source"]) for i in df["Department"].unique()],
                        # "layout": go.Layout(yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text="Percentage by Source")))
                        }
                )
            ])
    ], className="row")
])

# diversity Profile
dept_gender = df.groupby(["Sex"])["Department"].value_counts()
dept_race = df.groupby(["RaceDesc"])["Department"].value_counts()
gender_ratio = np.round(df[df["Sex"]=="Male"].shape[0]/df[df["Sex"]=="Female"].shape[0],2)
diversity = html.Div([
    html.Div([
        html.Div([
            dcc.Graph(
                id="gender",
                figure = {"data": [go.Bar(name=i, x=dept_gender[i].index,
                               y=dept_gender[i], opacity=0.9) for i in df["Sex"].unique()],
                          "layout": go.Layout(
                              title = "Gender by Department",
                              barmode = "stack",
                              barnorm = "percent",
                              bargap = 0.4)
                          }
            )
        ], className="ten columns"),

        html.Div([
            html.P("Male-to-Female Ratio", style={"fontWeight":"30pt","textAlign":"center"}),
            html.H4("1 : {}".format(gender_ratio), style={"textAlign":"center"})
        ], className="two columns", style={"border": "thin lightgrey solid",
                                           "padding": "20px 0px 0px 0px"})
    ], className="row"),

    html.Div([
        html.Div([
            dcc.Graph(
                id="race",
                figure = {"data": [go.Bar(name=i, x=dept_race[i].index,
                               y=dept_race[i], opacity=0.9) for i in df["RaceDesc"].unique()],
                          "layout": go.Layout(
                              title = "Race by Department",
                              barmode = "group",
                              barnorm = "percent",
                              bargap = 0.4)
                          }
            )
        ], className="ten columns"),
    ], className="row")

])

# headcount
hire = df["Date of Hire"].value_counts().sort_index()
term = df["Date of Termination"].value_counts().sort_index()
emp_count = hire.sub(term, fill_value=0)
idx = pd.date_range(emp_count.index.min(), emp_count.index.max())
emp_count = emp_count.reindex(idx, fill_value=0).cumsum()

active = df["Employment Status"].value_counts()["Active"]


# attrition_rate
day = emp_count.index.max().day
month = emp_count.index.max().month
year = emp_count.index.max().year

last_month = emp_count[emp_count.index=="{}-{}-{}".format(year, month-1, day)][0]
this_month = emp_count[emp_count.index=="{}-{}-{}".format(year, month, day)][0]
avg = (last_month+this_month)/2
attritions = term[(term.index>="{}-{}-{}"\
                   .format(year, month-1, day)) & (term.index<="{}-{}-{}"\
                                                   .format(year, month, day))]
attritions = 0 if len(attritions)==0 else attrition
attrition_rate = np.round(attritions/avg,2)

# employees by "variable"


head_count = html.Div([
    html.Div([
        html.Div([
            dcc.Graph(
                id = "head_count_plot",
                figure = {"data": [go.Scatter(x = list(emp_count.index), y=list(emp_count.values), line={"color":"#83db7b"})],
                      "layout": go.Layout(title = "Number of Employees",
                                          xaxis=dict(
                                                rangeselector=dict(
                                                    buttons=list([
                                                        dict(count=1,
                                                             label="1m",
                                                             step="month",
                                                             stepmode="backward"),
                                                        dict(count=6,
                                                             label="6m",
                                                             step="month",
                                                             stepmode="backward"),
                                                        dict(count=1,
                                                             label="YTD",
                                                             step="year",
                                                             stepmode="todate"),
                                                        dict(count=1,
                                                             label="1y",
                                                             step="year",
                                                             stepmode="backward"),
                                                        dict(step="all")
                                                        ])
                                                    ),
                                                rangeslider={"visible":True}
                                                )
                                        )}
            )
        ], className="ten columns"),

        html.Div([
            html.P("Monthly Attrition Rate", style={"fontWeight":"30pt","textAlign":"center"}),
            html.H4("{}".format(attrition_rate), style={"textAlign":"center"})
        ], className="two columns", style={"border": "thin lightgrey solid", "margin": "20px 0px 0px 0px"}),

        html.Div([
            html.P("No. of Employees", style={"fontWeight":"30pt","textAlign":"center"}),
            html.H4("{}".format(active), style={"textAlign":"center"})
        ], className="two columns", style={"border": "thin lightgrey solid", "margin": "20px 0px 0px 0px"}),
    ], className="row"),

    html.Div([
        html.Div([
            html.Label("Filter details by:"),
            dcc.Dropdown(
                id="active_filter",
                options = [
                    {"label": "Department", "value": "Department"},
                    {"label": "Position", "value": "Position"},
                    {"label": "Manager", "value": "Manager"}
                ], value="Department", clearable=False
            ),
            html.Label("Specifics:"),
            dcc.Dropdown(
                    id="managers",
                    placeholder="Applies only to Managers")
        ], className="row", style={"width": "15%"}),

        html.Div([
            html.Div([
                dcc.Graph(
                    id="active_per_variable",
                    figure={"data": [go.Histogram(name=i, x=df[df["Department"]==i]["Employment Status"]) for i in df["Department"].unique()],
                            }
                    )
                ])
        ])
    ], className="row")
])

# data table
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
        page_size = 10,
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
    figure={"data": [go.Histogram(name=i,
                        x=df[df[filter_value_name]==i]["Employee Source"]) for i in df[filter_value_name].unique()],
            }
    return figure

@app.callback([Output("managers","options"),
                Output("managers", "value"),
                Output("managers", "disabled")],
            [Input("active_filter", "value")])
def update_manager_list(selected_active):
    options = [{"label": i, "value":i} for i in df["Manager Name"].unique()]
    value = "Janet King"
    if selected_active in ["Department", "Position"]:
        return options, None, True
    else:
        return options, value, False


@app.callback(Output("active_per_variable", "figure"),
              [Input("active_filter", "value"),
               Input("managers", "value")])
def update_active_employees(selected_active, selected_managers):
    if selected_active in ["Department", "Position"]:
        figure={"data": [go.Histogram(name=i, x=df[df[selected_active]==i]["Employment Status"]) for i in df[selected_active].unique()]}
    else:
        figure={"data": [go.Bar(name=selected_managers,
                        x=df[(df["Manager Name"]==selected_managers)]["Employment Status"].value_counts().index,
                        y=df[(df["Manager Name"]==selected_managers)]["Employment Status"].value_counts().values)]}
    return figure

# @app.callback(Output("managers", "value"),
#                 [Input("active_filter", "value")])
# @app.callback(Output("active_per_variable","figure"),
#             [Input("managers", "value")])
# def update_manager_filter(value):
#     # data = [go.Bar(name=i, x=df[(df["Manager Name"]==i)]["Employment Status"].value_counts().index,
#     #         y=df[(df["Manager Name"]==i)]["Employment Status"].value_counts().values) for i in value]
#     # figure={"data":data}
#     return "figure"

# update page
@app.callback(Output('page-content', 'children'),
              [Input('tabs', 'value')])
def display_page(tab):
    if tab == "recruit":
        return recruit
    elif tab == "data_table":
        return data_table
    elif tab == "diversity":
        return diversity
    elif tab == "head_count":
        return head_count
    else:
        return 404

if __name__ == '__main__':
    app.run_server(debug=False)
