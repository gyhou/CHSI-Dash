import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.figure_factory as ff
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import colorlover

# importing Dataset wrapper class
from data.dataset import Dataset


# preload the cause of death and demographics dataset and preprocess it.
cod = Dataset('./data/LEADINGCAUSESOFDEATH.csv')
state_cod = cod.state_data()
demogr = pd.read_csv('./data/DEMOGRAPHICS.csv')

#########################################################################
# 3D Scatter
#########################################################################

def display_fig(in_age='A', in_slice=0, in_range=0):
	colorscales = ["Greens", "YlOrRd", "Bluered", "RdBu", "Reds",
               	       "Blues", "Picnic", "Rainbow", "Portland", "Jet",
               	       "Hot", "Blackbody", "Earth", "Electric", "Viridis",
               	       "Cividis"]
	portland = [[0, 'rgb(12,51,131)'], [0.25, 'rgb(10,136,186)'],
  	            [0.5, 'rgb(242,211,56)'], [0.75, 'rgb(242,143,56)'],
  	            [1, 'rgb(217,30,30)']]
	portland_rgb = [i[1] for i in portland]
	cols = demogr.columns.tolist()
	titlez = "Poverty (%)"
	colorbarx = 0.95

	# age
	if in_age=='A' or in_age=='B' or in_age=='C':
            y = demogr[cols[17]]
            titley = "y = Age Under 19 (%)"
	elif in_age=='D' or in_age=='E':
            y = demogr[cols[20]]
            titley = "y = Age 19-64 (%)"
	elif in_age=='F':
	    y = demogr[cols[23]] + demogr[cols[26]]
	    titley = "y = Age Above 64 (%)"

	# log10(population density), poverty
	x = np.log10(demogr[cols[11]].replace([-2222,0], [demogr[cols[11]].mean(),1]))
	z = demogr[cols[14]].replace(-2222.2, demogr[cols[14]].mean())
	d = np.log10(demogr[cols[8]]) # log10(population)

	##############
	if in_slice == 0:
	##############
		trace1 = go.Scatter3d(
			x=x,
			y=y,
			z=z,
			mode='markers',
			marker=dict(
				size=d*2,
				color=z,                     # set color to an array/list of desired values
				colorscale=colorscales[8],   # choose a colorscale
				opacity=1,
				showscale=True,
				colorbar=dict(x=colorbarx, len=0.5,
							  thickness=10,
							  outlinecolor='white', outlinewidth=0,
							  title=dict(text=titlez, font=dict(size=10))
							  ),
				 line=dict(width=0.001, color='black')
			),
	        text='County Level',
			projection=dict(x=dict(show=True, opacity=0.1, scale=0.4),
							y=dict(show=True, opacity=0.1, scale=0.4),
							z=dict(show=True, opacity=0.1, scale=0.4),
							)
		)
		data = [trace1]
	##############
	else:
	##############
	    # for slicing data
		slicenum = 38
		if in_range<0 or in_range>slicenum:
			in_range=0
		slices = np.linspace(0, max(z), slicenum)
		condition = ((z >= slices[in_range]) & (z < slices[in_range+1]))
		x1 = x[condition]
		y1 = y[condition]
		z1 = [slices[in_range]] * len(x1)
		slicecolor =colorlover.interp(portland_rgb, slicenum)[in_range]

	    # for creating a plane
		p1 = np.linspace(0, max(x), 5)
		p2 = np.linspace(0, max(y), 5)
		p1, p2 = np.meshgrid(p1, p2)
		p3 = [[slices[in_range]] * 5] * 5

		trace1 = go.Scatter3d(
			x=x,
			y=y,
			z=z,
			mode='markers',
			name='county',
			marker=dict(
				size=d*2,
				color="black",
				opacity=0.01,
				line=dict(width=0.00, color='black'),
				),
				showlegend=False,
		)
		# this a a plane
		trace2 = go.Surface(
	        x=tuple(p1),
	        y=tuple(p2),
	        z=tuple(p3),
	        name='slice',
	        opacity=0.5,
		colorscale="Greys",
	        showscale=False,
	    )

		# this is merely a colorbar
		trace3 = go.Scatter3d(
						x=[0],
						y=[0],
						z=[0],
						name='',
						mode='markers',
						marker=dict(
							size=0.01,
							color=z, # set color to an array/list of desired values
							colorscale=portland, # choose a colorscale
							opacity=1,
							showscale=True,
							colorbar=dict(x=0.81, len=0.5,
										  thickness=10,
										  outlinecolor='white', outlinewidth=0,
										  title=dict(text=titlez, font=dict(size=10))
										  ),
                            line=dict(width=0.01, color='gray')
                        ),
                        showlegend=False,
		)
        # this is the actual sliced data points
        # why separating data points and colorbar?
        # cause I need only one color from the colorscale
		trace4 = go.Scatter3d(
                    x=x1,
                    y=y1,
                    z=z1,
                    name='Poverty',
                    mode='markers',
                    marker=dict(
                        size=d*2,
                        color=slicecolor,
                        opacity=1,
                        showscale=False,
                        line=dict(width=0.01, color='gray')
                    ),
                    projection=dict(x=dict(show=True, opacity=0.1, scale=0.8),
                                    y=dict(show=True, opacity=0.1, scale=0.8),
                                    z=dict(show=True, opacity=0.1, scale=0.8),
                                   ),
                    showlegend=False,
		)
		data = [trace1, trace2, trace3, trace4]
        ##############
        # end of if-else
        ##############

	layout = go.Layout(
		plot_bgcolor='#FFFFFF',#colors['background'],
		paper_bgcolor='#FFFFFF',#colors['background'],
    	autosize=True,
    	#width=600,
    	#height=500,
    	margin=dict(
        	l=10,
	        r=0,
        	b=0,
        	t=0
		),
		scene=dict(xaxis=dict(title="x = Population Density (lg)"),
                   yaxis=dict(title=titley),
                   zaxis=dict(title="z = "+titlez),),
	)
	fig = go.Figure(data=data, layout=layout)
	return fig

def plot_state_choro(df, age: str, cod: str):
	"""
	Plot state choropleth, adopted from georges code
	"""
	for col in df.columns:
		df[col] = df[col].astype(str)

	scl = [
	    [0.0, 'rgb(242,240,247)'],
	    [0.2, 'rgb(218,218,235)'],
	    [0.4, 'rgb(188,189,220)'],
	    [0.6, 'rgb(158,154,200)'],
	    [0.8, 'rgb(117,107,177)'],
	    [1.0, 'rgb(84,39,143)']
	]

	data = []
	textb, textc, textd = "Age 1-14: ", "Age 15-24: ", "Age 25-44: "
	B_Injury = age+'_'+cod
	B_Homicide = age+'_'+cod
	C_Injury = age+'_'+cod
	C_Homicide = age+'_'+cod
	C_Suicide = age+'_'+cod
	D_Injury = age+'_'+cod
	D_Homicide = age+'_'+cod
	D_Suicide = age+'_'+cod
	D_HIV = age+'_'+cod

	df[B_Injury+' text'] = df['State_Name'] + '<br>' + \
		textb+df[B_Injury].astype(float).round(2).astype(str)+'%'
	df[B_Homicide+' text'] = df['State_Name'] + '<br>' + \
		textb+df[B_Homicide].astype(float).round(2).astype(str) +'%'

	df[C_Injury+' text'] = df['State_Name'] + '<br>' + \
		textc + df[C_Injury].astype(float).round(2).astype(str) +'%'
	df[C_Homicide+' text'] = df['State_Name'] + '<br>' + \
		textc + df[C_Homicide].astype(float).round(2).astype(str) +'%'
	df[C_Suicide+' text'] = df['State_Name'] + '<br>' + \
		textc + df[C_Suicide].astype(float).round(2).astype(str) +'%'

	df[D_Injury+' text'] = df['State_Name'] + '<br>' + \
		textd + df[D_Injury].astype(float).round(2).astype(str) +'%'
	df[D_Homicide+' text'] = df['State_Name'] + '<br>' + \
		textd + df[D_Homicide].astype(float).round(2).astype(str) +'%'
	df[D_Suicide+' text'] = df['State_Name'] + '<br>' + \
		textd + df[D_Suicide].astype(float).round(2).astype(str) +'%'
	df[D_HIV+' text'] = df['State_Name'] + '<br>' + \
		textd + df[D_HIV].astype(float).round(2).astype(str) +'%'

	# colorbar propertiess
	colorbarx = 0.85
	colorbary = 0.4
	colorbarlen = 0.5
	colorbarthickness = 5 # default 30
	colorbaroutlinewidth = 0 # 0 to 1
	# map title
	title = 'Leading Cause of Death in USA 2003'
	titley = 0.91
	# hover text (no display of auto text)
	hovertemplate = '<b>%{text}</b>'

	trc1 = dict(type='choropleth',autocolorscale = False,locations=df['State_Abbr'],
              z=df[B_Injury].astype(float),locationmode='USA-states',
              hovertemplate=hovertemplate, text=df[B_Injury+' text'], colorscale = scl,
              colorbar=dict(x=colorbarx, y=colorbary, thickness=colorbarthickness, len=colorbarlen, outlinewidth=colorbaroutlinewidth,
                            title = "Percentage"),
              name='')
	trc2 = dict(type='choropleth',autocolorscale = False,locations=df['State_Abbr'],
              z=df[B_Homicide].astype(float),locationmode='USA-states',
              hovertemplate=hovertemplate, text = df[B_Homicide+' text'],colorscale = scl,
              colorbar=dict(x=colorbarx, y=colorbary, thickness=colorbarthickness, len=colorbarlen, outlinewidth=colorbaroutlinewidth,
                            title = "Percentage"),
              name='')

	trc3 = dict(type='choropleth',autocolorscale = False,locations=df['State_Abbr'],
              z=df[C_Injury].astype(float),locationmode='USA-states',
              hovertemplate=hovertemplate, text = df[C_Injury+' text'],colorscale = scl,
              colorbar=dict(x=colorbarx, y=colorbary, thickness=colorbarthickness, len=colorbarlen, outlinewidth=colorbaroutlinewidth,
                            title = "Percentage"),
              name='')
	trc4 = dict(type='choropleth',autocolorscale = False,locations=df['State_Abbr'],
              z=df[C_Homicide].astype(float),locationmode='USA-states',
              hovertemplate=hovertemplate, text = df[C_Homicide+' text'],colorscale = scl,
              colorbar=dict(x=colorbarx, y=colorbary, thickness=colorbarthickness, len=colorbarlen, outlinewidth=colorbaroutlinewidth,
                            title = "Percentage"),
              name='')
	trc5 = dict(type='choropleth',autocolorscale = False,locations=df['State_Abbr'],
              z=df[C_Suicide].astype(float),locationmode='USA-states',
              hovertemplate=hovertemplate, text = df[C_Suicide+' text'],colorscale = scl,
              colorbar=dict(x=colorbarx, y=colorbary, thickness=colorbarthickness, len=colorbarlen, outlinewidth=colorbaroutlinewidth,
                            title = "Percentage"),
              name='')

	trc6 = dict(type='choropleth',autocolorscale = False,locations=df['State_Abbr'],
              z=df[D_Injury].astype(float),locationmode='USA-states',
              hovertemplate=hovertemplate, text = df[D_Injury+' text'],colorscale = scl,
              colorbar=dict(x=colorbarx, y=colorbary, thickness=colorbarthickness, len=colorbarlen, outlinewidth=colorbaroutlinewidth,
                            title = "Percentage"),
              name='')
	trc7 = dict(type='choropleth',autocolorscale = False,locations=df['State_Abbr'],
              z=df[D_Homicide].astype(float),locationmode='USA-states',
              hovertemplate=hovertemplate, text = df[D_Homicide+' text'],colorscale = scl,
              colorbar=dict(x=colorbarx, y=colorbary, thickness=colorbarthickness, len=colorbarlen, outlinewidth=colorbaroutlinewidth,
                            title = "Percentage"),
              name='')
	trc8 = dict(type='choropleth',autocolorscale = False,locations=df['State_Abbr'],
              z=df[D_Suicide].astype(float),locationmode='USA-states',
              hovertemplate=hovertemplate, text = df[D_Suicide+' text'],colorscale = scl,
              colorbar=dict(x=colorbarx, y=colorbary, thickness=colorbarthickness, len=colorbarlen, outlinewidth=colorbaroutlinewidth,
                            title = "Percentage"),
              name='')
	trc9 = dict(type='choropleth',autocolorscale = False,locations=df['State_Abbr'],
              z=df[D_HIV].astype(float),locationmode='USA-states',
              hovertemplate=hovertemplate, text = df[D_HIV+' text'],colorscale = scl,
              colorbar=dict(x=colorbarx, y=colorbary, thickness=colorbarthickness, len=colorbarlen, outlinewidth=colorbaroutlinewidth,
                            title = "Percentage"),
              name='')

	data = [trc1, trc2,trc3, trc4,trc5, trc6,trc7, trc8,trc9]

	layout = dict(#title='Leading Cause of Death in USA',
				plot_bgcolor='#FFFFFF',
				paper_bgcolor='#FFFFFF',
				margin = dict(r=20, l=0, t=0, b=0),
				showlegend=False,
				#updatemenus=updatemenus,
				geo = dict(scope = 'usa',projection = dict(type = 'albers usa'),
				showlakes = True,lakecolor = '#F4F4F8'))#rgb(255, 255, 255)'))

	fig = go.Figure(data = data, layout = layout)
	return fig

def plot_choropleth(df):
	"""
	This function generates and returns a choropleth from the input dataset.

	TODO: Add error checking.

	Parameters
	----------
	df: a pandas dataframe with two columns; first column is `FIPS` for FIPS
	    geoencoding. Second column is the features to be plotted, base on a
		combination of age, ethnicity, and cause of death.
	"""
	colorscale = ["#f7fbff", "#ebf3fb", "#deebf7", "#d2e3f3", "#c6dbef", "#b3d2e9",
				  "#9ecae1", "#85bcdb", "#6baed6", "#57a0ce", "#4292c6", "#3082be",
				  "#2171b5", "#1361a9",	"#08519c", "#0b4083", "#08306b"]

	fips = df.FIPS.tolist()
	values = df.iloc[:,1].tolist()
	endpts = list(np.linspace(1, 100, len(colorscale)-1))

	annotations = [dict(
		showarrow = False,
		align = 'right',
		text = '<b>Age-adjusted death rate<br>per county per year</b>',
		x = 0.95,
		y = 0.95,
	)]

	layout = go.Layout(
		plot_bgcolor='#FFFFFF',#colors['background'],
		paper_bgcolor='#FFFFFF',#colors['background'],
		hovermode = 'closest',
		margin = dict(r=0, l=0, t=0, b=0),
		annotations = annotations,
		dragmode = 'lasso',
    	autosize=False,
		height=200,
    	width=400,
	)

	fig = ff.create_choropleth(
    	fips = fips, values = values, scope = ['Texas'],
    	binning_endpoints = endpts, colorscale = colorscale,
		simplify_county=0, simplify_state=0,
    	show_hover = True, centroid_marker = {'opacity': 0},
		county_outline={'color': 'rgb(244,24,244)', 'width': 0.5},
    	asp = 2.9,
    	legend_title = '% Death',
		layout=layout,
		)
	return fig

"""
App layout. Have to use dash.Dash(__name__) and put css/js files in /assets
folder according to https://dash.plot.ly/external-resources

Setting default values of the plot to D, Wh, and Homicide. Only one
choropleth graph. The graph is dynamically updated w/ @callback by function
update_graph, id='choropleth'.
"""
# starting plotly Dash server and add bootstrap css style sheet
app = dash.Dash(__name__)
server = app.server
app.config['suppress_callback_exceptions']=True

# Set style basics
app.css.append_css({'external_url':'assets/stylesheet.css'})

"""
Interactive options
"""
slices_radio = [
	{'label': 'All Data', 'value': 0},
	{'label': 'Sliced Data', 'value': 1},
]
ages_dropdown = [
	{'label': "1 - 14 Years Old", 'value': 'B'},
	{'label': "15 - 24 Years Old", 'value': 'C'},
	{'label': "25 - 44 Years Old", 'value': 'D'},
]
#ethnicity_dropdown = [
#	{'label': 'White', 'value': 'Wh'},
#	{'label': 'Black', 'value': 'Bl'},
#	{'label': 'Hispanic', 'value': 'Hi'},
#	{'label': 'Other', 'value': 'Ot'},
#]
causes_dropdown=[
	{'label': "Injury", 'value': 'Injury'},
	{'label': "Suicide", 'value': 'Suicide'},
	{'label': "Homicide", 'value': 'Homicide'},
	{'label': "HIV", 'value': 'HIV'}
]
marks1 = {
    0:"0", 10:"10", 20:"20", 30:"30"
}

app.layout = html.Div([
	# Header Div
	#html.Div([
	#	html.Img(src='assets/logo2.png',
	#			style = {'width': '50%', 'height': '20%',
	#					'float':'left', 'position':'relative'}),
		#html.H2("A Story of Life and Death",
		#		style={'margin-top':'5rem',
		#				'margin-bottom':'0rem'}),
		#html.P("Cause of Death and Demographics Visualization, 1996-2003",
		#		style={'margin-top':'0rem'})
	#], style = {'width': '66%', 'display':'inline-block'}),

	# Header + Control Grid
	html.Div([
		html.Div([
			html.Img(src='assets/logo2.png',
				style = {'width': '60%', 'height': '20%',
						'float':'left', 'position':'relative'}),
			html.Div([
				html.Div('Cause of Death'),
				dcc.Dropdown(
						id='cods',
						options=causes_dropdown,
						multi=False, clearable=False, searchable=False,
						value='Homicide'
				)
			], style = {'width': '31%', 'display':'inline-block',
						'fontSize': '13px', 'padding-left': '40px'}),
			html.Div([
				html.Div('Age Group'),
				dcc.Dropdown(
						id='ages',
						options=ages_dropdown,
						multi=False, clearable=False, searchable=False,
						value='D'
				)
			], style = {'width': '31%','display':'inline-block',
						'fontSize': '13px', 'padding-left': '40px'})
		], style = {'width': '70%', 'display':'inline-block'}),
		html.Div([
			dcc.RadioItems(id='radio1',
					        options=slices_radio,
					        value=0,
					        labelStyle={'display': 'inline-block'},
					        style = {'fontSize': '13px', 'padding-left': '0px'},
		    ),
		    html.Div(children='Slice Data by Poverty Level',
			    	style = {'fontSize': '13px', 'padding-left': '0px'}),
	    	html.Div(
	    		dcc.Slider(id="slider1",
	        			min=0,
			        	max=30,
			        	step=1,
			        	value=0,
			        	marks=marks1,
			        ),
			    	style={'height': '20px', 'width': '20%',
							'padding-left': '0px', 'display': 'inline-block'},)
	    ], style = {'width': '30%', 'display':'inline-block',
					'fontSize': '13px'})#, 'padding-left': '20px'})
	]),

	# plots Div. left and right plots
	html.Div([
		# left plot
		html.Div([
			html.Div([
				dcc.Graph(id='choropleth')
			]),
		], style = {'width': '49%', 'display':'inline-block'}),
		# right plot with radio items and slider
		html.Div([
			html.Div([
				dcc.Graph(id="scatter3d")
			]),
		], style = {'width': '49%',
					'display':'inline-block'})
	], style = {'width': '98%', 'display':'inline-block'}),

	# Disclaimer Div
	html.Div([
		html.P("Source: U.S. Department of Health & Human Services",
				style={'margin-top':'0rem', 'margin-bottom':'0rem'}),
		html.P("Community Health Status Indicator to Combat Obesity, Heart Disease and Cancer",
				style={'margin-top':'0rem', 'margin-bottom':'0rem'}),
		html.P("https://catalog.data.gov/dataset/community-health-status-indicators-chsi-to-combat-obesity-heart-disease-and-cancer",
				style={'margin-top':'0rem', 'margin-bottom':'0rem'})
	], style = {'width': '98%', 'margin-top':'5rem','fontSize': '10px'})
])

@app.callback(Output("scatter3d", "figure"),
			 [Input("ages", "value"),
              Input("radio1", "value"),
              Input('slider1', "value")])
def update_3dscatter(input1, input2, input3):
  return display_fig(in_age=input1, in_slice=input2, in_range=input3)

@app.callback(Output('choropleth', 'figure'),
 			 [Input('ages', 'value'),
			  #Input('ethnicities', 'value'),
			  Input('cods', 'value')])
def update_choro(age, cods):
	"""
	This is the callback function that dynamically adjusts the choropleth by
	taking inputs from the dropdown menus, calling the Dataset class to lookup
	the appropriate column, get the data slices with FIPS and feature column.
	Returns a choropleth figure by calling plot_state_choro.

	Parameters
	----------
	age: age brackets
	cods: causes of death
	"""
	return plot_state_choro(state_cod, age, cods)

#@app.callback(Output('choropleth', 'figure'),
# 			 [Input('ages', 'value'),
#			  Input('ethnicities', 'value'),
#			  Input('cods', 'value')])
#def update_choro(age, ethnicities, cods):
#	"""
#	This is the callback function that dynamically adjusts the choropleth by
#	taking inputs from the dropdown menus, calling the Dataset class to lookup
#	the appropriate column, get the data slices with FIPS and feature column.
#	It then returns a choropleth figure by calling plot_choropleth.
#
#	NOTE: if NaN values are plotted, the mouseover data inpsection will not work
#	Instead, fillna with 0 so every polygon is plotted.
#
#	Parameters
#	----------
#	age: age brackets
#	ethnicities: ethnicities
#	cods: causes of death
#	"""
#	if cod.isin_cols(age, ethnicities, cods):
#		slices = cod.lookup(age, ethnicities, cods)
#	else:
#		# if age/ethnicities/cods combination dont exist, plot default graph.
#		slices = cod.lookup('D', 'Wh', 'Homicide')
#
#	tx_slices = slices[slices.FIPS.str.startswith("48")].fillna(0)
#	return plot_choropleth(tx_slices)


if __name__ == '__main__':
    app.run_server(debug=True)
