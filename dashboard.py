import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

import base64

def add_bg_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

add_bg_local("fondecolo.jpg")

# Fonction de chargement des données
@st.cache_data
def load_data():

    try:
        df = pd.read_csv('Station_Agroclim_INRAE_11170004_daily_1989_2024.csv')
        
        # Détection automatique de la colonne de date
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_cols:
            df['Date'] = pd.to_datetime(df[date_cols[0]])
        else:
            # Si pas de colonne date explicite, essayer la première colonne
            df['Date'] = pd.to_datetime(df.iloc[:, 0])
        
        # Extraction des composants temporels
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df['Day'] = df['Date'].dt.day
        df['Month_Name'] = df['Date'].dt.strftime('%B')
        df['Season'] = df['Month'].map({
            12: 'Winter', 1: 'Winter', 2: 'Winter',
            3: 'Spring', 4: 'Spring', 5: 'Spring',
            6: 'Summer', 7: 'Summer', 8: 'Summer',
            9: 'Fall', 10: 'Fall', 11: 'Fall'
        })
        
        # Identification des colonnes de température (colonnes contenant 'temp', 'T_', 'TX', 'TN', etc.)
        temp_cols = [col for col in df.columns if any(x in col.lower() for x in ['temp', 't_', 'tx', 'tn', 'tg'])]
        
        # Identification des colonnes de précipitations
        precip_cols = [col for col in df.columns if any(x in col.lower() for x in ['precip', 'rain', 'rr', 'pluvio', 'pluie'])]
        
        # Si on trouve des colonnes, on les renomme de manière standard
        if temp_cols:
            # Chercher température moyenne
            temp_mean_cols = [col for col in temp_cols if 'mean' in col.lower() or 'avg' in col.lower() or 'tg' in col.lower() or 'moy' in col.lower()]
            if temp_mean_cols:
                df['Temp_Mean'] = df[temp_mean_cols[0]]
            elif len(temp_cols) >= 2:
                # Si on a min et max, calculer la moyenne
                df['Temp_Mean'] = (df[temp_cols[0]] + df[temp_cols[1]]) / 2
            else:
                df['Temp_Mean'] = df[temp_cols[0]]
            
            # Chercher température max
            temp_max_cols = [col for col in temp_cols if 'max' in col.lower() or 'tx' in col.lower()]
            if temp_max_cols:
                df['Temp_Max'] = df[temp_max_cols[0]]
            
            # Chercher température min
            temp_min_cols = [col for col in temp_cols if 'min' in col.lower() or 'tn' in col.lower()]
            if temp_min_cols:
                df['Temp_Min'] = df[temp_min_cols[0]]
        
        if precip_cols:
            df['Precipitation'] = df[precip_cols[0]]
        
        # Nettoyage des valeurs manquantes
        df = df.dropna(subset=['Date'])
        
        return df
        
    except FileNotFoundError:
        st.error("Fichier non trouvé. Veuillez vous assurer que le fichier CSV est dans le même répertoire que le script.")
        st.stop()
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        st.info("Structure détectée des colonnes pour débogage :")
        st.stop()

# Chargement des données
df = load_data()


# ========================================
# SECTION 1 : LE PROBLÈME
# ========================================
st.set_page_config(layout="wide", page_title="Agricultural Climate Analysis")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Where Do We Go ?",
    [
        "1. THE PROBLEM",
        "2. ANALYSIS",
        "3. INTERACTIVE INSIGHTS",
        "4. CONCLUSION"
    ]
)


if page == "1. THE PROBLEM":
    st.markdown('# 1. THE PROBLEM: Climate Change Impact on Agriculture</p>', unsafe_allow_html=True)


    st.markdown("""
    <strong> Context:</strong> Over the past 35 years, climate change has significantly impacted agricultural conditions. 
    This analysis examines temperature trends, precipitation patterns, and extreme weather events to understand 
    how farming conditions have evolved and what challenges farmers face today.
    """, unsafe_allow_html=True)

elif page == "2. ANALYSIS":
    st.markdown('# 2. ANALYSIS: Long-term Climate Trends</p>', unsafe_allow_html=True)

    # GRAPHIQUE 1 : Évolution de la température moyenne annuelle
    if 'Temp_Mean' in df.columns:
        st.markdown("## Annual Average Temperature Evolution (1989-2024)")
        
        yearly_temp = df.groupby('Year')['Temp_Mean'].mean().reset_index()
        
        fig1 = go.Figure()
        
        # Ligne de température
        fig1.add_trace(go.Scatter(
            x=yearly_temp['Year'],
            y=yearly_temp['Temp_Mean'],
            mode='lines+markers',
            name='Annual Temperature',
            line=dict(color='#e74c3c', width=2),
            marker=dict(size=6)
        ))
        
        fig1.update_layout(
            title='Temperature Warming Trend Over 35 Years',
            xaxis_title='Year',
            yaxis_title='Temperature (°C)',
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # Calcul du changement de température
        temp_change = yearly_temp['Temp_Mean'].iloc[-5:].mean() - yearly_temp['Temp_Mean'].iloc[:5].mean()

    st.markdown("""
    ### **Temperature Trend Analysis (1989-2024):** 
    **The annual average temperature shows a clear upward trend over the past 35 years. This warming pattern 
    indicates a significant change in growing conditions for crops. With an average increase of {:.1f}°C, 
    farmers must now adapt to longer growing seasons but also face increased risks of heat stress during 
    critical growth phases.**
    """.format(temp_change))




    # GRAPHIQUE 2 : Évolution des précipitations annuelles
    if 'Precipitation' in df.columns:
        st.markdown("## Annual Precipitation Evolution")
        
        yearly_precip = df.groupby('Year')['Precipitation'].sum().reset_index()
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Scatter(
            x=yearly_precip['Year'],
            y=yearly_precip['Precipitation'],
            mode='lines+markers',
            name='Annual Precipitation',
            line=dict(color='#3498db', width=2),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.2)'
        ))
        
        
        fig2.update_layout(
            title='Precipitation Pattern Changes',
            xaxis_title='Year',
            yaxis_title='Total Precipitation (mm)',
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
     ### **Precipitation Pattern Analysis:**  ##
    **The annual precipitation data reveals increasing variability in rainfall patterns. While the total 
    annual precipitation hasn't changed dramatically, its distribution throughout the year has become more 
    erratic. This unpredictability poses challenges for agricultural planning and irrigation management, 
    potentially affecting crop yields and farming strategies.**
    """)





    # GRAPHIQUE 3 : Distribution des températures (2 périodes)
    if 'Temp_Mean' in df.columns:
        st.markdown("## Temperature Distribution Comparison (1989-2004 vs 2005-2024)")
        
        df['Period'] = df['Year'].apply(lambda x: '1989-2004' if x <= 2004 else '2005-2024')
        
        fig3 = go.Figure()
        
        for period in ['1989-2004', '2005-2024']:
            period_data = df[df['Period'] == period]['Temp_Mean'].dropna()
            fig3.add_trace(go.Histogram(
                x=period_data,
                name=period,
                opacity=0.7,
                nbinsx=50
            ))
        
        fig3.update_layout(
            title='Temperature Distribution Shift Between Two Periods',
            xaxis_title='Temperature (°C)',
            yaxis_title='Frequency (days)',
            barmode='overlay',
            height=500
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Stats comparatives
        col1, col2 = st.columns(2)
        with col1:
            early_mean = df[df['Period'] == '1989-2004']['Temp_Mean'].mean()
            st.metric("1989-2004 Avg", f"{early_mean:.2f}°C")
        with col2:
            recent_mean = df[df['Period'] == '2005-2024']['Temp_Mean'].mean()
            delta = recent_mean - early_mean
            st.metric("2005-2024 Avg", f"{recent_mean:.2f}°C", f"+{delta:.2f}°C")

    st.markdown("""
    ### **Temperature Distribution Impact:**  
    **Comparing the two periods (1989-2004 vs 2005-2024) shows a clear shift in temperature distribution. 
    The more recent period exhibits both higher average temperatures and more extreme temperature events. 
    This shift affects crop selection decisions and necessitates adjustments in planting and harvesting 
    schedules to optimize agricultural productivity.**
    """)





    # GRAPHIQUE 4 : Heatmap mensuelle des températures
    if 'Temp_Mean' in df.columns:
        st.markdown("## Monthly Temperature Heatmap")
        
        # Créer une pivot table
        monthly_temp = df.pivot_table(
            values='Temp_Mean',
            index='Month',
            columns='Year',
            aggfunc='mean'
        )
        
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        fig4 = go.Figure(data=go.Heatmap(
            z=monthly_temp.values,
            x=monthly_temp.columns,
            y=month_names,
            colorscale='RdYlBu_r',
            colorbar=dict(title='Temp (°C)')
        ))
        
        fig4.update_layout(
            title='Temperature Calendar: Seasonal Patterns Over Years',
            xaxis_title='Year',
            yaxis_title='Month',
            height=500
        )
        
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("""
    ### **Seasonal Temperature Evolution:**  
    **The heatmap reveals intensifying summer temperatures and milder winters over the 35-year period. 
    This seasonal shift has extended the growing season but also increased the risk of early spring frosts 
    damaging crops that start growing too soon. The changing pattern requires farmers to reconsider 
    traditional crop calendars and variety selection.**
    """)






    # GRAPHIQUE 5 : Box plot des précipitations par mois
    if 'Precipitation' in df.columns:
        st.markdown("## Monthly Precipitation Distribution")
        
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        
        fig5 = go.Figure()
        
        for month in month_order:
            month_data = df[df['Month_Name'] == month]['Precipitation'].dropna()
            fig5.add_trace(go.Box(
                y=month_data,
                name=month[:3],
                boxmean='sd'
            ))
        
        fig5.update_layout(
            title='Seasonal Precipitation Variability',
            xaxis_title='Month',
            yaxis_title='Precipitation (mm/day)',
            height=500
        )
        
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("""
     ### **Precipitation Distribution Analysis:**  
    **Monthly precipitation patterns show increasing variability, with more intense rainfall events and 
    longer dry periods. This change in precipitation distribution impacts soil moisture levels and 
    erosion risks, requiring adaptation in soil management practices and potentially investment in 
    irrigation systems to ensure crop resilience.**
    """)






# ========================================
# SECTION 3 : GRAPHIQUES DYNAMIQUES
# ========================================
if page == "3. INTERACTIVE INSIGHTS":
    st.markdown('# 3. INTERACTIVE INSIGHTS: Deep Dive Analysis</p>', unsafe_allow_html=True)

    # GRAPHIQUE 7 : Sélecteur d'année - Profil climatique annuel
    st.markdown("##  Annual Climate Profile ")

    selected_year = st.selectbox(
        "Select a year to explore:",
        options=sorted(df['Year'].unique(), reverse=True),
        index=0
    )

    year_data = df[df['Year'] == selected_year].copy()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if 'Temp_Mean' in df.columns:
            year_avg_temp = year_data['Temp_Mean'].mean()
            all_avg_temp = df['Temp_Mean'].mean()
            delta_temp = year_avg_temp - all_avg_temp
            st.metric(
                f"🌡️ Avg Temp {selected_year}",
                f"{year_avg_temp:.1f}°C",
                f"{delta_temp:+.1f}°C vs avg"
            )

    with col2:
        if 'Precipitation' in df.columns:
            year_precip = year_data['Precipitation'].sum()
            all_avg_precip = df.groupby('Year')['Precipitation'].sum().mean()
            delta_precip = year_precip - all_avg_precip
            st.metric(
                f"💧 Total Precip {selected_year}",
                f"{year_precip:,.0f} mm",
                f"{delta_precip:+.0f} mm vs avg"
            )

    st.markdown("""
     ### **Annual Climate Profile Impact:**  
    **The detailed temperature profile for {selected_year} compared to historical patterns highlights the 
    evolving challenges in agricultural planning. The increased temperature variability and shifting 
    seasonal patterns require more adaptive farming practices and careful monitoring of crop development 
    stages.**
    """)






    # Graphique de l'année sélectionnée
    if 'Temp_Mean' in df.columns:
        fig7 = go.Figure()
        
        fig7.add_trace(go.Scatter(
            x=year_data['Date'],
            y=year_data['Temp_Mean'],
            mode='lines',
            name='Daily Temperature',
            line=dict(color='#e74c3c', width=1),
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.2)'
        ))
        
        # Moyenne mobile sur 30 jours
        year_data['Temp_MA'] = year_data['Temp_Mean'].rolling(window=30, center=True).mean()
        fig7.add_trace(go.Scatter(
            x=year_data['Date'],
            y=year_data['Temp_MA'],
            mode='lines',
            name='30-day Moving Average',
            line=dict(color='#c0392b', width=3)
        ))
        
        fig7.update_layout(
            title=f'Daily Temperature Profile for {selected_year}',
            xaxis_title='Date',
            yaxis_title='Temperature (°C)',
            height=400
        )
        
        st.plotly_chart(fig7, use_container_width=True)







    # GRAPHIQUE 8 : Sélecteur de variable - Comparaison décennale
    st.markdown("## Decadal Comparison ")

    if 'Temp_Mean' in df.columns and 'Precipitation' in df.columns:
        selected_var = st.radio(
            "Select variable to compare:",
            options=['Temperature', 'Precipitation'],
            horizontal=True
        )
        
        # Créer des décennies
        df['Decade'] = (df['Year'] // 10) * 10
        
        # Sélectionner la variable et configurer le graphique en fonction du choix
        if selected_var == 'Temperature':
            plot_var = 'Temp_Mean'
            y_label = 'Temperature (°C)'
            title = 'Monthly Temperature by Decade'
            color_scale = 'RdYlBu_r'
        else:
            plot_var = 'Precipitation'
            y_label = 'Precipitation (mm/day)'
            title = 'Monthly Precipitation by Decade'
            color_scale = 'Blues'
        
        monthly_by_decade = df.groupby(['Decade', 'Month'])[plot_var].mean().reset_index()
        
        fig8 = go.Figure()
        
        decades = sorted(monthly_by_decade['Decade'].unique())
        colors = px.colors.qualitative.Set2
        
        for i, decade in enumerate(decades):
            decade_data = monthly_by_decade[monthly_by_decade['Decade'] == decade]
            fig8.add_trace(go.Scatter(
                x=decade_data['Month'],
                y=decade_data[plot_var].values,
                mode='lines+markers',
                name=f'{decade}s',
                line=dict(width=2.5, color=colors[i % len(colors)]),
                marker=dict(size=7)
            ))
        
        fig8.update_layout(
            title=title,
            xaxis_title='Month',
            yaxis_title=y_label,
            xaxis=dict(tickmode='array', 
                      tickvals=list(range(1, 13)),
                      ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
            height=500,
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        st.plotly_chart(fig8, use_container_width=True)

    st.markdown("""
     ### **Decadal Climate Evolution:**  
    **The decade-by-decade comparison reveals a progressive warming trend and changing precipitation 
    patterns. Each successive decade shows warmer temperatures and more erratic rainfall, indicating 
    a long-term shift in agricultural conditions that requires strategic adaptation in farming practices 
    and crop selection.**
    """)






    # GRAPHIQUE 9 : Sélecteur de saison - Analyse saisonnière
    st.markdown("## Seasonal Analysis ")

    season = st.selectbox(
        "Select a season:",
        options=['Winter', 'Spring', 'Summer', 'Fall']
    )

    season_data = df[df['Season'] == season].copy()

    col1, col2 = st.columns(2)

    with col1:
        if 'Temp_Mean' in df.columns:
            # Évolution de la température saisonnière
            season_yearly = season_data.groupby('Year')['Temp_Mean'].mean().reset_index()
            
            fig9a = go.Figure()
            
            fig9a.add_trace(go.Scatter(
                x=season_yearly['Year'],
                y=season_yearly['Temp_Mean'],
                mode='markers',
                name=f'{season} Temperature',
                marker=dict(size=10, color=season_yearly['Temp_Mean'],
                           colorscale='RdYlBu_r', showscale=True,
                           colorbar=dict(title='°C'))
            ))
            
            
            fig9a.update_layout(
                title=f'{season} Temperature Trend',
                xaxis_title='Year',
                yaxis_title='Average Temperature (°C)',
                height=400
            )
            
            st.plotly_chart(fig9a, use_container_width=True)

    with col2:
        if 'Precipitation' in df.columns:
            # Évolution des précipitations saisonnières
            season_precip = season_data.groupby('Year')['Precipitation'].sum().reset_index()
            
            fig9b = go.Figure()
            
            fig9b.add_trace(go.Bar(
                x=season_precip['Year'],
                y=season_precip['Precipitation'],
                name=f'{season} Precipitation',
                marker_color='#3498db'
            ))
            
            # Moyenne
            avg_precip = season_precip['Precipitation'].mean()
            fig9b.add_hline(
                y=avg_precip,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Average: {avg_precip:.0f} mm"
            )
            
            fig9b.update_layout(
                title=f'{season} Precipitation Pattern',
                xaxis_title='Year',
                yaxis_title='Total Precipitation (mm)',
                height=400
            )
            
            st.plotly_chart(fig9b, use_container_width=True)

    st.markdown("""
    ### **Seasonal Pattern Changes:**  
    **The detailed seasonal analysis shows that {season} has experienced significant changes over the 
    35-year period. These seasonal shifts affect crucial agricultural phases such as planting times, 
    growing periods, and harvest windows. Farmers must now adapt their agricultural calendar and 
    techniques to these new seasonal patterns to maintain productivity.**
    """)

if page == "4. CONCLUSION"   :
    st.markdown('# 4. Conclusion</p>', unsafe_allow_html=True)

    st.markdown("""
    ## Implications & Agricultural Adaptation Strategies

    **The analysis reveals critical implications for agricultural sustainability. For farmers, immediate 
    adaptations are essential: they must carefully select crops better suited to warmer conditions, 
    implement robust irrigation systems to counter irregular rainfall patterns, and modify traditional 
    planting and harvesting schedules to align with shifting seasonal patterns.** 

    **On the agricultural planning front, research and development efforts should focus on developing 
    heat-resistant crop varieties that can withstand temperature extremes, while establishing 
    sophisticated early warning systems for extreme weather events. Additionally, implementing effective 
    soil conservation practices becomes crucial to maintain soil health under changing climatic conditions.**

    **Moving forward, three key actions are vital: maintaining vigilant monitoring of climate trends to 
    anticipate further changes, conducting field trials of adaptive farming techniques to validate their 
    effectiveness, and fostering knowledge-sharing networks within farming communities to spread successful 
    adaptation strategies. These steps will be crucial for ensuring agricultural resilience in the face of 
    ongoing climate change.**

    """)
