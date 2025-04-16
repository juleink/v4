
import streamlit as st
import pandas as pd

st.set_page_config(page_title="KI-Lernplan Empfehlung", layout="centered")

# Session State zum Tracken der "Seite"
if "page" not in st.session_state:
    st.session_state.page = "upload"

st.title("🎓 KI-gestützte Lernplan-Empfehlung")

# ------------------------ Seite 1: Upload ------------------------
if st.session_state.page == "upload":
    st.subheader("📂 Schritt 1: Lade deine Excel-Datei hoch")
    uploaded_file = st.file_uploader("Wähle deine .xlsx-Datei", type="xlsx")

    if uploaded_file:
        try:
            st.session_state.df_modules = pd.read_excel(uploaded_file, sheet_name="Module", engine="openpyxl")
            st.session_state.df_keywords = pd.read_excel(uploaded_file, sheet_name="Keywords", engine="openpyxl")

            st.success("Datei erfolgreich geladen ✅")
            st.dataframe(st.session_state.df_modules)
            if st.button("➡️ Weiter zu Semesterwahl"):
                st.session_state.page = "semester"

        except Exception as e:
            st.error(f"Fehler beim Einlesen der Datei: {e}")

# ------------------------ Seite 2: Semesterwahl ------------------------
elif st.session_state.page == "semester":
    st.subheader("📅 Schritt 2: Wähle dein aktuelles Semester")

    if "df_modules" in st.session_state:
        semester = st.selectbox("Wähle dein Semester", sorted(st.session_state.df_modules["Semester"].unique()))
        st.session_state.selected_semester = semester

        if st.button("➡️ Lernpläne anzeigen"):
            st.session_state.page = "lernplaene"
    else:
        st.warning("⚠️ Bitte lade zuerst eine Datei hoch.")
        if st.button("🔙 Zurück zum Upload"):
            st.session_state.page = "upload"

# ------------------------ Seite 3: Lernpläne ------------------------
elif st.session_state.page == "lernplaene":
    st.subheader("🧠 Schritt 3: Deine automatisch erkannten Lernpläne")

    df_modules = st.session_state.df_modules
    df_keywords = st.session_state.df_keywords
    semester = st.session_state.selected_semester

    semester_modules = df_modules[df_modules["Semester"] == semester]

    if semester_modules.empty:
        st.warning("⚠️ Keine Module für dieses Semester gefunden.")
    else:
        if "lernplan" not in st.session_state:
            st.session_state.lernplan = []

        for index, row in semester_modules.iterrows():
            modulbeschreibung = str(row["Beschreibung"]).lower()
            modulname = row["Modulname"]
            passende_cluster = set()

            for _, k in df_keywords.iterrows():
                keyword = str(k["Keyword"]).lower()
                cluster = k["Clustername"]

                if keyword in modulbeschreibung:
                    passende_cluster.add(cluster)

            if passende_cluster:
                st.markdown(f"### 📘 **{modulname}**")
                st.markdown(f"**Erkannte Themen-Cluster:** {', '.join(passende_cluster)}")

                if st.button(f"📌 Zu Lernplan hinzufügen – {modulname}"):
                    st.session_state.lernplan.append({
                        "Modul": modulname,
                        "Cluster": list(passende_cluster)
                    })
            else:
                st.markdown(f"### 🟡 {modulname}")
                st.markdown("_Keine passenden Keywords erkannt_")

    if st.button("📊 Weiter zu meinem Dashboard"):
        st.session_state.page = "dashboard"

    if st.button("🔙 Zurück zur Semesterwahl"):
        st.session_state.page = "semester"

# ------------------------ Seite 4: Dashboard ------------------------
elif st.session_state.page == "dashboard":
    st.subheader("📋 Dein persönliches Lernplan-Dashboard")

    lernplan = st.session_state.get("lernplan", [])

    if lernplan:
        for eintrag in lernplan:
            st.markdown(f"### ✅ {eintrag['Modul']}")
            st.markdown(f"**Cluster:** {', '.join(eintrag['Cluster'])}")
            st.markdown("_📺 Lernvideos folgen bald durch KI..._")
    else:
        st.info("Du hast noch keine Lernpläne ausgewählt.")

    if st.button("🔁 Zurück zum Upload"):
        st.session_state.page = "upload"
