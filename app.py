import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc # Import dash-bootstrap-components
import plotly.graph_objects as go

# --- 1. Data Loading and Preprocessing ---
try:
    df = pd.read_csv('international_matches.csv')
except FileNotFoundError:
    print("Error: 'international_matches.csv' not found. Make sure the file is in the same directory.")
    exit()

# Convert Date to datetime objects
df['Date'] = pd.to_datetime(df['Date'], format='mixed', errors='coerce')
df = df.dropna(subset=['Date'])

# Determine Winner/Draw
df['IsDraw'] = df['Winning Team'].isnull() & df['Losing Team'].isnull()
df['Winner'] = df.apply(lambda row: row['Home Team'] if row['Home Goals'] > row['Away Goals'] else (row['Away Team'] if row['Away Goals'] > row['Home Goals'] else 'Draw'), axis=1)
df['IsHomeWin'] = df['Winner'] == df['Home Team']
df['IsAwayWin'] = df['Winner'] == df['Away Team']

# Simplify Tournament Names (Optional - can group similar tournaments)
# Example: df['TournamentSimple'] = df['Tournament'].replace({...})

# Get unique values for dropdowns
all_teams = sorted(pd.concat([df['Home Team'], df['Away Team']]).unique())
all_tournaments = sorted(df['Tournament'].unique())

# --- 2. Dash App Initialization with Bootstrap ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Football Match Insights"

# --- 3. App Layout with Bootstrap Components ---
app.layout = dbc.Container([
    # Row for Banner Image
    dbc.Row([
        dbc.Col(html.Img(src=app.get_asset_url('banner.jpg'),
                         style={'height': '200px', 'width': '100%', 'objectFit': 'cover'}), width=12)
    ], className="mb-4"), # Add margin below banner

    # Row for Title
    dbc.Row(dbc.Col(html.H1("Smart Betting Insights Dashboard"), width=12), className="mb-1 text-center"), # Reduced margin-bottom
    dbc.Row(dbc.Col(html.H5("Based on Historical International Matches", className="text-muted"), width=12), className="mb-4 text-center"), # Added subtitle

    # --- Tabs ---
    dcc.Tabs(id="tabs", value='tab-dashboard', children=[
        # --- Dashboard Tab ---
        dcc.Tab(label='Dashboard', value='tab-dashboard', children=[
            dbc.Container([ # Wrap dashboard content in a container for padding
                # --- Row 1: Win Rate & Goal Trends ---
                dbc.Row([
                    # Col 1: Win Rate Analysis
                    dbc.Col([
                        html.H4("Win Rate Analysis by Tournament Type"),
                        html.Label("Select Country:"),
                        dcc.Dropdown(
                            id='country-dropdown-v1',
                            options=[{'label': team, 'value': team} for team in all_teams],
                            value='Brazil'
                        ),
                        dcc.Graph(id='win-rate-tournament-graph')
                    ], width=6, className="border rounded p-3"), # Added border, rounding, padding

                    # Col 2: Goal Scoring Trends
                    dbc.Col([
                        html.H4("Goal Scoring Trends (Home vs. Away)"),
                        html.Label("Select Tournament Type (Optional):"),
                        dcc.Dropdown(
                            id='tournament-dropdown-v2',
                            options=[{'label': 'All Tournaments', 'value': 'All'}] + [{'label': t, 'value': t} for t in all_tournaments],
                            value='All'
                        ),
                        dcc.Graph(id='goal-trends-graph')
                        # Optional: Add a date range slider here
                    ], width=6, className="border rounded p-3") # Added border, rounding, padding
                ], className="mb-4"), # Added margin bottom

                # --- Row 2: Home/Away & Head-to-Head ---
                dbc.Row([
                    # Col 1: Home vs Away Performance (Reverted)
                    dbc.Col([
                        html.H4("Home vs. Away Performance"), # Reverted title
                        html.Label("Select Country/Overall:"),
                        dcc.Dropdown(
                            id='country-dropdown-v3',
                            options=[{'label': 'Overall', 'value': 'Overall'}] +
                                    [{'label': team, 'value': team} for team in all_teams],
                            value='Overall'
                        ),
                        dcc.Graph(id='home-away-graph')
                    ], width=6, className="border rounded p-3"),

                    # Col 2: Head-to-Head Comparison
                    dbc.Col([
                        html.H4("Head-to-Head Comparison"),
                         dbc.Row([ # Inner row for team selection dropdowns
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
                        html.Div(id='h2h-kpis', className="mt-2"), # Placeholder for KPIs
                        html.Div(id='h2h-table', className="mt-2") # Placeholder for table
                    ], width=6, className="border rounded p-3") # Added border, rounding, padding
                ])
            ], fluid=True, className="pt-3") # Add padding top
        ]),

        # --- Information Tab (Reverted relevant text) ---
        dcc.Tab(label='Betting Insights Guide', value='tab-guide', children=[
            dbc.Container([
                html.H3("Understanding the Insights", className="text-center mt-3 mb-4"),
                html.P("This dashboard uses historical international match data...", # Intro text remains same
                       className="text-center mb-4 lead"),
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Home vs. Away Performance"), # Reverted Card Header
                        dbc.CardBody([
                            html.P("Teams often play differently at home versus away.", className="card-text"),
                            html.Small("Look for significant differences in win % between Home and Away games on the Dashboard."), # Reverted text
                        ])
                    ]), width=6, className="mb-3"),
                    dbc.Col(dbc.Card([
                        dbc.CardHeader("Head-to-Head (H2H) Record"),
                        dbc.CardBody([
                            html.P("Past matchups can reveal patterns. Focus on recent, competitive games.", className="card-text"),
                            html.Small("Check the KPIs for goal trends (Avg Goals, Over/Under %) in the H2H section."),
                        ])
                    ]), width=6, className="mb-3"),
                ]),
                dbc.Row([
                     dbc.Col(dbc.Card([
                        dbc.CardHeader("Recent Form & Tournament Context"),
                        dbc.CardBody([
                            html.P("A team's last few competitive games indicate current momentum.", className="card-text"),
                            html.Small("Note that competitive matches (World Cup, Qualifiers) are usually prioritized over Friendlies."),
                            # html.Div("[Example Graph/Visual]")
                        ])
                    ]), width=6, className="mb-3"),
                     dbc.Col(dbc.Card([
                        dbc.CardHeader("Data Limitations & Responsible Betting"),
                        dbc.CardBody([
                            html.P("Historical data is informative but not predictive. Combine insights with current news.", className="card-text"),
                            html.Small("Always bet responsibly. Past performance doesn't guarantee future results."),
                            # html.Div("[Example Graph/Visual]")
                        ])
                    ]), width=6, className="mb-3"),
                ]),
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
    # Calculate perc on the counts df directly
    results_perc = results_by_tournament_counts[valid_rows].apply(lambda x: x * 100 / x.sum(), axis=1).reset_index()

    if results_perc.empty:
         return {
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
     Input('country-dropdown-v3', 'value')]
)
def update_goal_trends_graph(selected_tournament_dropdown, win_rate_clickData, selected_country_v3):

    trigger_id = dash.ctx.triggered_id
    filter_tournament = selected_tournament_dropdown # Default tournament filter

    # --- Determine Tournament Filter Based on Trigger --- #
    # If the radial chart click triggered it, try to use that tournament
    if trigger_id == 'win-rate-tournament-graph' and win_rate_clickData:
        try:
            clicked_tournament = win_rate_clickData['points'][0]['theta']
            filter_tournament = clicked_tournament
            print(f"Filtering Goal Trends by clicked tournament: {clicked_tournament}")
        except (KeyError, IndexError, TypeError):
            print("Could not extract tournament from win_rate_clickData")
            filter_tournament = selected_tournament_dropdown # Fallback to dropdown
    # If triggered by dropdown, use its value (filter_tournament is already set)
    elif trigger_id == 'tournament-dropdown-v2':
         print(f"Filtering Goal Trends by dropdown: {filter_tournament}")
    # If triggered by country dropdown, use the existing tournament filter
    elif trigger_id == 'country-dropdown-v3':
         print(f"Filtering Goal Trends by Country change: {selected_country_v3} with Tournament: {filter_tournament}")


    # --- Data Filtering --- #
    filtered_df = df.copy()
    # Apply Country Filter first (from Home/Away Dropdown V3)
    country_filter_text = "Overall"
    if selected_country_v3 and selected_country_v3 != 'Overall':
        filtered_df = filtered_df[(filtered_df['Home Team'] == selected_country_v3) | (filtered_df['Away Team'] == selected_country_v3)]
        country_filter_text = selected_country_v3

    # Apply Tournament Filter (from own dropdown or radial click)
    tournament_filter_text = "All Tournaments"
    if filter_tournament and filter_tournament != 'All':
        # Apply on top of country filter
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
            line=dict(shape='spline', width=1),
            fill='tozeroy',
            name='Home Goals',
            marker_color='#9467bd',
            opacity=0.7
        ))

    # Add Away Goals trace (Only if data exists for the filtered selection)
    if 'Away Goals' in avg_goals_yearly.columns and not avg_goals_yearly['Away Goals'].isnull().all():
        fig.add_trace(go.Scatter(
            x=avg_goals_yearly['Date'],
            y=avg_goals_yearly['Away Goals'],
            mode='lines',
            line=dict(shape='spline', width=1),
            fill='tozeroy',
            name='Away Goals',
            marker_color='#2ca02c',
            opacity=0.7
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

    # --- Calculate Overall H2H Wins/Draws (Used for Sankey values AND labels) ---
    team1_wins = h2h_df_full[h2h_df_full['Winner'] == team1].shape[0]
    team2_wins = h2h_df_full[h2h_df_full['Winner'] == team2].shape[0]
    draws = h2h_df_full[h2h_df_full['Winner'] == 'Draw'].shape[0]

    # --- Create Sankey Diagram --- (No changes needed here for this interaction)
    try:
        # Define nodes and colors - Include counts in outcome labels
        label = [
            team1,
            team2,
            f'{team1} Wins ({team1_wins})',
            f'{team2} Wins ({team2_wins})',
            f'Draw ({draws})'
        ]
        # Colorblind Friendly: Node Colors (Purple/Green for teams, Blue/Grey for outcomes)
        colors = [
            '#9467bd', # Team 1 (Purple)
            '#2ca02c', # Team 2 (Green)
            '#1f77b4', # Win Outcome (Blue)
            '#1f77b4', # Win Outcome (Blue)
            '#7f7f7f'  # Draw Outcome (Grey)
        ]

        source = []
        target = []
        value = []
        link_colors = []

        # Define RGBA colors for links with transparency based on new node colors
        alpha = 0.6
        link_color_t1 = f'rgba(148, 103, 189, {alpha})'
        link_color_t2 = f'rgba(44, 160, 44, {alpha})'

        # Calculate flows (Use h2h_df_full)
        t1_home_df = h2h_df_full[h2h_df_full['Home Team'] == team1]
        t1_home_wins_count = t1_home_df[t1_home_df['Winner'] == team1].shape[0]
        t1_home_losses_count = t1_home_df[t1_home_df['Winner'] == team2].shape[0]
        t1_home_draws_count = t1_home_df[t1_home_df['Winner'] == 'Draw'].shape[0]

        if t1_home_wins_count > 0:
            source.append(0); target.append(2); value.append(t1_home_wins_count)
            link_colors.append(link_color_t1)
        if t1_home_losses_count > 0:
            source.append(0); target.append(3); value.append(t1_home_losses_count)
            link_colors.append(link_color_t1)
        if t1_home_draws_count > 0:
            source.append(0); target.append(4); value.append(t1_home_draws_count)
            link_colors.append(link_color_t1)

        t2_home_df = h2h_df_full[h2h_df_full['Home Team'] == team2]
        t2_home_wins_count = t2_home_df[t2_home_df['Winner'] == team2].shape[0]
        t2_home_losses_count = t2_home_df[t2_home_df['Winner'] == team1].shape[0]
        t2_home_draws_count = t2_home_df[t2_home_df['Winner'] == 'Draw'].shape[0]

        if t2_home_wins_count > 0:
            source.append(1); target.append(3); value.append(t2_home_wins_count)
            link_colors.append(link_color_t2)
        if t2_home_losses_count > 0:
            source.append(1); target.append(2); value.append(t2_home_losses_count)
            link_colors.append(link_color_t2)
        if t2_home_draws_count > 0:
            source.append(1); target.append(4); value.append(t2_home_draws_count)
            link_colors.append(link_color_t2)

        # Create the Sankey figure
        fig = go.Figure(data=[go.Sankey(
            arrangement='snap',
            node=dict(
              pad=15,
              thickness=20,
              line=dict(color="#444", width=0.5),
              label=label, # Use labels with counts
              color=colors, # Keep node colors opaque
              hoverinfo='skip' # Skip default node hover info
            ),
            link=dict(
              source=source,
              target=target,
              value=value,
              color=link_colors, # Assign transparent RGBA colors to links
              hoverinfo='all',
              hovertemplate='Matches in %{source.label} resulting in %{target.label}: %{value}x<extra></extra>'
          ))])

        fig.update_layout(title_text=f"H2H Outcomes Flow: {team1} vs {team2}",
                          font_size=12,
                          height=300,
                          margin=dict(l=20, r=20, t=50, b=20),
                          template='plotly_dark')

    except Exception as e:
         print(f"Error creating H2H Sankey chart: {e}")
         # Fully formed error dictionary
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
         return no_data_fig, "Error generating plot.", None

    # --- Calculate KPIs (Use h2h_df_full) ---
    total_goals = h2h_df_full['Home Goals'].sum() + h2h_df_full['Away Goals'].sum()
    total_matches = len(h2h_df_full)
    avg_goals_per_match = (total_goals / total_matches) if total_matches > 0 else 0
    h2h_df_full['Total Goals'] = h2h_df_full['Home Goals'] + h2h_df_full['Away Goals']
    over_2_5 = h2h_df_full[h2h_df_full['Total Goals'] > 2.5].shape[0]
    perc_over_2_5 = (over_2_5 / total_matches * 100) if total_matches > 0 else 0

    kpi_div = html.Div([
        html.Strong("H2H Stats (All Time): "),
        f"Avg Goals/Match: {avg_goals_per_match:.2f} | ",
        f"Over 2.5 Goals: {perc_over_2_5:.1f}%"
    ])

    # --- Create Recent Matches Table (Reverted to always show last 5) ---
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
                page_size=5, # Show only 5 rows if not filtered, otherwise allows more if needed
            )
        ])
    else:
        # This case should ideally not happen if h2h_df_full wasn't empty initially
        table_div = html.Div("No H2H matches found to display in table.")

    return fig, kpi_div, table_div

# --- Callback to update Team 2 options based on Team 1 --- #
@app.callback(
    Output('team2-dropdown-v4', 'options'),
    Input('team1-dropdown-v4', 'value')
)
def set_team2_options(selected_team1):
    return [{'label': team, 'value': team} for team in all_teams if team != selected_team1]

# --- Callback to update Team 1 options based on Team 2 --- #
@app.callback(
    Output('team1-dropdown-v4', 'options'),
    Input('team2-dropdown-v4', 'value')
)
def set_team1_options(selected_team2):
    return [{'label': team, 'value': team} for team in all_teams if team != selected_team2]

# --- Callbacks to sync Country Dropdowns V1 and V3 --- #
@app.callback(
    Output('country-dropdown-v3', 'value'),
    Input('country-dropdown-v1', 'value'),
    prevent_initial_call=True # Avoid triggering on initial load if default values match
)
def sync_v3_from_v1(selected_country):
    return selected_country

@app.callback(
    Output('country-dropdown-v1', 'value'),
    Input('country-dropdown-v3', 'value'),
    prevent_initial_call=True # Avoid triggering on initial load if default values match
)
def sync_v1_from_v3(selected_country):
    # Allow 'Overall' selection in V3 without changing V1 from a specific country
    # Only sync if V3 selects a specific country
    if selected_country != 'Overall':
        return selected_country
    # If V3 is 'Overall', we don't want to force V1 to change
    # Prevent the update to avoid clearing V1 selection
    return dash.no_update

# --- 5. Run the App ---
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)
