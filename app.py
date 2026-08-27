import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from database import (
    initialize_database,
    seed_data,
    get_assessments,
    add_assessment,
)


st.set_page_config(
    page_title="WASH Service Monitoring Dashboard",
    page_icon="🚰",
    layout="wide",
)


initialize_database()
seed_data()


COLUMNS = [
    "ID",
    "Assessment Date",
    "District",
    "Upazila",
    "Households",
    "Population",
    "Safe Water Access (%)",
    "Water Source",
    "Water Distance (km)",
    "Daily Water Availability (L/person)",
    "Functional Water Points",
    "Sanitation Coverage (%)",
    "Functional Toilets",
    "Shared Toilets",
    "Open Defecation (%)",
    "Handwashing Facilities (%)",
    "Soap Availability (%)",
    "Hygiene Awareness (%)",
    "Menstrual Hygiene Support (%)",
    "Water Quality Status",
    "Water Shortage",
    "Hygiene Material Access",
    "Vulnerability Score",
    "Vulnerability Level",
    "Service Coverage Score",
    "Coverage Level",
]


def load_data():
    return pd.DataFrame(
        get_assessments(),
        columns=COLUMNS,
    )


df = load_data()


def calculate_scores(
    safe_water_access,
    water_distance,
    daily_water_availability,
    sanitation_coverage,
    open_defecation,
    handwashing_facilities,
    soap_availability,
    hygiene_awareness,
    menstrual_hygiene_support,
    water_quality_status,
    water_shortage,
    hygiene_material_access,
):

    vulnerability = 0

    if safe_water_access < 60:
        vulnerability += 18
    elif safe_water_access < 75:
        vulnerability += 10
    else:
        vulnerability += 4

    if water_distance >= 1.2:
        vulnerability += 12
    elif water_distance >= 0.7:
        vulnerability += 7

    if daily_water_availability < 15:
        vulnerability += 12
    elif daily_water_availability < 25:
        vulnerability += 6

    if sanitation_coverage < 70:
        vulnerability += 15
    elif sanitation_coverage < 85:
        vulnerability += 8

    if open_defecation >= 15:
        vulnerability += 12
    elif open_defecation >= 8:
        vulnerability += 6

    if handwashing_facilities < 60:
        vulnerability += 8
    elif handwashing_facilities < 75:
        vulnerability += 4

    if soap_availability < 55:
        vulnerability += 7
    elif soap_availability < 70:
        vulnerability += 4

    if hygiene_awareness < 55:
        vulnerability += 6
    elif hygiene_awareness < 70:
        vulnerability += 3

    if menstrual_hygiene_support < 50:
        vulnerability += 6
    elif menstrual_hygiene_support < 65:
        vulnerability += 3

    if water_quality_status == "Unsafe":
        vulnerability += 10
    elif water_quality_status == "At Risk":
        vulnerability += 5

    if water_shortage == "Yes":
        vulnerability += 8

    if hygiene_material_access == "Limited":
        vulnerability += 6
    elif hygiene_material_access == "Moderate":
        vulnerability += 3

    vulnerability = min(vulnerability, 100)

    coverage_components = [
        safe_water_access,
        sanitation_coverage,
        handwashing_facilities,
        soap_availability,
        hygiene_awareness,
        menstrual_hygiene_support,
    ]

    coverage = sum(coverage_components) / len(
        coverage_components
    )

    if water_quality_status == "Unsafe":
        coverage -= 10
    elif water_quality_status == "At Risk":
        coverage -= 5

    if water_shortage == "Yes":
        coverage -= 5

    coverage = max(
        0,
        min(100, coverage),
    )

    return vulnerability, round(coverage)


def vulnerability_level(score):

    if score >= 80:
        return "Critical"

    if score >= 60:
        return "High"

    if score >= 40:
        return "Medium"

    return "Low"


def coverage_level(score):

    if score >= 75:
        return "High"

    if score >= 50:
        return "Medium"

    return "Low"


st.title(
    "🚰 WASH Service Monitoring Dashboard"
)

st.caption(
    "Water, sanitation, hygiene access, service coverage "
    "and WASH vulnerability monitoring."
)


st.sidebar.title("🌍 Navigation")

page = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "Water Access Assessment",
        "Sanitation Monitoring",
        "Hygiene Assessment",
        "WASH Vulnerability",
        "Service Coverage",
        "Reports",
    ],
)


if page == "Dashboard":

    st.subheader("📊 WASH Overview")

    total_households = int(
        df["Households"].sum()
    )

    total_population = int(
        df["Population"].sum()
    )

    avg_water = df[
        "Safe Water Access (%)"
    ].mean()

    critical = int(
        (
            df["Vulnerability Level"]
            == "Critical"
        ).sum()
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Households Assessed",
        f"{total_households:,}",
    )

    c2.metric(
        "Population Covered",
        f"{total_population:,}",
    )

    c3.metric(
        "Average Safe Water Access",
        f"{avg_water:.1f}%",
    )

    c4.metric(
        "Critical Locations",
        critical,
    )

    st.divider()

    left, right = st.columns(2)

    with left:

        vulnerability = (
            df["Vulnerability Level"]
            .value_counts()
            .reset_index()
        )

        vulnerability.columns = [
            "Vulnerability Level",
            "Locations",
        ]

        fig = px.pie(
            vulnerability,
            names="Vulnerability Level",
            values="Locations",
            title="WASH Vulnerability Distribution",
            hole=0.4,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with right:

        district_water = (
            df.groupby("District")[
                "Safe Water Access (%)"
            ]
            .mean()
            .reset_index()
        )

        district_water[
            "Safe Water Access (%)"
        ] = district_water[
            "Safe Water Access (%)"
        ].round(1)

        fig = px.bar(
            district_water,
            x="District",
            y="Safe Water Access (%)",
            title="Safe Water Access by District",
            text_auto=True,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    st.subheader(
        "🚨 Priority WASH Locations"
    )

    priority = df[
        df["Vulnerability Level"].isin(
            ["Critical", "High"]
        )
    ]

    st.dataframe(
        priority[
            [
                "District",
                "Upazila",
                "Safe Water Access (%)",
                "Sanitation Coverage (%)",
                "Open Defecation (%)",
                "Water Quality Status",
                "Vulnerability Score",
                "Vulnerability Level",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


elif page == "Water Access Assessment":

    st.subheader(
        "🚰 Water Access Assessment"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Average Water Access",
        f"{df['Safe Water Access (%)'].mean():.1f}%",
    )

    c2.metric(
        "Average Distance",
        f"{df['Water Distance (km)'].mean():.1f} km",
    )

    c3.metric(
        "Water Shortage Locations",
        int(
            (
                df["Water Shortage"]
                == "Yes"
            ).sum()
        ),
    )

    c4.metric(
        "Unsafe Water Locations",
        int(
            (
                df["Water Quality Status"]
                == "Unsafe"
            ).sum()
        ),
    )

    st.divider()

    source = (
        df["Water Source"]
        .value_counts()
        .reset_index()
    )

    source.columns = [
        "Water Source",
        "Locations",
    ]

    fig = px.bar(
        source,
        x="Water Source",
        y="Locations",
        title="Water Source Distribution",
        text_auto=True,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.subheader(
        "Water Access by District"
    )

    water = (
        df.groupby("District")
        .agg(
            Safe_Water=(
                "Safe Water Access (%)",
                "mean",
            ),
            Daily_Availability=(
                "Daily Water Availability (L/person)",
                "mean",
            ),
        )
        .reset_index()
    )

    water[
        "Safe_Water"
    ] = water[
        "Safe_Water"
    ].round(1)

    water[
        "Daily_Availability"
    ] = water[
        "Daily_Availability"
    ].round(1)

    fig = px.bar(
        water,
        x="District",
        y="Safe_Water",
        title="Average Safe Water Access",
        text_auto=True,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.subheader(
        "➕ Add Water Assessment"
    )

    with st.form("water_form"):

        c1, c2, c3, c4 = st.columns(4)

        assessment_date = c1.date_input(
            "Assessment Date",
            value=date.today(),
        )

        district = c2.selectbox(
            "District",
            [
                "Barishal",
                "Bhola",
                "Patuakhali",
                "Barguna",
                "Jhalokathi",
                "Pirojpur",
            ],
        )

        upazila = c3.text_input(
            "Upazila"
        )

        households = c4.number_input(
            "Households",
            min_value=1,
            value=100,
        )

        c5, c6, c7, c8 = st.columns(4)

        population = c5.number_input(
            "Population",
            min_value=1,
            value=500,
        )

        safe_water_access = c6.slider(
            "Safe Water Access (%)",
            0,
            100,
            70,
        )

        water_source = c7.selectbox(
            "Water Source",
            [
                "Tube Well",
                "Piped Water",
                "Rainwater",
                "Surface Water",
                "Protected Spring",
            ],
        )

        water_distance = c8.number_input(
            "Distance to Water (km)",
            min_value=0.0,
            value=0.7,
            step=0.1,
        )

        c9, c10, c11, c12 = st.columns(4)

        daily_water = c9.number_input(
            "Daily Water Availability (L/person)",
            min_value=0.0,
            value=20.0,
            step=1.0,
        )

        functional_points = c10.number_input(
            "Functional Water Points",
            min_value=0,
            value=8,
        )

        sanitation = c11.slider(
            "Sanitation Coverage (%)",
            0,
            100,
            75,
        )

        functional_toilets = c12.number_input(
            "Functional Toilets",
            min_value=0,
            value=100,
        )

        c13, c14, c15, c16 = st.columns(4)

        shared_toilets = c13.number_input(
            "Shared Toilets",
            min_value=0,
            value=20,
        )

        open_defecation = c14.slider(
            "Open Defecation (%)",
            0,
            100,
            8,
        )

        handwashing = c15.slider(
            "Handwashing Facilities (%)",
            0,
            100,
            70,
        )

        soap = c16.slider(
            "Soap Availability (%)",
            0,
            100,
            65,
        )

        c17, c18, c19, c20 = st.columns(4)

        hygiene_awareness = c17.slider(
            "Hygiene Awareness (%)",
            0,
            100,
            70,
        )

        menstrual_support = c18.slider(
            "Menstrual Hygiene Support (%)",
            0,
            100,
            60,
        )

        water_quality = c19.selectbox(
            "Water Quality",
            [
                "Safe",
                "At Risk",
                "Unsafe",
            ],
        )

        water_shortage = c20.selectbox(
            "Water Shortage?",
            [
                "No",
                "Yes",
            ],
        )

        hygiene_material = st.selectbox(
            "Hygiene Material Access",
            [
                "Good",
                "Moderate",
                "Limited",
            ],
        )

        submitted = st.form_submit_button(
            "Add WASH Assessment"
        )

        if submitted:

            if not upazila.strip():

                st.error(
                    "Please enter the Upazila."
                )

            else:

                vulnerability, coverage = (
                    calculate_scores(
                        safe_water_access,
                        water_distance,
                        daily_water,
                        sanitation,
                        open_defecation,
                        handwashing,
                        soap,
                        hygiene_awareness,
                        menstrual_support,
                        water_quality,
                        water_shortage,
                        hygiene_material,
                    )
                )

                v_level = vulnerability_level(
                    vulnerability
                )

                c_level = coverage_level(
                    coverage
                )

                add_assessment(
                    str(assessment_date),
                    district,
                    upazila.strip(),
                    int(households),
                    int(population),
                    int(safe_water_access),
                    water_source,
                    float(water_distance),
                    float(daily_water),
                    int(functional_points),
                    int(sanitation),
                    int(functional_toilets),
                    int(shared_toilets),
                    int(open_defecation),
                    int(handwashing),
                    int(soap),
                    int(hygiene_awareness),
                    int(menstrual_support),
                    water_quality,
                    water_shortage,
                    hygiene_material,
                    int(vulnerability),
                    v_level,
                    int(coverage),
                    c_level,
                )

                st.success(
                    f"Assessment added. "
                    f"Vulnerability: {vulnerability} ({v_level}) | "
                    f"Coverage: {coverage}% ({c_level})"
                )

                st.rerun()


elif page == "Sanitation Monitoring":

    st.subheader(
        "🚽 Sanitation Monitoring"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Average Sanitation Coverage",
        f"{df['Sanitation Coverage (%)'].mean():.1f}%",
    )

    c2.metric(
        "Average Open Defecation",
        f"{df['Open Defecation (%)'].mean():.1f}%",
    )

    c3.metric(
        "Functional Toilets",
        int(
            df["Functional Toilets"].sum()
        ),
    )

    sanitation = (
        df.groupby("District")[
            [
                "Sanitation Coverage (%)",
                "Open Defecation (%)",
            ]
        ]
        .mean()
        .reset_index()
    )

    sanitation[
        "Sanitation Coverage (%)"
    ] = sanitation[
        "Sanitation Coverage (%)"
    ].round(1)

    sanitation[
        "Open Defecation (%)"
    ] = sanitation[
        "Open Defecation (%)"
    ].round(1)

    sanitation_long = sanitation.melt(
        id_vars="District",
        var_name="Indicator",
        value_name="Percentage",
    )

    fig = px.bar(
        sanitation_long,
        x="District",
        y="Percentage",
        color="Indicator",
        barmode="group",
        title="Sanitation Indicators by District",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


elif page == "Hygiene Assessment":

    st.subheader(
        "🧼 Hygiene Assessment"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Handwashing Facilities",
        f"{df['Handwashing Facilities (%)'].mean():.1f}%",
    )

    c2.metric(
        "Soap Availability",
        f"{df['Soap Availability (%)'].mean():.1f}%",
    )

    c3.metric(
        "Hygiene Awareness",
        f"{df['Hygiene Awareness (%)'].mean():.1f}%",
    )

    c4.metric(
        "Menstrual Hygiene Support",
        f"{df['Menstrual Hygiene Support (%)'].mean():.1f}%",
    )

    hygiene = (
        df.groupby("District")
        [
            [
                "Handwashing Facilities (%)",
                "Soap Availability (%)",
                "Hygiene Awareness (%)",
                "Menstrual Hygiene Support (%)",
            ]
        ]
        .mean()
        .reset_index()
    )

    hygiene_long = hygiene.melt(
        id_vars="District",
        var_name="Indicator",
        value_name="Percentage",
    )

    fig = px.bar(
        hygiene_long,
        x="District",
        y="Percentage",
        color="Indicator",
        barmode="group",
        title="Hygiene Indicators by District",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.subheader(
        "Hygiene Material Access"
    )

    materials = (
        df["Hygiene Material Access"]
        .value_counts()
        .reset_index()
    )

    materials.columns = [
        "Access Level",
        "Locations",
    ]

    fig = px.pie(
        materials,
        names="Access Level",
        values="Locations",
        title="Hygiene Material Access",
        hole=0.4,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


elif page == "WASH Vulnerability":

    st.subheader(
        "⚠️ WASH Vulnerability Analysis"
    )

    c1, c2, c3, c4 = st.columns(4)

    for col, level in zip(
        [c1, c2, c3, c4],
        ["Critical", "High", "Medium", "Low"],
    ):

        count = int(
            (
                df["Vulnerability Level"]
                == level
            ).sum()
        )

        col.metric(
            level,
            count,
        )

    district_risk = (
        df.groupby("District")[
            "Vulnerability Score"
        ]
        .mean()
        .reset_index()
    )

    district_risk[
        "Vulnerability Score"
    ] = district_risk[
        "Vulnerability Score"
    ].round(1)

    fig = px.bar(
        district_risk,
        x="District",
        y="Vulnerability Score",
        title="Average WASH Vulnerability by District",
        text_auto=True,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.subheader(
        "🎯 Priority Locations"
    )

    priority = df.sort_values(
        "Vulnerability Score",
        ascending=False,
    ).head(10)

    st.dataframe(
        priority[
            [
                "District",
                "Upazila",
                "Safe Water Access (%)",
                "Sanitation Coverage (%)",
                "Water Quality Status",
                "Water Shortage",
                "Vulnerability Score",
                "Vulnerability Level",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


elif page == "Service Coverage":

    st.subheader(
        "📍 WASH Service Coverage"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Average Coverage",
        f"{df['Service Coverage Score'].mean():.1f}%",
    )

    c2.metric(
        "High Coverage",
        int(
            (
                df["Coverage Level"]
                == "High"
            ).sum()
        ),
    )

    c3.metric(
        "Low Coverage",
        int(
            (
                df["Coverage Level"]
                == "Low"
            ).sum()
        ),
    )

    district_coverage = (
        df.groupby("District")[
            "Service Coverage Score"
        ]
        .mean()
        .reset_index()
    )

    district_coverage[
        "Service Coverage Score"
    ] = district_coverage[
        "Service Coverage Score"
    ].round(1)

    fig = px.bar(
        district_coverage,
        x="District",
        y="Service Coverage Score",
        title="Average WASH Service Coverage",
        text_auto=True,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    coverage = (
        df["Coverage Level"]
        .value_counts()
        .reset_index()
    )

    coverage.columns = [
        "Coverage Level",
        "Locations",
    ]

    fig = px.pie(
        coverage,
        names="Coverage Level",
        values="Locations",
        title="Service Coverage Distribution",
        hole=0.4,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


elif page == "Reports":

    st.subheader(
        "📑 WASH Monitoring Reports"
    )

    report_type = st.selectbox(
        "Select Report",
        [
            "Full WASH Assessment",
            "Critical & High Vulnerability",
            "District Summary",
            "Service Coverage Summary",
        ],
    )

    if report_type == "Full WASH Assessment":

        report_df = df.copy()

    elif report_type == "Critical & High Vulnerability":

        report_df = df[
            df["Vulnerability Level"].isin(
                ["Critical", "High"]
            )
        ].copy()

    elif report_type == "District Summary":

        report_df = (
            df.groupby("District")
            .agg(
                Locations=("ID", "count"),
                Households=(
                    "Households",
                    "sum",
                ),
                Population=(
                    "Population",
                    "sum",
                ),
                Safe_Water_Access=(
                    "Safe Water Access (%)",
                    "mean",
                ),
                Sanitation_Coverage=(
                    "Sanitation Coverage (%)",
                    "mean",
                ),
                Vulnerability=(
                    "Vulnerability Score",
                    "mean",
                ),
                Service_Coverage=(
                    "Service Coverage Score",
                    "mean",
                ),
            )
            .reset_index()
        )

        numeric_cols = [
            "Safe_Water_Access",
            "Sanitation_Coverage",
            "Vulnerability",
            "Service_Coverage",
        ]

        report_df[
            numeric_cols
        ] = report_df[
            numeric_cols
        ].round(1)

    else:

        report_df = (
            df.groupby("Coverage Level")
            .agg(
                Locations=("ID", "count"),
                Households=(
                    "Households",
                    "sum",
                ),
                Population=(
                    "Population",
                    "sum",
                ),
                Average_Coverage=(
                    "Service Coverage Score",
                    "mean",
                ),
                Average_Vulnerability=(
                    "Vulnerability Score",
                    "mean",
                ),
            )
            .reset_index()
        )

        report_df[
            [
                "Average_Coverage",
                "Average_Vulnerability",
            ]
        ] = report_df[
            [
                "Average_Coverage",
                "Average_Vulnerability",
            ]
        ].round(1)

    st.dataframe(
        report_df,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = report_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Download Report CSV",
        data=csv_data,
        file_name=(
            report_type.lower()
            .replace(" ", "_")
            .replace("&", "and")
            + ".csv"
        ),
        mime="text/csv",
    )


st.sidebar.divider()

st.sidebar.caption(
    "WASH Service Monitoring Dashboard"
)

st.sidebar.caption(
    "Synthetic data for portfolio demonstration."
)