# Data Analyze

Link of the app : https://data-analyze-fpqobjzoccgkjueqzdsh8m.streamlit.app/

# Agricultural Climate Analysis Dashboard

## Overview
This interactive dashboard analyzes 35 years of agricultural climate data (1989-2024) to understand climate change impacts on farming conditions. The application provides comprehensive visualizations and insights for temperature trends, precipitation patterns, and seasonal changes.

## Features
- **Navigation**: 4 sections structure the project
  1. The Problem: Introduction to climate change impacts
  2. Analysis: Long-term climate trend visualizations
  3. Interactive Insights: Dynamic data exploration tools
  4. Conclusion
- **Key Visualizations**:
  - Annual temperature evolution trends
  - Precipitation pattern changes
  - Temperature distribution comparisons
  - Monthly temperature heatmaps
  - Seasonal precipitation variability
  - Customizable yearly climate profiles
  - Decadal comparisons
  - Seasonal analysis tools

## Installation

```bash
# Clone the repository
git clone [your-repo-url]

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

## Requirements
- Python 3.8+
- Streamlit
- Pandas
- Plotly
- NumPy

## Usage
```bash
streamlit run dashboard.py
```

## Data Structure
The application expects a CSV file with the following columns:
- Date: YYYY-MM-DD format
- Temperature measurements (daily)
- Precipitation measurements (daily)

## Features Details

### 1. The Problem
- Overview of climate change impact on agriculture
- Context setting for data analysis

### 2. Analysis
- Long-term temperature trends
- Precipitation pattern analysis
- Temperature distribution comparisons
- Seasonal pattern visualization
- Monthly variation analysis

### 3. Interactive Insights
- Year-by-year climate profile exploration
- Decadal comparison tools
- Seasonal analysis with customizable views

### 4. Conclusion
- Agricultural adaptation strategies
- Recommendations for farmers

## Acknowledgments
- Data source: [Agricultural Weather Station]
- Built with Streamlit and Plotly
