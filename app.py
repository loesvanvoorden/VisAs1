import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc # Import dash-bootstrap-components
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# import requests # No longer needed for FIFA API
# import json # No longer needed for JSON handling

# Initialize the app with the Cyborg theme and Bootstrap
app = dash.Dash(__name__, 
    external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}] # Corrected meta_tags
)
app.title = "Football Match Insights"

# --- 1. Data Loading and Preprocessing ---
try:
    df = pd.read_csv('international_matches.csv')
except FileNotFoundError:
    print("Error: 'international_matches.csv' not found. Make sure the file is in the same directory.")
    exit()

# Convert Date to datetime objects for international_matches.csv
df['Date'] = pd.to_datetime(df['Date'], format='mixed', errors='coerce')
df = df.dropna(subset=['Date'])

# Determine Winner/Draw
df['IsDraw'] = df['Winning Team'].isnull() & df['Losing Team'].isnull()
df['Winner'] = df.apply(lambda row: row['Home Team'] if row['Home Goals'] > row['Away Goals'] else (row['Away Team'] if row['Away Goals'] > row['Home Goals'] else 'Draw'), axis=1)
df['IsHomeWin'] = df['Winner'] == df['Home Team']
df['IsAwayWin'] = df['Winner'] == df['Away Team']

# Load FIFA Ranking Data from CSV
try:
    df_ranking = pd.read_csv('fifa_ranking-2024-06-20.csv')
    df_ranking['rank_date'] = pd.to_datetime(df_ranking['rank_date'], errors='coerce')
    df_ranking = df_ranking.dropna(subset=['rank_date', 'rank', 'country_full'])
    df_ranking['year'] = df_ranking['rank_date'].dt.year
    ranking_years = sorted(df_ranking['year'].unique(), reverse=True)
except FileNotFoundError:
    print("Error: 'fifa_ranking-2024-06-20.csv' not found. Make sure the file is in the same directory.")
    df_ranking = pd.DataFrame() # Create an empty DataFrame to avoid errors
    ranking_years = []


# Get unique values for dropdowns
all_teams = sorted(pd.concat([df['Home Team'], df['Away Team']]).unique())
all_tournaments = sorted(df['Tournament'].unique())

# Color mapping for consistent chart colors
WIN_COLOR = 'rgb(26, 188, 156)' # Mint Green / Teal
LOSS_COLOR = 'rgb(231, 76, 60)'   # Pomegranate Red
DRAW_COLOR = 'rgb(149, 165, 166)' # Silver / Grey

HOME_COLOR = 'rgb(155, 89, 182)' # Amethyst Purple (Team 1 / Home)
AWAY_COLOR = 'rgb(52, 152, 219)'  # Belize Hole Blue (Team 2 / Away)


# --- 2. App Layout with Bootstrap Components ---
app.layout = dbc.Container([
    # Row for Banner Image
    dbc.Row([
        dbc.Col(html.Img(src=app.get_asset_url('banner.jpg'),
                         style={'height': '200px', 'width': '100%', 'objectFit': 'cover'}), width=12)
    ], className="mb-4"),

    # Row for Title
    dbc.Row(dbc.Col(html.H1("Smart Betting Insights Dashboard"), width=12), className="mb-1 text-center"),
    dbc.Row(dbc.Col(html.H5("Based on Historical International Matches", className="text-muted"), width=12), className="mb-4 text-center"),
    
    # dcc.Location(id='url', refresh=False), # Removed, was for old FIFA API

    # --- Tabs ---
    dcc.Tabs(id="tabs", value='tab-dashboard', children=[
        # --- Dashboard Tab ---
        dcc.Tab(label='Dashboard', value='tab-dashboard', children=[
            dbc.Container([ # Wrap dashboard content in a container for padding
                
                # --- Row 1: FIFA Ranking, Win Rate & Goal Trends (3 columns) ---
                dbc.Row([
                    # Col 1: FIFA Top 3 Ranking (Moved here)
                    dbc.Col([
                        html.H5("FIFA Top 3 Ranking", className="mb-2"),
                        html.Label("Select Year:"),
                        dcc.Dropdown(
                            id='ranking-year-dropdown',
                            options=[{'label': str(year), 'value': year} for year in ranking_years],
                            value=ranking_years[0] if ranking_years else None,
                            clearable=False,
                            style={'marginBottom': '10px', 'color': '#000'}
                        ),
                        html.Div(id='top-3-ranking-display', className="text-center")
                    ], width=2, className="p-3 mb-3"), # Reduced width to 3

                    # Col 2: Win Rate Analysis
                    dbc.Col([
                        html.H5("Win Rate Analysis by Tournament Type", className="mb-2"),
                        html.Label("Select Country:"),
                        dcc.Dropdown(
                            id='country-dropdown-v1',
                            options=[{'label': team, 'value': team} for team in all_teams],
                            value='Brazil'
                        ),
                        dcc.Graph(id='win-rate-tournament-graph')
                    ], width=5, className="p-3"), # Kept width at 4

                    # Col 3: Goal Scoring Trends
                    dbc.Col([
                        html.H5("Goal Scoring Trends (Home vs. Away)", className="mb-2"),
                        html.Label("Select Tournament Type (Optional):"),
                        dcc.Dropdown(
                            id='tournament-dropdown-v2',
                            options=[{'label': 'All Tournaments', 'value': 'All'}] + [{'label': t, 'value': t} for t in all_tournaments],
                            value='All'
                        ),
                        dcc.Graph(id='goal-trends-graph')
                    ], width=5, className="p-3") # Increased width to 5
                ], className="mb-4"),

                # --- Row 2: Home/Away & Head-to-Head ---
                dbc.Row([
                    # Col 1: Home vs Away Performance
                    dbc.Col([
                        html.H5("Home vs. Away Performance", className="mb-2"),
                        html.Label("Select Country/Overall:"),
                        dcc.Dropdown(
                            id='country-dropdown-v3',
                            options=[{'label': 'Overall', 'value': 'Overall'}] +
                                    [{'label': team, 'value': team} for team in all_teams],
                            value='Overall'
                        ),
                        dcc.Graph(id='home-away-graph')
                    ], width=6, className="p-3"), # Removed border, rounded.

                    # Col 2: Head-to-Head Comparison
                    dbc.Col([
                        html.H5("Head-to-Head Comparison", className="mb-2"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Select Team 1:"),
                                dcc.Dropdown(
                                    id='team1-dropdown-v4',
                                    options=[{'label': team, 'value': team} for team in all_teams],
                                    value='Brazil'
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("Select Team 2:"),
                                dcc.Dropdown(
                                    id='team2-dropdown-v4',
                                    options=[{'label': team, 'value': team} for team in all_teams],
                                    value='Argentina'
                                )
                            ], width=6),
                        ]),
                        dcc.Graph(id='h2h-graph'),
                        
                        # Add Explain Metrics button
                        html.Div([
                            dbc.Button(
                                "Explain Metrics",
                                id="metrics-help",
                                color="info",
                                size="sm",
                                className="mr-1"
                            ),
                        ], style={'textAlign': 'center', 'marginTop': '10px', 'marginBottom': '20px'}),
                        
                        # Modal for metrics explanation
                        dbc.Modal([
                            dbc.ModalHeader("Understanding the Metrics"),
                            dbc.ModalBody([
                                html.P([html.Strong("Win Rate: "), "Percentage of total matches won"]),
                                html.P([html.Strong("Home Win Rate: "), "Success rate when playing at home"]),
                                html.P([html.Strong("Clean Sheets: "), "Defensive strength - % of matches where team kept opponent from scoring (0-0 or a win/loss without conceding)"]),
                                html.Div([
                                    html.P([
                                        html.Strong("Recent Form: "), 
                                        "Form rating based on the last 5 competitive matches, with more recent results weighted higher:"
                                    ]),
                                    html.Div([
                                        "• Latest match: 33% impact",
                                        html.Br(),
                                        "• 2nd latest: 27% impact",
                                        html.Br(),
                                        "• 3rd latest: 20% impact",
                                        html.Br(),
                                        "• 4th latest: 13% impact",
                                        html.Br(),
                                        "• 5th latest: 7% impact",
                                    ], style={'marginLeft': '15px', 'marginTop': '5px', 'marginBottom': '5px'}),
                                    html.P([
                                        "Win = 100% of points, Draw = 50%, Loss = 0%. ",
                                        "Helps identify teams in good form regardless of historical stats."
                                    ], style={'marginTop': '5px'})
                                ])
                            ])
                        ], id="metrics-modal", is_open=False),
                        
                        html.Div(id='h2h-kpis', className="mt-2"),
                        html.Div(id='h2h-table', className="mt-2")
                    ], width=6, className="p-3") # Removed border, rounded.
                ]), # End of Row 2

                # --- Old FIFA World Ranking Section (Removed) ---
                # This entire dbc.Row and its contents related to the old API-based FIFA ranking table
                # have been removed.

            ], fluid=True, className="pt-3") # Add padding top
        ]),

        # --- Information Tab (Updated with betting insights) ---
        dcc.Tab(label='Betting Insights Guide', value='tab-guide', children=[
            dbc.Container([
                html.H3("Understanding the Betting Insights", className="text-center mt-3 mb-4"),
                html.P(
                    "This dashboard analyzes historical international football data to help inform betting decisions. "
                    "Each visualization provides different insights for match analysis.",
                    className="text-center mb-4 lead"
                ),
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Tournament Performance Analysis"),
                        dbc.CardBody([
                            html.P(
                                "The radial win/loss chart shows how teams perform in different competitions. "
                                "Look for patterns in specific tournament types - some teams excel in qualifiers "
                                "but struggle in major tournaments.",
                                className="card-text"
                            ),
                            html.Small(
                                "Tip: Pay attention to win percentages in similar tournament types to upcoming matches.",
                                className="text-muted"
                            )
                        ])
                    ]), width=6, className="mb-3"),
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Goal Scoring Patterns"),
                        dbc.CardBody([
                            html.P(
                                "The goal trends chart reveals historical scoring patterns. "
                                "Compare home vs away scoring rates and look for recent trends in goal-scoring form.",
                                className="card-text"
                            ),
                            html.Small(
                                "Tip: Useful for Over/Under and Both Teams to Score markets.",
                                className="text-muted"
                            )
                        ])
                    ]), width=6, className="mb-3"),
                ]),
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Home vs Away Analysis"),
                        dbc.CardBody([
                            html.P(
                                "Compare how teams perform at home versus away. "
                                "Some teams show significant home advantage while others maintain consistent form regardless of location.",
                                className="card-text"
                            ),
                            html.Small(
                                "Tip: Consider home/away splits when betting on match outcomes or Asian Handicaps.",
                                className="text-muted"
                            )
                        ])
                    ]), width=6, className="mb-3"),
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Head-to-Head Insights"),
                        dbc.CardBody([
                            html.P([
                                "The radar chart compares four key metrics:",
                                html.Ul([
                                    html.Li("Win Rate: Overall success rate across all competitions"),
                                    html.Li("Home Win Rate: Specific performance when playing at home"),
                                    html.Li("Clean Sheets: Defensive strength - matches without conceding"),
                                    html.Li("Recent Form: Weighted performance of last 5 matches (33% latest to 7% oldest)")
                                ], className="mt-2 mb-2")
                            ]),
                            html.Small(
                                "Tip: Teams with strong defensive records (high Clean Sheets) often provide value in Under 2.5 markets.",
                                className="text-muted"
                            )
                        ])
                    ]), width=6, className="mb-3"),
                ]),
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Additional Betting Considerations"),
                        dbc.CardBody([
                            html.P([
                                "When using this data for betting:",
                                html.Ul([
                                    html.Li("Recent Form weighs the last 5 matches with diminishing importance - great for spotting current team momentum"),
                                    html.Li("High Clean Sheets % suggests good defensive organization - consider Under markets or 'No' in BTTS"),
                                    html.Li("Compare Home Win Rate to overall Win Rate to identify home advantage value"),
                                    html.Li("Check the last 5 meetings table for specific head-to-head patterns")
                                ], className="mt-2")
                            ]),
                            html.Small(
                                "Remember: Historical data is just one factor. Consider current injuries, weather, and team news.",
                                className="text-muted"
                            )
                        ])
                    ]), width=12, className="mb-3")
                ])
            ], fluid=True)
        ])
    ])

], fluid=True) # Use fluid container for full width

# --- 4. Callbacks ---

# Callback for Visualization 1: Win Rates by Tournament
@app.callback(
    Output('win-rate-tournament-graph', 'figure'),
    Input('country-dropdown-v1', 'value')
)
def update_win_rate_graph(selected_country):
    if not selected_country:
        # Use Bootstrap alert for better visual feedback
        return {
            'layout': {
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': 'Please select a country.',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 16}
                }]
            }
        }

    # Filter data for the selected country (playing either home or away)
    country_df = df[(df['Home Team'] == selected_country) | (df['Away Team'] == selected_country)].copy()

    if country_df.empty:
        return {
            'layout': {
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': f'No data available for {selected_country}.',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 16}
                }]
            }
        }

    # Determine win/loss/draw from the perspective of the selected country
    def get_result(row):
        if row['IsDraw']:
            return 'Draw'
        elif (row['Home Team'] == selected_country and row['IsHomeWin']) or \
             (row['Away Team'] == selected_country and row['IsAwayWin']):
            return 'Win'
        else:
            return 'Loss'
    country_df['Result'] = country_df.apply(get_result, axis=1)

    # Calculate win/loss/draw counts per tournament
    results_by_tournament_counts = country_df.groupby(['Tournament', 'Result']).size().unstack(fill_value=0)

    # Ensure all result columns exist
    for res in ['Win', 'Draw', 'Loss']:
         if res not in results_by_tournament_counts.columns:
             results_by_tournament_counts[res] = 0

    # Melt counts for later merging
    counts_melted = results_by_tournament_counts.reset_index().melt(id_vars='Tournament', var_name='Result', value_name='Count')

    # Calculate percentages
    results_sum = results_by_tournament_counts.sum(axis=1)
    valid_rows = results_sum > 0
    results_perc = results_by_tournament_counts[valid_rows].apply(lambda x: x * 100 / x.sum(), axis=1).reset_index()

    if results_perc.empty:
         return {
            'data': [],
            'layout': {
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': f'No valid match results for {selected_country} to calculate percentages.',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 16}
                }]
            }
        }

    # Melt percentages for plotting
    results_melted = results_perc.melt(id_vars='Tournament', var_name='Result', value_name='Percentage')

    # Merge Counts into the Percentage DataFrame for hover info
    plot_df = pd.merge(results_melted, counts_melted, on=['Tournament', 'Result'], how='left')

    try:
        # Use px.bar_polar with the merged plot_df
        fig = px.bar_polar(plot_df, # Use merged dataframe
                           theta='Tournament', # Angle axis
                           r='Percentage',     # Radius axis
                           color='Result',
                           title=f'Win/Loss/Draw % for {selected_country} by Tournament (Hover for Count)', # Updated title
                           # hover_data=['Count'], # Remove hover_data
                           custom_data=['Result', 'Count'], # Explicitly define custom_data
                           labels={'Percentage': '% of Matches', 'Count': 'Matches'}, # Add label for Count
                           category_orders={"Result": ["Win", "Draw", "Loss"]},
                           color_discrete_map={'Win': '#1f77b4', 'Loss': '#ff7f0e', 'Draw': '#7f7f7f'}, # Colorblind Friendly: Blue/Orange/Grey
                           template='plotly_dark',
                           range_r=[0, 105]
                           )
        # Customize hover template slightly for clarity (should now work correctly)
        fig.update_traces(hovertemplate=
            '<b>%{theta}</b><br>' +
            'Result: %{customdata[0]}<br>' + # Result is the first custom data item
            'Percentage: %{r:.1f}%<br>' +
            'Count: %{customdata[1]}<extra></extra>') # Count is the second custom data item

        # Update layout for polar chart
        fig.update_layout(margin=dict(l=40, r=40, t=80, b=40),
                          legend_title_text='Result',
                          polar=dict(radialaxis=dict(ticksuffix='%')))

    except Exception as e:
        print(f"Error creating win rate polar plot: {e}") # Log error to terminal
        return {
            'layout': {
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': f'Could not generate plot: {e}',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 12}
                }],
                'template': 'plotly_dark' # Ensure error message respects theme
            }
        }
    return fig

# Callback for Visualization 2: Goal Scoring Trends (Now interactive)
@app.callback(
    Output('goal-trends-graph', 'figure'),
    [Input('tournament-dropdown-v2', 'value'),
     Input('win-rate-tournament-graph', 'clickData'),
     Input('country-dropdown-v1', 'value'),      # Country from Win Rate analysis
     Input('country-dropdown-v3', 'value')]      # Country from Home/Away analysis
)
def update_goal_trends_graph(selected_tournament_dropdown, 
                             win_rate_clickData, 
                             selected_country_v1, 
                             selected_country_v3):

    trigger_id = dash.ctx.triggered_id
    # Get the specific property that triggered, e.g., 'country-dropdown-v1.value'
    # triggered_prop_id = dash.ctx.triggered_prop_ids.get(trigger_id) 

    filter_tournament = selected_tournament_dropdown # Default tournament filter

    # --- Determine Tournament Filter Based on Trigger --- #
    if trigger_id == 'win-rate-tournament-graph' and win_rate_clickData:
        try:
            clicked_tournament = win_rate_clickData['points'][0]['theta']
            filter_tournament = clicked_tournament
            print(f"Goal Trends: Filtering by clicked tournament: {clicked_tournament}")
        except (KeyError, IndexError, TypeError):
            print("Goal Trends: Could not extract tournament from win_rate_clickData")
            # Fallback to dropdown if click data is invalid
    elif trigger_id == 'tournament-dropdown-v2':
         print(f"Goal Trends: Filtering by tournament dropdown: {filter_tournament}")

    # --- Determine Country Filter --- #    
    country_to_filter_by = None
    country_filter_text = "Overall" # Default text for title

    # Priority 1: Direct country selection trigger from V1 or V3
    if trigger_id == 'country-dropdown-v1' and selected_country_v1:
        country_to_filter_by = selected_country_v1
        print(f"Goal Trends: Country filter by V1 trigger: {selected_country_v1}")
    elif trigger_id == 'country-dropdown-v3' and selected_country_v3 and selected_country_v3 != 'Overall':
        country_to_filter_by = selected_country_v3
        print(f"Goal Trends: Country filter by V3 trigger: {selected_country_v3}")
    # Priority 2: Contextual country selection if trigger was NOT a direct country dropdown action
    # This means if a tournament was changed, we look at V3 for country context.
    elif trigger_id != 'country-dropdown-v1' and trigger_id != 'country-dropdown-v3':
        if selected_country_v3 and selected_country_v3 != 'Overall':
            country_to_filter_by = selected_country_v3
            print(f"Goal Trends: Contextual country filter from V3 (e.g., after tournament change): {selected_country_v3}")
        else:
            # If V3 is 'Overall' or not set, and trigger wasn't V1/V3, then country is overall.
            print("Goal Trends: Trigger was not V1/V3, and V3 is 'Overall'. Showing overall country trends.")
    # If the trigger was 'country-dropdown-v3' and its new value is 'Overall',
    # country_to_filter_by will correctly remain None from initialization, leading to "Overall".
    
    if country_to_filter_by:
        country_filter_text = country_to_filter_by
        print(f"Goal Trends: Applying country filter for: {country_to_filter_by}")
    else:
        print("Goal Trends: No specific country filter to apply, using overall data for countries.")

    # --- Data Filtering --- #
    filtered_df = df.copy()

    if country_to_filter_by:
        filtered_df = filtered_df[(filtered_df['Home Team'] == country_to_filter_by) | 
                                  (filtered_df['Away Team'] == country_to_filter_by)]

    # Apply Tournament Filter (from own dropdown or radial click)
    tournament_filter_text = "All Tournaments"
    if filter_tournament and filter_tournament != 'All':
        filtered_df = filtered_df[filtered_df['Tournament'] == filter_tournament]
        tournament_filter_text = filter_tournament
    
    # --- Title --- #
    plot_title = f'Avg Goals Scored (Home vs. Away) - {country_filter_text} - {tournament_filter_text}'

    # Calculate average goals per year
    avg_goals_yearly = filtered_df.groupby(filtered_df['Date'].dt.year)[['Home Goals', 'Away Goals']].mean().reset_index()

    # --- Handle No Data --- #
    # Update error message context
    if avg_goals_yearly.empty:
        error_text = f"No relevant goal data found for {country_filter_text} in {tournament_filter_text}"
        return {
            'layout': {
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': error_text,
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 16}
                }],
                'template': 'plotly_dark'
            }
        }

    # --- Create Area Chart --- #
    fig = go.Figure()

    # Add Home Goals trace (Only if data exists for the filtered selection)
    if 'Home Goals' in avg_goals_yearly.columns and not avg_goals_yearly['Home Goals'].isnull().all():
        fig.add_trace(go.Scatter(
            x=avg_goals_yearly['Date'],
            y=avg_goals_yearly['Home Goals'],
            mode='lines',
            line=dict(shape='spline', width=1.5),
            name='Home Goals',
            marker_color='#9467bd',
            opacity=1
        ))

    # Add Away Goals trace (Only if data exists for the filtered selection)
    if 'Away Goals' in avg_goals_yearly.columns and not avg_goals_yearly['Away Goals'].isnull().all():
        fig.add_trace(go.Scatter(
            x=avg_goals_yearly['Date'],
            y=avg_goals_yearly['Away Goals'],
            mode='lines',
            line=dict(shape='spline', width=1.5),
            name='Away Goals',
            marker_color='#2ca02c',
            opacity=1
        ))

    # Update layout
    fig.update_layout(
        title=plot_title,
        xaxis_title='Year',
        yaxis_title='Avg Goals per Match',
        legend_title_text='Team Location', # Keep legend title
        margin=dict(l=20, r=20, t=50, b=20),
        height=400,
        template='plotly_dark',
        hovermode='x unified'
    )

    return fig

# Callback for Visualization 3: Home vs Away Performance (Reverted)
@app.callback(
    Output('home-away-graph', 'figure'),
    Input('country-dropdown-v3', 'value')
)
def update_home_away_graph(selected_option):
    if not selected_option:
         # Fully formed error dictionary
         return {
             'layout': {
                 'xaxis': {'visible': False},
                 'yaxis': {'visible': False},
                 'annotations': [{
                     'text': 'Please select a country or Overall.',
                     'xref': 'paper',
                     'yref': 'paper',
                     'showarrow': False,
                     'font': {'size': 16}
                 }],
                 'template': 'plotly_dark'
             }
         }

    # Filter competitive matches
    comp_df = df[df['Tournament'] != 'Friendly'].copy()

    # --- Get Home and Away Data --- (Filter by country OR use all data)
    if selected_option == 'Overall':
        country_home = comp_df.copy() # Use all competitive home games
        country_away = comp_df.copy() # Use all competitive away games
        title_suffix = "(Overall Competitive Matches)"
    else:
        country_home = comp_df[(comp_df['Home Team'] == selected_option)].copy()
        country_away = comp_df[(comp_df['Away Team'] == selected_option)].copy()
        title_suffix = f"(Competitive Matches for {selected_option})"

    # --- Calculate Home Stats --- (Reverted to Percentage Calculations)
    home_total = len(country_home)
    home_wins = country_home['IsHomeWin'].sum()
    home_draws = country_home[country_home['Winner'] == 'Draw'].shape[0]
    home_losses = home_total - home_wins - home_draws

    home_win_perc = (home_wins / home_total * 100) if home_total > 0 else 0
    home_draw_perc = (home_draws / home_total * 100) if home_total > 0 else 0
    home_loss_perc = 100 - home_win_perc - home_draw_perc

    # --- Calculate Away Stats --- (Reverted to Percentage Calculations)
    away_total = len(country_away)
    away_wins = country_away['IsAwayWin'].sum()
    away_draws = country_away[country_away['Winner'] == 'Draw'].shape[0]
    away_losses = away_total - away_wins - away_draws

    away_win_perc = (away_wins / away_total * 100) if away_total > 0 else 0
    away_draw_perc = (away_draws / away_total * 100) if away_total > 0 else 0
    away_loss_perc = 100 - away_win_perc - away_draw_perc

    # --- Create DataFrame for Plotting --- (Reverted)
    plot_data = pd.DataFrame({
        'Location': ['Home'] * 3 + ['Away'] * 3,
        'Result': ['Win', 'Draw', 'Loss'] * 2,
        'Percentage': [home_win_perc, home_draw_perc, home_loss_perc,
                       away_win_perc, away_draw_perc, away_loss_perc]
    })

    if plot_data.empty or (home_total == 0 and away_total == 0):
         return {
             'layout': {
                 'xaxis': {'visible': False},
                 'yaxis': {'visible': False},
                 'annotations': [{
                     'text': f'No competitive match data found for {selected_option}.',
                     'xref': 'paper',
                     'yref': 'paper',
                     'showarrow': False,
                     'font': {'size': 16}
                 }],
                 'template': 'plotly_dark'
             }
         }

    # --- Create Grouped Bar Chart --- (Reverted from Box Plot)
    try:
        # Switched axes: x=Location, color=Result
        fig = px.bar(plot_data, x='Location', y='Percentage', color='Result',
                     barmode='group',
                     title=f"Home vs Away Win/Draw/Loss % {title_suffix}",
                     labels={'Percentage': '% of Matches', 'Location': 'Match Location'},
                     category_orders={"Location": ["Home", "Away"], "Result": ["Win", "Draw", "Loss"]},
                     color_discrete_map={'Win': '#1f77b4', 'Loss': '#ff7f0e', 'Draw': '#7f7f7f'}, # Colorblind Friendly: Blue/Orange/Grey
                     template='plotly_dark')
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20), height=400,
                          yaxis_title="% of Matches",
                          xaxis_title="Match Location", # Updated X axis title
                          legend_title_text='Result', # Added legend title
                          title_font_size=14)
    except Exception as e:
         print(f"Error creating home vs away bar plot: {e}")
         # Fully formed error dictionary
         return {
             'layout': {
                 'xaxis': {'visible': False},
                 'yaxis': {'visible': False},
                 'annotations': [{
                     'text': f'Could not generate plot: {e}',
                     'xref': 'paper',
                     'yref': 'paper',
                     'showarrow': False,
                     'font': {'size': 12}
                 }],
                 'template': 'plotly_dark'
             }
         }

    return fig

# Callback for Visualization 4: Head-to-Head
@app.callback(
    [Output('h2h-graph', 'figure'),
     Output('h2h-kpis', 'children'),
     Output('h2h-table', 'children')],
    [Input('team1-dropdown-v4', 'value'),
     Input('team2-dropdown-v4', 'value')]
)
def update_h2h_graph(team1, team2):
    if not team1 or not team2 or team1 == team2:
        # Fully formed error dictionary
        no_data_fig = {
            'layout': {
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': 'Please select two different teams.',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 16}
                }],
                'template': 'plotly_dark'
            }
        }
        return no_data_fig, None, None # Return empty figure and None for KPIs/Table

    # Filter matches between the two selected teams
    h2h_df_full = df[((df['Home Team'] == team1) & (df['Away Team'] == team2)) |
                ((df['Home Team'] == team2) & (df['Away Team'] == team1))].copy()

    # --- Handle No Data --- (Use h2h_df_full)
    if h2h_df_full.empty:
        # Fully formed error dictionary
        no_data_fig = {
            'layout': {
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': f'No match history found between {team1} and {team2}.',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 16}
                }],
                'template': 'plotly_dark'
            }
        }
        return no_data_fig, "No match history.", None

    # --- Calculate Overall H2H Stats ---
    team1_wins = h2h_df_full[h2h_df_full['Winner'] == team1].shape[0]
    team2_wins = h2h_df_full[h2h_df_full['Winner'] == team2].shape[0]
    draws = h2h_df_full[h2h_df_full['Winner'] == 'Draw'].shape[0]
    total_matches_h2h = len(h2h_df_full)

    # Calculate detailed stats for both teams
    team1_stats = {}
    team2_stats = {}

    # Home performance
    team1_home = h2h_df_full[h2h_df_full['Home Team'] == team1]
    team2_home = h2h_df_full[h2h_df_full['Home Team'] == team2]
    
    # Win rates
    team1_stats['Win Rate'] = (team1_wins / total_matches_h2h * 100) if total_matches_h2h > 0 else 0
    team2_stats['Win Rate'] = (team2_wins / total_matches_h2h * 100) if total_matches_h2h > 0 else 0
    
    # Home win rates
    team1_stats['Home Win Rate'] = (team1_home[team1_home['Winner'] == team1].shape[0] / len(team1_home) * 100) if len(team1_home) > 0 else 0
    team2_stats['Home Win Rate'] = (team2_home[team2_home['Winner'] == team2].shape[0] / len(team2_home) * 100) if len(team2_home) > 0 else 0

    # Clean sheet calculations (matches without conceding any goals)
    team1_clean_sheets = (team1_home[team1_home['Away Goals'] == 0].shape[0] + 
                         h2h_df_full[(h2h_df_full['Away Team'] == team1) & 
                                   (h2h_df_full['Home Goals'] == 0)].shape[0])
    team2_clean_sheets = (team2_home[team2_home['Away Goals'] == 0].shape[0] + 
                         h2h_df_full[(h2h_df_full['Away Team'] == team2) & 
                                   (h2h_df_full['Home Goals'] == 0)].shape[0])
    
    team1_stats['Clean Sheets'] = (team1_clean_sheets / total_matches_h2h * 100) if total_matches_h2h > 0 else 0
    team2_stats['Clean Sheets'] = (team2_clean_sheets / total_matches_h2h * 100) if total_matches_h2h > 0 else 0

    # Recent form (last 5 matches - weighted by recency)
    recent_matches = h2h_df_full.sort_values('Date', ascending=False).head(5)
    
    # Calculate weighted recent form (more recent matches count more)
    weights = [5, 4, 3, 2, 1]  # Weights for last 5 matches (most recent = 5 points)
    team1_recent_points = 0
    team2_recent_points = 0
    max_points = sum(weights)  # Maximum possible points (15)
    
    for i, match in enumerate(recent_matches.itertuples()):
        if match.Winner == team1:
            team1_recent_points += weights[i]
        elif match.Winner == team2:
            team2_recent_points += weights[i]
        else:  # Draw
            team1_recent_points += weights[i] * 0.5
            team2_recent_points += weights[i] * 0.5
    
    team1_stats['Recent Form'] = (team1_recent_points / max_points * 100)
    team2_stats['Recent Form'] = (team2_recent_points / max_points * 100)

    # Calculate scoring stats
    team1_goals = (h2h_df_full[h2h_df_full['Home Team'] == team1]['Home Goals'].sum() +
                  h2h_df_full[h2h_df_full['Away Team'] == team1]['Away Goals'].sum())
    team2_goals = (h2h_df_full[h2h_df_full['Home Team'] == team2]['Home Goals'].sum() +
                  h2h_df_full[h2h_df_full['Away Team'] == team2]['Away Goals'].sum())
    
    team1_avg_goals = team1_goals / total_matches_h2h if total_matches_h2h > 0 else 0
    team2_avg_goals = team2_goals / total_matches_h2h if total_matches_h2h > 0 else 0
    total_avg_goals = (team1_goals + team2_goals) / total_matches_h2h if total_matches_h2h > 0 else 0
    
    # Calculate high-scoring match percentage
    high_scoring_matches = h2h_df_full[
        (h2h_df_full['Home Goals'] + h2h_df_full['Away Goals']) > 2.5
    ].shape[0]
    high_scoring_percentage = (high_scoring_matches / total_matches_h2h * 100) if total_matches_h2h > 0 else 0

    # Create KPI div with metrics help button
    kpi_stats = f"Avg Goals/Match: {total_avg_goals:.2f} | Over 2.5 Goals: {high_scoring_percentage:.1f}%"
    
    kpi_div = dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Strong("H2H Stats (All Time): ", className="align-middle"),
                html.Button(
                    "?",
                    id="metrics-help",
                    className="btn btn-info btn-sm rounded-circle mx-1",
                    style={
                        'width': '24px',
                        'height': '24px',
                        'padding': '0px',
                        'lineHeight': '24px',
                        'textAlign': 'center',
                        'verticalAlign': 'middle'
                    }
                ),
                html.Span(kpi_stats, className="align-middle")
            ], className="d-flex align-items-center"),
            
            dbc.Modal([
                dbc.ModalHeader("Understanding the Metrics"),
                dbc.ModalBody([
                    html.P([html.Strong("Win Rate: "), "Percentage of total matches won"]),
                    html.P([html.Strong("Home Win Rate: "), "Success rate when playing at home"]),
                    html.P([html.Strong("Clean Sheets: "), "Defensive strength - % of matches where team kept opponent from scoring (0-0 or a win/loss without conceding)"]),
                    html.Div([
                        html.P([
                            html.Strong("Recent Form: "), 
                            "Form rating based on the last 5 competitive matches, with more recent results weighted higher:"
                        ]),
                        html.Div([
                            "• Latest match: 33% impact",
                            html.Br(),
                            "• 2nd latest: 27% impact",
                            html.Br(),
                            "• 3rd latest: 20% impact",
                            html.Br(),
                            "• 4th latest: 13% impact",
                            html.Br(),
                            "• 5th latest: 7% impact",
                        ], style={'marginLeft': '15px', 'marginTop': '5px', 'marginBottom': '5px'}),
                        html.P([
                            "Win = 100% of points, Draw = 50%, Loss = 0%. ",
                            "Helps identify teams in good form regardless of historical stats."
                        ], style={'marginTop': '5px'})
                    ])
                ])
            ], id="metrics-modal", is_open=False),
            
            html.Div(id='h2h-kpis', className="mt-2"),
            html.Div(id='h2h-table', className="mt-2")
        ])
    ], className="mb-3", style={'backgroundColor': 'rgba(255, 255, 255, 0.05)'})

    print("Debug: KPI div structure:", kpi_div)  # Debug print

    try:
        # Create radar chart with tooltips
        categories = ['Win Rate', 'Home Win Rate', 'Clean Sheets', 'Recent Form']
        closed_categories = categories + [categories[0]] # Close the loop for theta
        
        # Find the maximum value to help set the range (already done, range is 0-100)
        # max_value = max(
        #     max(team1_stats[cat] for cat in categories),
        #     max(team2_stats[cat] for cat in categories)
        # )
        # # Round up to nearest 5% for clean scale
        # range_max = min(75, ((max_value // 5) + 1) * 5) # This is now overridden by fixed 0-100 range
        
        fig = go.Figure()

        # Prepare r values and close them
        r_team1 = [team1_stats[cat] for cat in categories] + [team1_stats[categories[0]]]
        r_team2 = [team2_stats[cat] for cat in categories] + [team2_stats[categories[0]]]

        # Add traces for both teams with fill
        fig.add_trace(go.Scatterpolar(
            r=r_team1, # Use closed r values
            theta=closed_categories, # Use closed categories
            name=team1,
            fill='toself',
            fillcolor='rgba(140, 81, 10, 0.1)',  # Light brown - increased opacity
            line=dict(color='#8c510a', width=3),  # Dark brown
            mode='lines+markers',
            marker=dict(size=8, symbol='circle'),
            hoveron='points',  # Add this line
            hovertemplate=(
                "<b>%{theta}</b><br>" +
                "Value: %{r:.1f}%<br>" +
                "<extra>%{fullData.name}</extra>"
            )
        ))
        fig.add_trace(go.Scatterpolar(
            r=r_team2, # Use closed r values
            theta=closed_categories, # Use closed categories
            name=team2,
            fill='toself',
            fillcolor='rgba(1, 133, 113, 0.1)',  # Light teal - increased opacity
            line=dict(color='#018571', width=3),  # Dark teal
            mode='lines+markers',
            marker=dict(size=8, symbol='circle'),
            hoveron='points',  # Add this line
            hovertemplate=(
                "<b>%{theta}</b><br>" +
                "Value: %{r:.1f}%<br>" +
                "<extra>%{fullData.name}</extra>"
            )
        ))

        # Update layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],  # Set range to 0-100 for percentages
                    ticksuffix="%",
                    gridcolor="rgba(255, 255, 255, 0.2)",
                    showline=False,
                    tickfont=dict(size=10),
                    dtick=20  # Adjusted dtick for 0-100 range
                ),
                angularaxis=dict(
                    gridcolor="rgba(255, 255, 255, 0.2)",
                    linecolor="rgba(255, 255, 255, 0.2)",
                    tickfont=dict(size=12)
                ),
                bgcolor="rgba(0, 0, 0, 0)"
            ),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=1.1,
                xanchor="left",
                x=0.01
            ),
            title=dict(
                text=f"Head-to-Head Analysis: {team1} vs {team2}<br>" +
                     f"<sup>{total_matches_h2h} Matches | Avg Goals: {team1_avg_goals:.2f} vs {team2_avg_goals:.2f}</sup>",
                y=0.95,
                x=0.5,
                xanchor='center',
                yanchor='top'
            ),
            template='plotly_dark',
            height=500,
            margin=dict(l=80, r=80, t=100, b=50),
            hovermode='closest'
        )

    except Exception as e:
        print(f"Error creating H2H radar chart: {e}")
        no_data_fig = {
            'layout': {
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': f'Could not generate plot: {e}',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 12}
                }],
                'template': 'plotly_dark'
            }
        }
        return no_data_fig, kpi_div, None

    # --- Calculate KPIs (Use h2h_df_full) ---
    total_goals = h2h_df_full['Home Goals'].sum() + h2h_df_full['Away Goals'].sum()
    avg_goals_per_match = (total_goals / total_matches_h2h) if total_matches_h2h > 0 else 0
    h2h_df_full['Total Goals'] = h2h_df_full['Home Goals'] + h2h_df_full['Away Goals']
    over_2_5 = h2h_df_full[h2h_df_full['Total Goals'] > 2.5].shape[0]
    perc_over_2_5 = (over_2_5 / total_matches_h2h * 100) if total_matches_h2h > 0 else 0

    kpi_div = html.Div([
        html.Strong("H2H Stats (All Time): "),
        f"Avg Goals/Match: {avg_goals_per_match:.2f} | ",
        f"Over 2.5 Goals: {perc_over_2_5:.1f}%"
    ])

    # --- Create Recent Matches Table (Last 5 matches) ---
    table_title = "Last 5 Meetings:"
    h2h_df_filtered = h2h_df_full # Always use full H2H data for the table base

    # Sort and select top 5 for display
    recent_matches_df = h2h_df_filtered.sort_values('Date', ascending=False).head(5)

    # Generate table or 'no matches' message
    if not recent_matches_df.empty:
        # Select and rename columns for display
        display_columns = ['Date', 'Home Team', 'Home Goals', 'Away Goals', 'Away Team', 'Tournament']
        recent_matches_df_display = recent_matches_df[display_columns].copy()
        recent_matches_df_display['Date'] = recent_matches_df_display['Date'].dt.strftime('%Y-%m-%d') # Format date

        table_div = html.Div([
            html.Strong(table_title),
            dash_table.DataTable(
                id='h2h-results-table',
                data=recent_matches_df_display.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in recent_matches_df_display.columns],
                style_cell={'textAlign': 'left', 'backgroundColor': '#333', 'color': 'white', 'border': '1px solid #555', 'padding': '5px'},
                style_header={'backgroundColor': '#555', 'fontWeight': 'bold'},
                style_table={'overflowX': 'auto'},
                page_size=5
            )
        ])
    else:
        # This case should ideally not happen if h2h_df_full wasn't empty initially
        table_div = html.Div("No H2H matches found to display in table.")

    return fig, kpi_div, table_div

# --- Callback to update Team 2 options based on Team 1 AND Tournament --- #
@app.callback(
    [Output('team2-dropdown-v4', 'options'),
     Output('team2-dropdown-v4', 'value', allow_duplicate=True)],
    Input('team1-dropdown-v4', 'value'), # Removed tournament input
    State('team2-dropdown-v4', 'value'),
    prevent_initial_call=True
)
def set_team2_options(selected_team1, current_team2_value): # Removed selected_tournament
    global df, all_teams

    if not selected_team1:
        # If no team1 is selected, Team2 can be any team (excluding None or hypothetical self)
        available_teams_for_t2 = all_teams
        new_options_t2 = [{'label': team, 'value': team} for team in available_teams_for_t2]
        new_value_t2 = current_team2_value # Keep current if possible
        if current_team2_value not in available_teams_for_t2:
             new_value_t2 = available_teams_for_t2[0] if available_teams_for_t2 else None
        return new_options_t2, new_value_t2

    # Find teams that have played against selected_team1
    home_matches = df[df['Home Team'] == selected_team1]['Away Team']
    away_matches = df[df['Away Team'] == selected_team1]['Home Team']
    opponents = pd.concat([home_matches, away_matches]).unique()
    
    available_teams_for_t2 = sorted([team for team in opponents if team != selected_team1 and pd.notna(team)])

    new_options_t2 = [{'label': team, 'value': team} for team in available_teams_for_t2]
    
    new_value_t2 = current_team2_value
    if current_team2_value not in available_teams_for_t2:
        new_value_t2 = available_teams_for_t2[0] if available_teams_for_t2 else None
        
    return new_options_t2, new_value_t2

# --- Callback to update Team 1 options based on Team 2 AND Tournament --- #
@app.callback(
    [Output('team1-dropdown-v4', 'options'),
     Output('team1-dropdown-v4', 'value', allow_duplicate=True)],
    Input('team2-dropdown-v4', 'value'), # Removed tournament input
    State('team1-dropdown-v4', 'value'),
    prevent_initial_call=True
)
def set_team1_options(selected_team2, current_team1_value): # Removed selected_tournament
    global df, all_teams

    if not selected_team2:
        # If no team2 is selected, Team1 can be any team
        available_teams_for_t1 = all_teams
        new_options_t1 = [{'label': team, 'value': team} for team in available_teams_for_t1]
        new_value_t1 = current_team1_value
        if current_team1_value not in available_teams_for_t1:
            new_value_t1 = available_teams_for_t1[0] if available_teams_for_t1 else None
        return new_options_t1, new_value_t1

    # Find teams that have played against selected_team2
    home_matches = df[df['Home Team'] == selected_team2]['Away Team']
    away_matches = df[df['Away Team'] == selected_team2]['Home Team']
    opponents = pd.concat([home_matches, away_matches]).unique()

    available_teams_for_t1 = sorted([team for team in opponents if team != selected_team2 and pd.notna(team)])
    new_options_t1 = [{'label': team, 'value': team} for team in available_teams_for_t1]

    new_value_t1 = current_team1_value
    if current_team1_value not in available_teams_for_t1:
        new_value_t1 = available_teams_for_t1[0] if available_teams_for_t1 else None

    return new_options_t1, new_value_t1

# --- Callbacks to sync Country Dropdowns V1 and V3 --- #
@app.callback(
    Output('country-dropdown-v3', 'value'),
    Input('country-dropdown-v1', 'value'),
    State('country-dropdown-v3', 'value'), # Add current value of v3 as State
    prevent_initial_call=True
)
def sync_v3_from_v1(selected_country_v1, current_country_v3):
    # If v1 is updated and is a valid country (not None), and it's different from v3, update v3.
    if selected_country_v1 and selected_country_v1 != 'Overall' and selected_country_v1 != current_country_v3:
        return selected_country_v1
    return dash.no_update

@app.callback(
    Output('country-dropdown-v1', 'value'),
    Input('country-dropdown-v3', 'value'),
    State('country-dropdown-v1', 'value'), # Add current value of v1 as State
    State('country-dropdown-v1', 'options'), # Get current options of v1
    prevent_initial_call=True
)
def sync_v1_from_v3(selected_country_v3, current_country_v1, v1_options):
    if selected_country_v3 and selected_country_v3 != 'Overall':
        # Check if selected_country_v3 is a valid option in v1's current dynamic options
        v1_option_values = [opt['value'] for opt in v1_options]
        if selected_country_v3 in v1_option_values and selected_country_v3 != current_country_v1:
            return selected_country_v3
    # If v3 is 'Overall', or if v3's country is already set in v1, or v3 is not a valid option for v1, do nothing to v1
    return dash.no_update

# Add callback for the metrics modal
@app.callback(
    Output("metrics-modal", "is_open"),
    [Input("metrics-help", "n_clicks")],
    [State("metrics-modal", "is_open")],
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

# --- New Callback for Top 3 FIFA Ranking from CSV ---
@app.callback(
    Output('top-3-ranking-display', 'children'),
    [Input('ranking-year-dropdown', 'value'),
     Input('country-dropdown-v1', 'value'), 
     Input('country-dropdown-v3', 'value')] # Added country-dropdown-v3 input
)
def update_top_3_ranking(selected_year, selected_country_v1, selected_country_v3): # Added selected_country_v3 parameter
    if selected_year is None or df_ranking.empty:
        return dbc.Alert("Ranking data not available or year not selected.", color="warning", className="mt-2")

    # Filter for the selected year
    yearly_data = df_ranking[df_ranking['year'] == selected_year]
    if yearly_data.empty:
        return dbc.Alert(f"No ranking data available for {selected_year}.", color="info", className="mt-2")

    # Find the latest ranking date within that year
    latest_date_in_year = yearly_data['rank_date'].max()
    latest_ranking_data_for_year = yearly_data[yearly_data['rank_date'] == latest_date_in_year]
    
    top_3_df = latest_ranking_data_for_year.sort_values(by='rank', ascending=True).head(3)

    if top_3_df.empty:
        return dbc.Alert(f"No top 3 ranking data found for the latest records in {selected_year}.", color="info", className="mt-2")

    medals = ["🥇", "🥈", "🥉"]
    display_elements = []
    top_3_country_names = []

    for i, (idx, row) in enumerate(top_3_df.iterrows()):
        rank_text = f"{medals[i]} {row['country_full']} (Rank: {int(row['rank'])})"
        display_elements.append(html.P(rank_text, style={'margin': '5px 0', 'fontSize': '1.2rem'}))
        top_3_country_names.append(row['country_full'])
    
    # Determine the specific country to show rank for, based on V1 then V3
    country_to_show_rank_for = None
    if selected_country_v1:
        country_to_show_rank_for = selected_country_v1
    elif selected_country_v3 and selected_country_v3 != 'Overall':
        country_to_show_rank_for = selected_country_v3
    
    if country_to_show_rank_for:
        selected_country_rank_info = latest_ranking_data_for_year[latest_ranking_data_for_year['country_full'] == country_to_show_rank_for]
        
        if not selected_country_rank_info.empty:
            if country_to_show_rank_for not in top_3_country_names:
                rank_val = int(selected_country_rank_info.iloc[0]['rank'])
                display_elements.append(html.Hr(style={'marginTop': '10px', 'marginBottom': '10px'}))
                display_elements.append(html.P(
                    f"{country_to_show_rank_for} Rank: {rank_val}", 
                    style={'margin': '5px 0', 'fontSize': '1.1rem', 'fontWeight': 'bold'}
                ))
        else:
            display_elements.append(html.Hr(style={'marginTop': '10px', 'marginBottom': '10px'}))
            display_elements.append(html.P(
                f"{country_to_show_rank_for} not ranked on {latest_date_in_year.strftime('%Y-%m-%d')}.", 
                style={'fontSize': '0.9rem', 'fontStyle': 'italic'}
            ))
            
    return html.Div(display_elements, className="mt-2")

# --- New Callback for Cascading Country Dropdown (V1) based on Tournament (V2) ---
@app.callback(
    [Output('country-dropdown-v1', 'options'),
     Output('country-dropdown-v1', 'value', allow_duplicate=True)], # Allow duplicate for resetting value
    Input('tournament-dropdown-v2', 'value'),
    State('country-dropdown-v1', 'value'), # Current value of country-dropdown-v1
    prevent_initial_call=True # Prevent initial call to avoid issues during app load
)
def update_country_dropdown_v1_options(selected_tournament, current_country_v1_value):
    global df # Ensure we are using the global DataFrame

    if selected_tournament == 'All' or not selected_tournament:
        # If 'All Tournaments' or no tournament is selected, show all teams
        available_teams = all_teams
    else:
        # Filter teams that participated in the selected tournament
        tournament_df = df[df['Tournament'] == selected_tournament]
        home_teams_in_tournament = tournament_df['Home Team'].unique()
        away_teams_in_tournament = tournament_df['Away Team'].unique()
        available_teams = sorted(list(set(home_teams_in_tournament) | set(away_teams_in_tournament)))

    new_options = [{'label': team, 'value': team} for team in available_teams]
    
    new_value = current_country_v1_value
    if current_country_v1_value not in available_teams:
        # If current selection is no longer valid, try to set to first available or None
        new_value = available_teams[0] if available_teams else None
        
    return new_options, new_value

# --- New Callback for Cascading Tournament Dropdown (V2) based on Country (V1) ---
@app.callback(
    [Output('tournament-dropdown-v2', 'options'),
     Output('tournament-dropdown-v2', 'value', allow_duplicate=True)],
    Input('country-dropdown-v1', 'value'),
    State('tournament-dropdown-v2', 'value'),
    prevent_initial_call=True
)
def update_tournament_dropdown_v2_options(selected_country, current_tournament_v2_value):
    global df # Ensure we are using the global DataFrame
    global all_tournaments # Ensure we have access to all unique tournaments

    if not selected_country:
        # If no country is selected, show all tournaments
        available_tournaments = all_tournaments
    else:
        # Filter tournaments that the selected country participated in
        country_games_df = df[(df['Home Team'] == selected_country) | (df['Away Team'] == selected_country)]
        available_tournaments = sorted(country_games_df['Tournament'].unique())

    # Always include 'All Tournaments' option
    new_options = [{'label': 'All Tournaments', 'value': 'All'}] + \
                  [{ 'label': t, 'value': t } for t in available_tournaments]
    
    new_value = current_tournament_v2_value
    # Check if current value is valid with the new options
    valid_values = [opt['value'] for opt in new_options]
    if current_tournament_v2_value not in valid_values:
        new_value = 'All' # Default to 'All' if current selection is invalid
        
    return new_options, new_value

# --- New Callback for Cascading Country Dropdown (V3) based on Tournament (V2) ---
@app.callback(
    [Output('country-dropdown-v3', 'options'),
     Output('country-dropdown-v3', 'value', allow_duplicate=True)],
    Input('tournament-dropdown-v2', 'value'),
    State('country-dropdown-v3', 'value'),
    prevent_initial_call=True
)
def update_country_dropdown_v3_options(selected_tournament, current_country_v3_value):
    global df # Ensure we are using the global DataFrame
    global all_teams # Ensure we have access to all unique teams

    if selected_tournament == 'All' or not selected_tournament:
        # If 'All Tournaments' or no tournament is selected, show all teams plus 'Overall'
        available_teams_for_v3 = all_teams
    else:
        # Filter teams that participated in the selected tournament
        tournament_df = df[df['Tournament'] == selected_tournament]
        home_teams_in_tournament = tournament_df['Home Team'].unique()
        away_teams_in_tournament = tournament_df['Away Team'].unique()
        available_teams_for_v3 = sorted(list(set(home_teams_in_tournament) | set(away_teams_in_tournament)))

    new_options_v3 = [{'label': 'Overall', 'value': 'Overall'}] + \
                     [{ 'label': team, 'value': team } for team in available_teams_for_v3]
    
    new_value_v3 = current_country_v3_value
    # Check if current value is valid with the new options
    valid_values_v3 = [opt['value'] for opt in new_options_v3]
    if current_country_v3_value not in valid_values_v3:
        new_value_v3 = 'Overall' # Default to 'Overall' if current selection is invalid
        
    return new_options_v3, new_value_v3

# --- Callbacks to sync H2H Team 1 from other country dropdowns ---
@app.callback(
    Output('team1-dropdown-v4', 'value', allow_duplicate=True),
    Input('country-dropdown-v1', 'value'),
    prevent_initial_call=True
)
def sync_h2h_team1_from_v1(selected_country_v1):
    if selected_country_v1: # country-dropdown-v1 always has a country if it has options
        return selected_country_v1
    return dash.no_update

@app.callback(
    Output('team1-dropdown-v4', 'value', allow_duplicate=True),
    Input('country-dropdown-v3', 'value'),
    prevent_initial_call=True
)
def sync_h2h_team1_from_v3(selected_country_v3):
    if selected_country_v3 and selected_country_v3 != 'Overall':
        return selected_country_v3
    return dash.no_update

# --- 5. Run the App ---
if __name__ == '__main__':
    # Make sure the 'assets' folder exists for app.get_asset_url to work
    import os
    if not os.path.exists('assets'):
        os.makedirs('assets')
    app.run(debug=True) # Changed from app.run_server
 