# Smart Betting Insights Dashboard

## Introduction
This project is a football visualization dashboard designed to provide smart betting insights. It analyzes historical international match data to reveal trends in team performance, goal scoring, head-to-head results, and more. The dashboard is built using Python with the Dash and Plotly libraries.

The goal is to present complex historical data in an intuitive, interactive, and visually appealing format that can help users make more informed betting decisions.

## Features
The dashboard is organized into two main tabs: a main **Dashboard** for visualizations and a **Betting Insights Guide** for explaining how to interpret the data.

*   **Interactive Visualizations:** The dashboard features several interconnected charts:
    *   **FIFA Top 3 Ranking:** Displays the top 3 ranked teams for a selected year, plus the rank of any team selected in the main dashboard filters.
    *   **Win Rate Analysis:** A radial bar chart showing a selected country's win, loss, and draw percentages across different tournament types.
    *   **Goal Scoring Trends:** An interactive area chart showing a team's or the overall average goals scored at home vs. away over time. This chart can be filtered by tournament or by clicking on the Win Rate chart.
    *   **Home vs. Away Performance:** A grouped bar chart comparing win/loss/draw percentages for home and away games, either for a specific country or for all competitive matches overall.
    *   **Head-to-Head Comparison:** A radar chart comparing two selected teams across key metrics like Win Rate, Home Win Rate, Clean Sheets, and Recent Form. It also includes a table of their last 5 meetings.
*   **Cross-Filtering:** Charts are interactive. For example, selecting a country in one dropdown can update the data and options available in other components.
*   **Betting Insights Guide:** A dedicated tab that explains how to interpret each visualization from a betting perspective, providing tips for markets like Over/Under, Match Outcome, and Both Teams to Score.
*   **Dark Theme:** The dashboard uses a modern, dark "Cyborg" theme from `dash-bootstrap-components` for better visual appeal.

## Implementation Details

### Self-Implemented Work
The core of this project is the `app.py` script, which was written specifically for this assignment. My contributions include:

*   **Data Loading and Preprocessing:** The logic to load the `.csv` datasets, handle date conversions, clean the data, and engineer new features (e.g., `Winner`, `IsDraw`, `IsHomeWin`) using the Pandas library.
*   **Dashboard Layout and UI:** The entire user interface, including the layout of tabs, rows, columns, dropdowns, and graphs, was structured using `dash-bootstrap-components`.
*   **Visualization Generation:** While Plotly Express and Graph Objects are used to create the charts, the data aggregation, calculations (e.g., win percentages, recent form scores, H2H stats), and chart-specific configurations (e.g., colors, labels, tooltips, radar chart setup) are custom logic.
*   **Interactivity (Callbacks):** All the interactivity is powered by Dash callbacks that I implemented. This includes:
    *   Callbacks to update graphs based on user selections in dropdowns.
    *   Callbacks for cross-filtering between different charts (e.g., clicking the win rate chart to filter the goal trends chart).
    *   Callbacks to dynamically update the options within dropdowns based on other selections (cascading dropdowns).
    *   Callbacks to sync selections between related dropdowns.

### Leveraged Libraries
This project relies on several key open-source Python libraries. The code for these libraries was **not** written by me, but I used their functions to build the application.

*   **`pandas`:** Used for all data manipulation tasks. Loading data from CSV files into DataFrames, cleaning data, and performing complex grouping and aggregation operations.
*   **`plotly` / `plotly.express`:** The core library used for creating all the data visualizations, including the radial bar chart, area chart, grouped bar chart, and radar chart.
*   **`dash`:** The main web framework for building the dashboard. It provides the application server and the mechanism for creating interactive components.
*   **`dash-bootstrap-components`:** A component library for Dash that makes it easy to build responsive layouts with a Bootstrap theme (`CYBORG`).
*   **`gunicorn`:** A WSGI server included in `requirements.txt` for potential deployment.

### Data Sources
*   `international_matches.csv`: Contains match-by-match data for international football games.
*   `fifa_ranking-2024-06-20.csv`: A supplementary dataset containing historical FIFA world rankings.

## How to Run the Project

To run this dashboard on your local machine, please follow these steps.

**Prerequisites:**
*   Python 3.7+
*   `pip` (Python package installer)

**Step-by-Step Instructions:**

1.  **Clone the Repository:**
    Download or clone this repository to your local machine.

2.  **Navigate to the Project Directory:**
    Open a terminal or command prompt and navigate to the root directory of the project.
    ```sh
    cd path/to/your/project/folder
    ```

3.  **Create and Activate a Virtual Environment (Recommended):**
    This creates an isolated environment for the project's dependencies.
    ```sh
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

4.  **Install Dependencies:**
    Install all the required Python packages using the `requirements.txt` file.
    ```sh
    pip install -r requirements.txt
    ```

5.  **Run the Application:**
    Execute the `app.py` script. The `debug=True` flag enables hot-reloading.
    ```sh
    python app.py
    ```

6.  **View the Dashboard:**
    Once the server is running, you will see output in your terminal similar to this:
    ```
    Dash is running on http://127.0.0.1:8050/
    ```
    Open this URL (`http://127.0.0.1:8050/`) in your web browser to view and interact with the dashboard.

## Local Development
When running locally, it's best to use Dash's built-in development server with debug mode enabled for features like hot-reloading.

To do this, set the `DEBUG` environment variable to `true` before running the script.

**For macOS/Linux:**
```sh
DEBUG=true python app.py
```

**For Windows (Command Prompt):**
```sh
set DEBUG=true
python app.py
```

## Deployment to Railway
This application is configured for deployment on platforms like Railway.

1.  **`Procfile`:** The included `Procfile` tells Railway to use `gunicorn` (a production-grade WSGI server) to run the application.
2.  **Server Configuration:** The `app.py` script is set up to bind to the host and port provided by Railway's environment variables.
3.  **Deployment:** To deploy, simply connect your GitHub repository to a new project on Railway. Railway will automatically detect the `Procfile` and `requirements.txt` and deploy the application.

A live version of this dashboard is also accessible here: [https://web-production-b8722.up.railway.app/](https://web-production-b8722.up.railway.app/). 
Please note that the initial load and interactions on the deployed version may be slower than running the application locally.

## Code and Source Attribution
The code in `app.py` was developed as part of this university project. The visual and functional components are built upon the open-source libraries listed in the `requirements.txt` file, which are fundamental to the fields of data analysis and web application development in Python.

**Note on AI Assistance:** The Python code in this project was generated with the assistance of an AI coding tool (Gemini 2.5 Pro in Cursor). The AI was used as a pair programmer to accelerate development, implement visualizations, debug code, and structure the application. The prompts and logic for the application's features, data analysis, and overall structure were directed by the human developer. All leveraged libraries are open-source and properly attributed.