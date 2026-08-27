import sqlite3

DB_NAME = "wash_service_monitoring_v3.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wash_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_date TEXT NOT NULL,
            district TEXT NOT NULL,
            upazila TEXT NOT NULL,
            households INTEGER NOT NULL,
            population INTEGER NOT NULL,
            safe_water_access INTEGER NOT NULL,
            water_source TEXT NOT NULL,
            water_distance REAL NOT NULL,
            daily_water_availability REAL NOT NULL,
            functional_water_points INTEGER NOT NULL,
            sanitation_coverage INTEGER NOT NULL,
            functional_toilets INTEGER NOT NULL,
            shared_toilets INTEGER NOT NULL,
            open_defecation INTEGER NOT NULL,
            handwashing_facilities INTEGER NOT NULL,
            soap_availability INTEGER NOT NULL,
            hygiene_awareness INTEGER NOT NULL,
            menstrual_hygiene_support INTEGER NOT NULL,
            water_quality_status TEXT NOT NULL,
            water_shortage TEXT NOT NULL,
            hygiene_material_access TEXT NOT NULL,
            vulnerability_score INTEGER NOT NULL,
            vulnerability_level TEXT NOT NULL,
            service_coverage_score INTEGER NOT NULL,
            coverage_level TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def seed_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM wash_assessments")

    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    data = [
        ("2026-08-01", "Barishal", "Mehendiganj", 180, 890, 58, "Tube Well", 0.8, 18, 7, 48, 86, 128, 32, 14, 61, 52, 58, "Unsafe", "Yes", "Limited", 84, "Critical", 51, "Medium"),
        ("2026-08-02", "Bhola", "Char Fasson", 210, 1050, 64, "Tube Well", 0.6, 22, 9, 57, 88, 154, 28, 9, 70, 61, 65, "At Risk", "Yes", "Moderate", 72, "High", 59, "Medium"),
        ("2026-08-03", "Patuakhali", "Galachipa", 195, 970, 49, "Rainwater", 1.2, 15, 5, 43, 76, 118, 41, 22, 55, 44, 51, "Unsafe", "Yes", "Limited", 91, "Critical", 43, "Low"),
        ("2026-08-04", "Barguna", "Amtali", 165, 810, 78, "Tube Well", 0.4, 28, 11, 68, 91, 139, 21, 5, 78, 73, 76, "Safe", "No", "Good", 38, "Medium", 76, "High"),
        ("2026-08-05", "Jhalokathi", "Kathalia", 150, 735, 84, "Piped Water", 0.3, 31, 13, 74, 94, 132, 16, 3, 86, 81, 83, "Safe", "No", "Good", 24, "Low", 84, "High"),
        ("2026-08-06", "Pirojpur", "Mathbaria", 175, 860, 81, "Piped Water", 0.5, 29, 12, 71, 93, 158, 19, 4, 84, 79, 82, "Safe", "No", "Good", 28, "Low", 82, "High"),
        ("2026-08-07", "Barishal", "Bakerganj", 220, 1080, 55, "Tube Well", 0.9, 17, 6, 50, 82, 145, 38, 17, 62, 49, 56, "At Risk", "Yes", "Limited", 79, "High", 54, "Medium"),
        ("2026-08-08", "Bhola", "Lalmohan", 190, 940, 62, "Surface Water", 1.4, 14, 5, 53, 79, 135, 35, 19, 58, 46, 54, "Unsafe", "Yes", "Limited", 82, "Critical", 47, "Low"),
        ("2026-08-09", "Patuakhali", "Rangabali", 160, 790, 69, "Rainwater", 0.9, 21, 8, 59, 87, 121, 29, 11, 68, 57, 63, "At Risk", "Yes", "Moderate", 67, "High", 58, "Medium"),
        ("2026-08-10", "Barguna", "Patharghata", 155, 760, 83, "Tube Well", 0.4, 30, 12, 70, 92, 130, 18, 4, 82, 77, 79, "Safe", "No", "Good", 27, "Low", 83, "High")
    ]

    cursor.executemany(
        """
        INSERT INTO wash_assessments (
            assessment_date, district, upazila, households, population,
            safe_water_access, water_source, water_distance, daily_water_availability,
            functional_water_points, sanitation_coverage, functional_toilets, shared_toilets,
            open_defecation, handwashing_facilities, soap_availability, hygiene_awareness,
            menstrual_hygiene_support, water_quality_status, water_shortage,
            hygiene_material_access, vulnerability_score, vulnerability_level,
            service_coverage_score, coverage_level
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        data
    )

    conn.commit()
    conn.close()

def get_assessments():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id, assessment_date, district, upazila, households, population,
            safe_water_access, water_source, water_distance, daily_water_availability,
            functional_water_points, sanitation_coverage, functional_toilets, shared_toilets,
            open_defecation, handwashing_facilities, soap_availability, hygiene_awareness,
            menstrual_hygiene_support, water_quality_status, water_shortage,
            hygiene_material_access, vulnerability_score, vulnerability_level,
            service_coverage_score, coverage_level
        FROM wash_assessments
        ORDER BY vulnerability_score DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows

def add_assessment(
    assessment_date, district, upazila, households, population,
    safe_water_access, water_source, water_distance, daily_water_availability,
    functional_water_points, sanitation_coverage, functional_toilets, shared_toilets,
    open_defecation, handwashing_facilities, soap_availability, hygiene_awareness,
    menstrual_hygiene_support, water_quality_status, water_shortage,
    hygiene_material_access, vulnerability_score, vulnerability_level,
    service_coverage_score, coverage_level
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO wash_assessments (
            assessment_date, district, upazila, households, population,
            safe_water_access, water_source, water_distance, daily_water_availability,
            functional_water_points, sanitation_coverage, functional_toilets, shared_toilets,
            open_defecation, handwashing_facilities, soap_availability, hygiene_awareness,
            menstrual_hygiene_support, water_quality_status, water_shortage,
            hygiene_material_access, vulnerability_score, vulnerability_level,
            service_coverage_score, coverage_level
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            assessment_date, district, upazila, households, population,
            safe_water_access, water_source, water_distance, daily_water_availability,
            functional_water_points, sanitation_coverage, functional_toilets, shared_toilets,
            open_defecation, handwashing_facilities, soap_availability, hygiene_awareness,
            menstrual_hygiene_support, water_quality_status, water_shortage,
            hygiene_material_access, vulnerability_score, vulnerability_level,
            service_coverage_score, coverage_level
        )
    )

    conn.commit()
    conn.close()