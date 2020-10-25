import dash 
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Output, Input 
import dash_bootstrap_components as dbc
import plotly.graph_objs as go 
import plotly.express as px
import pandas as pd 
import json
import requests
from urllib.request import urlopen
import dash_table
from datetime import datetime,date

app=dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

##Summary API
#Downloading  CSV FILE THAT CONTAINS COUNTRIES AND their coordinates.
#The coordinates will be later extracted and merged with the data retrieved from the API
codes=pd.read_csv('data/countries.csv')
codes.rename(columns={'country':'CountryCode','latitude':'Latitude','longitude':'Longitude'},inplace=True)
#print(codes)
#Consuming covid Api
covid =urlopen('https://api.covid19api.com/summary')
cjson = covid.read()
cjdata = json.loads(cjson)
data=pd.DataFrame(cjdata['Countries'])
#data.set_index('Country',inplace=True)
data.drop('Premium',inplace=True,axis=1)
data['Date']=pd.to_datetime(data['Date']).dt.date
#merging the cordinates with the main dataframe
data=pd.merge(data,codes[['CountryCode','Latitude','Longitude']],on='CountryCode')
uniq_country=data['Slug'].str.title().unique()
columns=['Date','Country','NewConfirmed', 'TotalConfirmed', 'NewDeaths',
       'TotalDeaths', 'NewRecovered', 'TotalRecovered', ]

## Pie chart summary data
label1=data.sort_values(by='TotalConfirmed',ascending=False)[0:10]['Country']
label2=data.sort_values(by='TotalRecovered',ascending=True)[0:10]['Country']
value1=data.sort_values(by='TotalConfirmed',ascending=False)[0:10]['TotalRecovered']
value2=data.sort_values(by='TotalRecovered',ascending=True)[0:10]['TotalRecovered']
bar1=go.Bar(x=data['Country'],y=data['NewConfirmed'],name='New Confirmed cases')
bar2=go.Bar(x=data['Country'],y=data['NewDeaths'],name='New Death cases')
bar3=go.Bar(x=data['Country'],y=data['NewRecovered'],name='New Recovered cases')

## Country Api(Cases STAT)
#Collecting the Case Stat
response = requests.get("https://api.covid19api.com/world?from=2020-04-13T00:00:00Z&to=datetime.now()")
df=pd.DataFrame(response.json())
df2=df.sort_values(by='TotalConfirmed')
#Getting the range of dates for the data
f ='2020-04-13T00:00:00Z'
ft=datetime.strptime(f,"%Y-%m-%dT%H:%M:%SZ")
dat=pd.DataFrame(pd.date_range(start=ft,end=datetime.now()))
dat.rename(columns={0: 'Date'}, inplace=True)
#joining the two dataframes to the final dataframe
df2.reset_index(drop=True, inplace=True)
dat.reset_index(drop=True, inplace=True)
statdata=pd.concat([df2,dat],axis=1)

trace=[]
for i in ['NewConfirmed','NewRecovered','NewRecovered','NewDeaths']:

	trace.append(go.Scatter(x=statdata['Date'],y=statdata[i],mode='lines',name=i))



app.layout=html.Div([
	dbc.Row(dbc.Col([html.Div([
					html.H1(['Dashboard'])
		]),
		    html.Div([
		    		html.H3(['Dashboard showing Corona Cases Statistics'])
		    		])
		    ])),

	dbc.Row(
		dbc.Col(html.Div([
			dcc.Graph(id='scatter-plot',
				  figure={
				  			'data':trace,
				  			'layout':go.Layout(
				  							   title='Corona Statistics',
				  							   xaxis={'title':'Dates',
				  							           'tickangle': 45},
				  							   yaxis={'title':'Number of Cases',
				  							   		  'dtick':1000000},
				  							   legend={'title':'Type of Cases'},
				  							   paper_bgcolor = 'rgb(30, 30, 30)',
				  							   hovermode='closest',
				  							   font=dict(
        											family="Courier New, monospace",
        											size=18,
        											color="white")
				  				)

				  })
			],style={'border': '2px solid white'}),width=12)

		),

	dbc.Row([
		dbc.Col(
			html.Div([
				dcc.Graph(id='map-graph',
				  figure={
				  		'data':[go.Scattergeo(
       									 lon = data['Longitude'],
       									 lat = data['Latitude'],
       									 text = data[['Country','TotalConfirmed']],
       									 hovertemplate='Total Infections:<br>%{text}',
       									 mode = 'markers',
        								 marker = dict(
										            size = 8,
										            opacity = 0.8,
										            reversescale = True,
										            autocolorscale = False,
										            symbol = 'circle',
										            line = dict(
										                width=1,
										                color='rgba(102, 102, 102)'
										            ),
										            colorscale = 'Reds',
										            cmin = 0,
										            color = data['TotalDeaths'],
										            cmax = data['TotalDeaths'].max(),
										            colorbar_title="Covid cases"
        )
        								 )],

				  		'layout': go.Layout(title='country maps',
				  						  plot_bgcolor="LightSteelBlue",
				  						  paper_bgcolor = 'rgb(30, 30, 30)',
				  						  geo =dict(
									            scope='world',
									            projection_type='miller',
									            showland = True,
									            showlakes=True,
									            showsubunits=True,
									            showocean=True,
									            showcountries=True,
									            landcolor = "rgb(180, 235, 250)",
									            subunitcolor = "rgb(217, 217, 217)",
									            countrycolor = "rgb(217, 217, 217)",
									            countrywidth = 0.5,
									            subunitwidth = 0.5,
									            resolution=50),
				  						   font=dict(
        											family="Courier New, monospace",
        											size=18,
        											color="white"))

				  })

				],style={'border': '2px solid white'}),width=6),
		dbc.Col(html.Div([
			dbc.CardHeader(html.H3(" Summary of Total Cases")),
			html.H5('Select a Date:'),
				dcc.DatePickerSingle(
					id='my_date',
					min_date_allowed=date(2020,1,1),
					max_date_allowed=date.today(),
					date=date.today()
					),
			dbc.Card([
					 
					 dbc.CardBody([
					 	html.H5("Total Confirmed Cases:"),
					 	html.P(id='confirmed-cases',style={'color': 'red', 'fontSize': 22})],style={'textAlign':'center'}),

					 dbc.CardBody([
					 	html.H5("Total Recovered:"),
					 	html.P(id='recovered-cases',style={'color': 'green', 'fontSize': 22})],style={'textAlign':'center'}),

					 dbc.CardBody([
					 	html.H5("Total Deaths:"),
					 	html.P(id='death-cases',style={'color': 'blue', 'fontSize': 22})],style={'textAlign':'center'})		

				])
		
			],style={'border': '2px solid white'}),width=6)


		],no_gutters=True),

	dbc.Row(
		dbc.Col(
			[dcc.Dropdown(id='stats-drop',
				         options=[{'label':'New Confirmed','value':'NewConfirmed'},
				         		  {'label':'New Deaths','value':'NewDeaths'},
				         		  {'label':'New Recovered','value':'NewRecovered'}],
				         value='NewRecovered',
				         placeholder="Select a case type"
				         #multi=True
				         		  ),
			dcc.Graph(id='bar-plot'
				  # figure={
				  # 		  'data':[bar1,bar2,bar3],
				  # 		  'layout':go.Layout(title='Daily Statistics per Country',
				  # 		  					 xaxis={'title':'Countries ',
				  # 		  					 		'tickangle': 45},
				  # 		  					 yaxis={'title':'Cases',
				  # 		  					 		'dtick':5000 },
				  # 		  					 legend={'title':'Statistics'},
				  # 		  					 hovermode='closest',

				  # 		  					 plot_bgcolor="LightSteelBlue")

				  # }
				  )],width=12)



		),

	dbc.Row([
		dbc.Col(html.Div([dcc.Graph(id='pie_plot1',
				  figure={
				  		'data':[go.Pie(labels=label1,values=value1)],
				  		'layout':go.Layout(title='Top 10 Countries with the highest Cases',
				  							paper_bgcolor = 'rgb(30, 30, 30)',
				  							legend={'title':'Country'},
				  							font=dict(
        										family="Courier New, monospace",
        										size=18,
        										color="white"))
				  }
			  
			  )],style={'border': '2px solid white'}),width=6),

		dbc.Col([
			html.Div([
				dcc.Dropdown(id='picker',
					options=[{'label': i, 'value': i} for i in uniq_country],
					value='Kenya',
					# multi=True,
					style={'color':'#060606'})
				]),
			html.Div([dcc.Graph(id='pie_plot2'
				  # figure={
				  # 		 'data':[go.Pie(labels=label2,values=value2)],
				  # 		 'layout':go.Layout(title='Bottom 10 countries with the lowest recovery numbers',
				  # 		 					paper_bgcolor = 'rgb(30, 30, 30)'
				  # 		 					)
				  # })

)],style={'border': '2px solid white'})],width=6)
		
		
],no_gutters=True),
	dbc.Row(
			dbc.Col(dash_table.DataTable(
            id='covid-table',
            data=data.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in columns],
            fixed_rows={'headers': True},
            page_size=20, 
    		style_table={'height': '400px', 'overflowY': 'auto'},
    		style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'}

        ),width=12)
       
		)
	
 ],style={'border':'2px block white'})

## Bar chart callback
@app.callback(Output('bar-plot','figure'),
 	          [Input('stats-drop','value')])

def update_graph(case):

	fig=go.Figure()
	fig.add_trace(go.Bar(x=data['Country'],y=data[case],name=case))
	fig.update_xaxes(showline=True, linewidth=2, linecolor='white', mirror=True)
	fig.update_layout(

			 go.Layout(title={'text': case + ' per Country',
			 					'y':0.9,
        						'x':0.5,
			 				   'xanchor': 'center',
                                'yanchor': 'top'},
				  		xaxis={'title':'Countries',

				  				'tickfont':dict(family='Rockwell', color='#FFFFFF', size=14),
				  		  	   'tickangle': 45,
				  		  	   'titlefont':{
				  		  	   				'color':'#FFFFFF'
				  		  	   }},

				  		yaxis={'title':case,
				  		        'tickfont':dict(family='Rockwell', color='#FFFFFF', size=14),
				  				'titlefont':{
           						 'size':18,
           						 'color':'#FFFFFF'}},
				  		  					 		# 'dtick':5000 },
				  		hovermode='closest',
				  		paper_bgcolor = 'rgb(30, 30, 30)',
				  		plot_bgcolor="LightSteelBlue",
			 			font=dict(
        					family="Courier New, monospace",
        					size=18,
        					color="white"))) 

	return fig	 

@app.callback(Output('pie_plot2','figure'),
			  [Input('picker','value')])

def update_pie(country):
	piedata=data[data['Country']==country]
	fig=go.Figure()
	fig.add_trace(go.Pie(labels=['Total Confirmed','Total Deaths','Total Recovered'],
				values=[piedata.iloc[0]['TotalConfirmed'],piedata.iloc[0]['TotalDeaths'],piedata.iloc[0]['TotalRecovered']],
				hole=.3))
	fig.update_layout(go.Layout(title='Number of cases in ' + country,
								paper_bgcolor = 'rgb(30, 30, 30)',
								legend={'title':'Type of cases'},
								font=dict(
        								family="Courier New, monospace",
        								size=18,
        								color="white")))
	return fig

#card callback
@app.callback(Output('confirmed-cases','children'),
			  [Input('my_date','date')])

def update_card(date):
	date1=datetime.strptime(date,"%Y-%m-%d")
	return statdata[statdata['Date']==date1]['TotalConfirmed']

@app.callback(Output('recovered-cases','children'),
			  [Input('my_date','date')])

def update_card(date):
	date1=datetime.strptime(date,"%Y-%m-%d")
	return statdata[statdata['Date']==date1]['TotalRecovered']

@app.callback(Output('death-cases','children'),
			  [Input('my_date','date')])

def update_card(date):
	date1=datetime.strptime(date,"%Y-%m-%d")
	return statdata[statdata['Date']==date1]['TotalDeaths']


if __name__ == '__main__':
	app.run_server(debug=True)