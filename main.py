import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_elements import elements, mui, nivo
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
import warnings
warnings.filterwarnings('ignore')

@st.cache_data
def load_data():
    return pd.read_csv('data/gravitas_country_index.csv'), pd.read_csv('data/gravitas_country_index2.csv')

df, df2 = load_data()

st.logo("data/l-gravitas-2.jpg", size = 'large')
# Injection CSS complète
st.markdown("""
    <style>
    /* Redimensionner le logo */
    [data-testid="stHeader"] img {
        height: 110px !important;
        width: auto !important;
        margin: auto;
        display: block;
    }

    /* Forcer la hauteur de len-tête pour contenir le logo */
    [data-testid="stHeader"] {
        min-height: 100px !important;
        height: auto !important;
        padding: 1px 0 !important;
        overflow: hidden !important;
    }
    </style>
""", unsafe_allow_html=True)


st.title('Gulf-Africa Strategic Partnership Index Dashboard')

st.set_page_config(
    page_title = 'Geospatial Dashboard',
    layout = 'wide'
)
with st.sidebar:
  st.title('Geospatial Dashboard')

    # Liste des régions disponibles
  region_lst = sorted(df["Region"].dropna().unique())
  select_region = st.multiselect("Select a Region", region_lst)

    # Filtrage conditionnel des pays affichés
  if select_region:
    # Pays disponibles dans les régions sélectionnées
    countries_in_region = sorted(df[df["Region"].isin(select_region)]["Country"].unique())
    default_countries = countries_in_region
  else:
    countries_in_region = sorted(df["Country"].dropna().unique())
    default_countries=[]

    # Sélection finale de pays avec possibilité de choisir en dehors des régions
  select_country = st.multiselect(
      "Select Country",
      options=sorted(df["Country"].dropna().unique()),  # tous les pays
      default=default_countries                      # pré-rempli si une région est sélectionnée
    )

    # Application du filtre final
  if select_country:
      filtered_df = df[df["Country"].isin(select_country)]
  else:
      filtered_df = df.copy()


theme_mode = "dark"  # ou "light"
tick_color = "black" if theme_mode == "dark" else "white"
tick_color2 = "white" if theme_mode == "dark" else "black"

## Le Globe
# --- Mise en page : deux colonnes pour les deux blocs ---
col1, col2 = st.columns([1, 1])

# === BLOC 1 : SUNBURST CHART ===
with col1:
    st.subheader("Sunburst Chart - GASPI Partners (1st Edition)")
    st.text("Click on the chart to deploy and discover the countries that willl be colaborating on the first edition of the GASPI intiative.")

    # Préparation du DataFrame hiérarchique
    sunburst_data = pd.DataFrame(columns=['labels', 'parents', 'values'])

    # Niveau 1 : Continents (racine)
    continents = df2.groupby('Continent')['Value'].sum().reset_index()
    sunburst_data = pd.concat([
        sunburst_data,
        pd.DataFrame({
            'labels': continents['Continent'],
            'parents': [''] * len(continents),  # racine
            'values': continents['Value']
        })
    ])

    # Niveau 2 : Régions
    regions = df2.groupby(['Continent', 'Region'])['Value'].sum().reset_index()
    sunburst_data = pd.concat([
        sunburst_data,
        pd.DataFrame({
            'labels': regions['Region'],
            'parents': regions['Continent'],
            'values': regions['Value']
        })
    ])

    # Niveau 3 : Pays
    countries = df2[['Region', 'Country', 'Value']]
    sunburst_data = pd.concat([
        sunburst_data,
        pd.DataFrame({
            'labels': countries['Country'],
            'parents': countries['Region'],
            'values': countries['Value']
        })
    ])

    # Création du Sunburst
    
    fig_sunburst = go.Figure(go.Sunburst(
        labels=sunburst_data['labels'],
        parents=sunburst_data['parents'],
        values=sunburst_data['values'],
        branchvalues="total",
        hoverinfo='skip',
        maxdepth=2  # facultatif, ne montre que les continents au début
    ))

    fig_sunburst.update_layout(
        margin=dict(t=60, l=0, r=0, b=0),
        font_color='white', font_size=16,
        height=600
    )
    st.plotly_chart(fig_sunburst, use_container_width=True)

# === BLOC 2 : GLOBE ORTHOGRAPHIQUE CHOROPLETH ===
with col2:
    st.subheader("World Map - African countries classified by GASPI Composite Index")
    st.text("Map-based visualization of country rankings according to the GASPI Classification.")

    # 🗺️ Construction du choropleth avec GO + projection globe
    fig = go.Figure(data=go.Choropleth(
        locations=filtered_df['Country'],               # noms de pays
        locationmode='country names',
        z=filtered_df['Composite index'],               # variable à colorier
        colorscale='Blues',
        colorbar_title='Composite Index',
        
        customdata=filtered_df[['Country', 'Composite index', 'Ranking']],
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>" +
            "Composite Index: %{customdata[1]:.2f}<br>" +
            "Ranking: %{customdata[2]}<br><extra></extra>"
        )
    ))

    # Paramètres de projection et style globe
    fig.update_geos(
        projection_type="orthographic",
        showland=True, landcolor='gray',
        showocean=True, oceancolor='black',
        showlakes=True, lakecolor='black', coastlinecolor='white',
        bgcolor= "rgba(0,0,0,0)",  # fond noir pour le globe
        # Empêche le globe de bouger au drag
        fitbounds="locations",   # ajuste à l'ensemble des pays affichés
        lataxis_showgrid=False,
        lonaxis_showgrid=False,
        )

    # Mise en page
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="black",   # fond
            font_size=16,
            font_family="Arial",
            font_color="white",
            bordercolor="white"
            ),
            coloraxis_colorbar=dict(
            tickfont=dict(color=tick_color2),
            ),
            height=600,
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
    )
    # Affichage dans Streamlit
    st.plotly_chart(fig, use_container_width=True)

##################################################

# Graphe interactif
with st.container():
    st.set_page_config(layout="wide")
        # Affichage
    st.title("")
    st.subheader("Macro Linkage Map of Composite Index")
    st.text("Navigate inside the graph to explore the relationships between the composite index, its pillars, and indicators. Hover over nodes and edges for more information.")

    # Définition des éléments
    graph_data = {
        "nodes": [
            {"data": {"id": "Composite", "label": "INDEX", "name": "Composite Index",
                      "description":"The overall macroeconomic composite index used to rank investment attractiveness. It combines 13 key indicators across three main pillars: economic importance (i), political and diplomatic relations (ii), and social and strategic significance (iii) "}},

            {"data": {"id": "Economic", "label": "PILLAR", "name": "Economic Importance (40%)",
                      "description":"The first pillar, economic importance, consists of five indicators that reflect the strength of economic engagement between Africa and the Gulf. These include the volume of bilateral trade with GCC countries, the stock of Gulf foreign direct investment, partnerships in energy and infrastructure, Gulf investments in African agriculture, African countries renewables energy capacity and Logistic Performance Index. These indicators highlight the economic interdependence between the regions and the role of African countries in supplying key commodities and investment opportunities to Gulf states."}},
            {"data": {"id": "Political", "label": "PILLAR", "name": "Political & Diplomatic Relations (35%)",
                      "description":"The second pillar, political and diplomatic relations, evaluates the strength of diplomatic engagement and governance quality. It includes three indicators: the level of diplomatic ties between GCC and African countries, the political stability score of each African country, and government effectiveness as measured by governance indices. These indicators provide insight into the reliability of African partners for long-term cooperation, as well as their institutional capacity to facilitate trade and investment."}},
            {"data": {"id": "Social", "label": "PILLAR", "name": "Social & Strategic Significance (25%)",
                      "description":"The third pillar, social and strategic significance, captures demographic and agricultural potential. It comprises three indicators: total population size, the urbanization rate as a proxy for market potential, and the food security and agricultural capacity of each African country. These factors are crucial for understanding Africa's role in meeting Gulf countries' long-term food security needs and their potential as key consumer markets."}},

            # Economic Indicators
            {"data": {"id": "Imports", "label": "INDICATOR", "name": "GCC Imports of Goods and Services from African Countries",
                      "description":"This measure captures the average imports of goods and services from African countries to the GCC region over the period 2020-2024."}},
            {"data": {"id": "Exports", "label": "INDICATOR", "name": "GCC Exports of Goods and Services from African Countries",
                      "description":"This indicator reports the average exports of goods and services from the GCC region to African countries between 2020-2024."}},
            {"data": {"id": "FDI", "label": "INDICATOR", "name": "GCC Greenfield Foreign Direct Investment (FDI) to African Countries",
                      "description":"This metric assesses the total stock of Greenfield FDI from GCC countries to African nations between 2020-2024, based on data from the fDi Markets database. Greenfield FDI represents new investments that involve the establishment of new operations, such as factories or subsidiaries."}},
            {"data": {"id": "GDP", "label": "INDICATOR", "name": "African Countries' GDP (PPP, Const $)",
                      "description":"This indicator measures the economic size or market potential of African countries, using GDP data converted to Purchasing Power Parity (PPP) and constant dollars. The data, sourced from the World Development Indicators (WDI), helps assess the relative economic strength and potential of African markets for GCC countries."}},
            {"data": {"id": "PCI", "label": "INDICATOR", "name": "African Countries' GDP Per Capita",
                      "description":"This metric, also sourced from the World Development Indicators (WDI), measures the GDP per capita of African countries. It provides insight into the purchasing power of citizens in each country, indicating the economic well-being and market potential at the individual level."}},
            {"data": {"id": "Renewables", "label": "INDICATOR", "name": "Renewable Energy Share",
                      "description":"Renewable power capacity growth refers to the expansion of energy generation from renewable sources over time. This includes hydropower (excluding pumped storage), solar energy, wind energy, bioenergy, geothermal energy, and marine energy. Data on the growth of renewable power capacity is sourced from the International Renewable Energy Agency (IRENA)"}},
            {"data": {"id": "LPI", "label": "INDICATOR", "name": "Logistic Performance Index",
                      "description":"The World Bank's Logistics Performance Index (LPI) is a tool that measures the relative ease and efficiency with which products can be moved into and within a country. The LPI is developed based on a worldwide survey of global freight forwarders and express carriers, combining their feedback with quantitative data on the performance of key logistics components. It evaluates countries across six key dimensions: the efficiency of customs clearance, the quality of trade and transport-related infrastructure, the ease of arranging competitively priced international shipments, the quality of logistics services, the ability to track and trace consignments, and the timeliness of shipments. LPI scores range from 1 to 5, with higher scores indicating better performance."}},

            # Political Indicators
            {"data": {"id": "Diplomacy", "label": "INDICATOR", "name": "Diplomatic Ties with GCC", 
                      "description":"For this we use a diplomatic representation database. The latest database is available until 2022. The Level of Representation Index (LoRI) is a scale ranging from 0 to 1, designed to measure the formal level of diplomatic accreditation along with the degree of focus on the bilateral relationship. A country receives the highest score of 1.00 if it is represented by an Ambassador, Nuncio, or Secretary of the People's Bureau with a singular focus on the relationship. A slightly lower score of 0.75 is assigned if the representation is through a Charge d'affaires, minister, or an unknown status, but still with a singular focus. When an Ambassador, Nuncio, or Secretary of the People's Bureau is accredited with multiple areas of focus, the score is 0.50, while the presence of a Charge d'affaires, minister, or an unknown status with multiple focuses results in a score of 0.375. Countries with only an interest desk receive a score of 0.125, whereas those whose interests are merely served by another entity are assigned 0.10. Finally, the lowest score of 0.00 is given when diplomatic relations have been expelled, recalled, or withdrawn. As there are six GCC countries, we need to sum up, and in this case the maximum any African country gets is 6. For example, if all of the GCC sates have ambassador to Nigeria, it means the level of representation index is 6. If three countries from the GCC have ambassadors to Gambia and two GCC countries have Charge d'affaires and one GCC country has only an interest desk, the score for the Gambia would be 1+1+1+0.75+0.75+0.125=4.625"}},
            {"data": {"id": "Stability", "label": "INDICATOR", "name": "Political Stability", 
                      "description":"The Political Stability and Absence of Violence/Terrorism indicator, provided by the World Bank's Worldwide Governance Indicators (WGI), assesses government performance in maintaining stability and preventing politically motivated violence, including terrorism. It reflects perceptions of the likelihood of political instability and unrest, drawing from multiple measures such as orderly transfers of power, violent demonstrations, social unrest, political terror scale, external and internal conflicts, and ethnic tensions. Countries are ranked on a percentile scale from 0 to 100, with higher values indicating greater political stability. The most recent data is from 2023."}},
            {"data": {"id": "Governance", "label": "INDICATOR", "name": "Government Effectiveness",
                      "description":"The Government Effectiveness indicator, sourced from the World Bank's Worldwide Governance Indicators (WGI), measures perceptions of the quality of public services, the competence and independence of the civil service from political influence, the effectiveness of policy formulation and implementation, and the government's commitment to its policies. This index is composed of various factors, including bureaucratic quality, road infrastructure, primary education quality, public satisfaction with transportation, and overall governance efficiency. Countries are ranked on a percentile scale from 0 to 100, with higher scores indicating more effective governance. The most recent data is from 2023"}},

            # Social Indicators
            {"data": {"id": "Population", "label": "INDICATOR", "name": "Population Size",
                      "description":"Population size is a key demographic indicator, reflecting the overall market potential of a country. A larger population often signifies a bigger consumer base, greater labour force availability, and increased economic activity. Countries with sizable populations tend to attract more trade and investment opportunities, making this an essential factor in economic and diplomatic considerations."}},
            {"data": {"id": "Urban", "label": "INDICATOR", "name": "Urbanization Rate/population",
                      "description":"The urbanization rate, measured as the percentage of a country's population living in urban areas, serves as a crucial proxy for economic development, infrastructure needs, and technological readiness. Higher urbanization levels often correlate with improved infrastructure, greater digital connectivity, and stronger prospects for collaboration in sectors such as the digital economy, smart cities, and advanced transportation systems. This indicator provides insights into a country's modernization efforts and its capacity for future economic growth."}},
            {"data": {"id": "Food", "label": "INDICATOR", "name": "Food Security & Agriculture",
                      "description":"Food security and agricultural potential are strategic priorities, particularly for regions reliant on food imports, such as the Gulf Cooperation Council (GCC) countries. To assess this, we consider key indicators like arable land availability and irrigation potential estimates, which determine a country's ability to sustain agricultural production. Given the importance of agriculture for food security, trade, and investment, this metric helps identify nations with strong potential for collaboration in agri-business, food supply chains, and sustainable farming practices."}},
        ],
        "edges": [
            # Composite to Pillars
            {"data": {"id": "e1", "label": "INCLUDES", "source": "Composite", "target": "Economic"}},
            {"data": {"id": "e2", "label": "INCLUDES", "source": "Composite", "target": "Political"}},
            {"data": {"id": "e3", "label": "INCLUDES", "source": "Composite", "target": "Social"}},

            # Economic Indicators
            {"data": {"id": "e4", "label": "MEASURED_BY", "source": "Economic", "target": "Imports"}},
            {"data": {"id": "e5", "label": "MEASURED_BY", "source": "Economic", "target": "Exports"}},
            {"data": {"id": "e6", "label": "MEASURED_BY", "source": "Economic", "target": "FDI"}},
            {"data": {"id": "e7", "label": "MEASURED_BY", "source": "Economic", "target": "GDP"}},
            {"data": {"id": "e8", "label": "MEASURED_BY", "source": "Economic", "target": "PCI"}},
            {"data": {"id": "e9", "label": "MEASURED_BY", "source": "Economic", "target": "Renewables"}},
            {"data": {"id": "e10", "label": "MEASURED_BY", "source": "Economic", "target": "LPI"}},

            # Political Indicators
            {"data": {"id": "e11", "label": "MEASURED_BY", "source": "Political", "target": "Diplomacy"}},
            {"data": {"id": "e12", "label": "MEASURED_BY", "source": "Political", "target": "Stability"}},
            {"data": {"id": "e13", "label": "MEASURED_BY", "source": "Political", "target": "Governance"}},

            # Social Indicators
            {"data": {"id": "e14", "label": "MEASURED_BY", "source": "Social", "target": "Population"}},
            {"data": {"id": "e15", "label": "MEASURED_BY", "source": "Social", "target": "Urban"}},
            {"data": {"id": "e16", "label": "MEASURED_BY", "source": "Social", "target": "Food"}},
        ]
    }

    # Styles
    node_styles = [
        NodeStyle("INDEX", "#00CED1", "name", "Index"),
        NodeStyle("PILLAR", "#FF7F3E", "name", "Pillar"),
        NodeStyle("INDICATOR", "#2A629A", "name", "Indicator"),
    ]

    edge_styles = [
        EdgeStyle("INCLUDES", caption="label", directed=True),
        EdgeStyle("MEASURED_BY", caption="label", directed=True),
    ]

    legend = {
        "INDEX": "#00CED1",
        "PILLAR": "#FF7F3E",        
        "INDICATOR": "#2A629A"
    }

    for label, color in legend.items():
        st.markdown(
            f"""
            <div style='display: flex; align-items: center; margin-bottom: 5px;'>
                <div style='width: 15px; height: 15px; background-color: {color}; border-radius: 3px; margin-right: 10px;'></div>
                <span style='font-weight: bold;'>{label}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 4. Graphe interactif
    st_link_analysis(
        graph_data, layout="cola", node_styles=node_styles,
        edge_styles=edge_styles,height=600
        )

#################################################

#Boxplot
radar_variables = [
    "GDP", "Per Capita Income (PCI)", "Import", "Export",
    "Foreign Direct Investments (FDI)", "Renewables", "Logistic Performance Index (LPI)",
    "Diplomatic Level Of Representation(LOR)", "Government Efficacity", "Political stability",
    "Population", "Urban Population", "Arable Land"
        ]

# Transformation au format long pour faciliter les boxplots
df_long = filtered_df.melt(
    id_vars=["Country"],
    value_vars=radar_variables,
    var_name="Indicator",
    value_name="Value"
)

# Calcul des statistiques descriptives par indicateur
stats_df = df_long.groupby("Indicator")["Value"].describe().reset_index()

# Ajout de la moyenne (mean) à la main si besoin
stats_df["mean"] = df_long.groupby("Indicator")["Value"].mean().values

# Fusion des statistiques avec les données longues
df_long = df_long.merge(stats_df, on="Indicator", suffixes=("", "_stat"))

# Calcul de la moyenne pour chaque indicateur
means = df_long.groupby("Indicator")["Value"].mean().round(2).reset_index().rename(columns={"Value": "Mean"})

# Fusion avec le DataFrame long
df_long = df_long.merge(means, on="Indicator", how="left")

# Création du tooltip avec uniquement la moyenne
df_long["Indicators"] = (
    "<br><b>Country:</b> " + df_long["Country"] +
    "<br><b>Value:</b> " + df_long["Value"].round(2).astype(str) +
    "<br><b>Mean:</b> " + df_long["Mean"].astype(str)
)

# Création du boxplot
fig = px.box(
    df_long,
    x="Indicator",
    y="Value",
    points="all",
    hover_data={"Indicators": False, "Country": False, "Indicator": False, "Value": False},
    custom_data="Indicators",
    template="plotly_white"
)

# Personnalisation
fig.update_traces(
    hovertemplate="%{customdata[0]}<extra></extra>",
    marker=dict(size=6, opacity=0.6),
    selector=dict(type='box')
)

fig.update_layout(
    xaxis_tickangle=-45,
    yaxis_title="Value",
    hoverlabel=dict(
        bgcolor="black",
        font_size=13,
        font_family="Arial",
        bordercolor="white",
        font_color="white"
    ),
    height=750,
    margin=dict(l=40, r=40, t=60, b=120)
)

# Affichage dans Streamlit
st.title("")
st.subheader("Composite Index Components Distribution")
st.text("Hover over the boxplots to see descriptive statistics of each indicator accross GASPI selected African countries.")
st.plotly_chart(fig, use_container_width=True)       

st.divider()

#####################

# Radar, Metric Cards and Pie Charts

if not select_country:
    st.subheader("Select from the sidebar to view country-specific charts visualizations.")
else:
    # Metric Cards pour chaque pays sélectionné
    st.subheader("Country Metric Cards")
    # Affichage des cartes côte à côte
    columns = st.columns(len(select_country))  # Crée une colonne par pays

    #css for metric card
    st.markdown("""
        <style>
        .card {
            border-radius: 12px;
            background-color: #1e1e1e;
            padding: 30px;
            margin: 20px auto;
            color: white;
            font-size: 24px;
            text-align: center;
            width: 250px;
            box-shadow: 0px 0px 12px rgba(255,255,255,0.1);
        }
        .value {
            font-size: 48px;
            font-weight: bold;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    #define card creation function
    def create_metric_card(country_name, index_value, ranking):
        st.markdown(f"""
        <div class="card">
            <div>{country_name}</div>
            <div class="value">{index_value:.2f}</div>
            <div style='margin-top:10px; font-size:20px;'>Ranking: #{ranking}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Affichage par lignes de 5 cartes maximum
    for i in range(0, len(select_country), 6):
        row = select_country[i:i+6]  # prend 6 pays à la fois
        cols = st.columns(len(row))  # crée le bon nombre de colonnes

        for j, country in enumerate(row):
            country_data = df[df['Country'] == country].iloc[0]
            with cols[j]:
                create_metric_card(
                    country_name=country,
                    index_value=country_data['Composite index'],
                    ranking=int(country_data['Ranking'])
            )

    st.divider()

#######Radar Chart 

    ### Construire les données
    with st.container():
        st.subheader("Country Radar Chart")
        st.text("Evaluate country performance through comparative indicator analysis.")        
        # Construire les données pour le radar chart
        selected_countries = select_country
        radar_data = []
        for var in radar_variables:
            row = {"indicator": var}
            for country in selected_countries:
                value = df[df["Country"] == country][var].values
                row[country] = round(float(value[0]), 2) if len(value) > 0 else 0
            radar_data.append(row)
        ## Liste du fixe du radar

        with elements("nivo_charts"):

                    # Streamlit Elements includes 45 dataviz components powered by Nivo

                with mui.Box(sx={"height": 700}):
                        nivo.Radar(
                            data=radar_data,
                            keys=selected_countries,
                            indexBy="indicator",
                            valueFormat=">-.2f",
                            margin={ "top": 100, "right": 80, "bottom": 40, "left": 80 },
                            borderColor={ "from": "color" },
                            gridLabelOffset=36,
                            dotSize=10,
                            dotColor={ "theme": "background" },
                            dotBorderWidth=2,
                            motionConfig="wobbly",
                            legends=[
                                {
                                    "anchor": "top-left",
                                    "direction": "column",
                                    "translateX": -50,
                                    "translateY": -40,
                                    "itemWidth": 80,
                                    "itemHeight": 20,
                                    "itemTextColor": "#999",
                                    "symbolSize": 12,
                                    "symbolShape": "circle",
                                    "effects": [
                                        {
                                            "on": "hover",
                                            "style": {
                                                "itemTextColor": "#000"
                                            }
                                        }
                                    ]
                                }
                            ],
                            theme={
                                "textColor": "#999",
                                "fontSize": 14,
                                "tooltip": {
                                    "container": {
                                        "color": "#999"
                                    }
                                }
                            }
                        )
            
        st.divider()

        ###Pie chart
        st.subheader("Country Composite Index Insights - Pie Charts")

        # ✅ Si aucun pays sélectionné : rien ne s'affiche
        for i in range(0, len(select_country), 2):
                cols = st.columns(2)  # deux colonnes côte à côte

                for j in range(2):
                    if i + j < len(select_country):
                        country = select_country[i + j]
                        row = df[df["Country"] == country]

                        if row.empty:
                            continue  # sécurité

                        row = row.iloc[0]

                        # Préparer les données radar sous forme de camembert
                        pie_data = [
                            {
                                "id": var,
                                "label": var,
                                "value": round(row[var], 3)
                            }
                            for var in radar_variables
                        ]

                        with cols[j]:
                            st.markdown(f"### {country}")
                            with elements(f"nivo_pie_chart_{country}"):
                                with mui.Box(sx={"height": 400}):
                                    nivo.Pie(
                                        data=pie_data,
                                        margin={ "top": 40, "right": 80, "bottom": 80, "left": 80 },
                                        innerRadius=0.4,
                                        padAngle=0.5,
                                        cornerRadius=3,
                                        activeOuterRadiusOffset=8,
                                        borderWidth=1,
                                        borderColor={ "from": "color", "modifiers": [["darker", 0.2]] },
                                        arcLinkLabelsSkipAngle=5,
                                        arcLinkLabelsTextColor="#999",
                                        arcLinkLabelsThickness=2,
                                        arcLinkLabelsColor={ "from": "color" },
                                        arcLabelsSkipAngle=5,
                                        arcLabelsTextColor={ "from": "color", "modifiers": [["darker", 2]] },
                                        theme={ "fontSize": 13,
                                            "tooltip": {
                                                "container": {
                                                    "background": "#ffffff",
                                                    "color": "#31333F",
                                                }
                                            }
                                        }
                                    )