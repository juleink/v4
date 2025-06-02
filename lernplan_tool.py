
import streamlit as st
import pandas as pd
import fitz

st.set_page_config(page_title="KI-Lernplan Empfehlung", layout="centered")

# Session State zum Tracken der "Seite"
if "page" not in st.session_state:
    st.session_state.page = "upload"

st.title("Erstelle deinen individuellen Lernplan auf Basis deiner Modulplans und deiner Persönlichen Interessen mit snackable!")

# ------------------------ Seite 1: Upload ------------------------
if st.session_state.page == "upload":
    st.subheader("📂 Schritt 1: Lade deinen Modulplan als pdf hoch")
    uploaded_file = st.file_uploader("Wähle deine .pdf-Datei", type="pdf")

    uploaded_file = st.file_uploader("Wähle deine PDF-Datei", type="pdf")

    if uploaded_file:
        try:
            # PDF-Inhalt extrahieren
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                text = "\n".join([page.get_text() for page in doc])

            # Platzhalter-DataFrames simulieren
            st.session_state.df_modules = pd.DataFrame({
                "Modulname": ["Erkannter Modultext"],
                "Semester": [3],
                "Beschreibung": [text[:500]]  # zeige nur einen Ausschnitt
            })

            st.session_state.df_keywords = pd.DataFrame({
                "Clustername": ["Thermodynamik", "Supply Chain Management"],
                "Keyword": ["thermisch", "logistik"]
            })

            st.success("PDF erfolgreich ausgelesen ✅")
            st.dataframe(st.session_state.df_modules)
            if st.button("➡️ Weiter zu Semesterwahl"):
                st.session_state.page = "semester"

        except Exception as e:
            st.error(f"Fehler beim Einlesen der PDF-Datei: {e}")



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
# ------------------------ Seite 3: Lernpläne ------------------------
elif st.session_state.page == "lernplaene":
    st.subheader("🧠 Schritt 3: Deine automatisch erkannten Lernpläne")

    df_modules = st.session_state.df_modules
    df_keywords = st.session_state.df_keywords
    semester = st.session_state.selected_semester

    semester_modules = df_modules[df_modules["Semester"] == semester]

    # Nutzer kann hier eigene Interessen/Schlagwörter eingeben
    user_keywords = st.text_input("✨ Hast du persönliche Interessen oder Wunschthemen? (Komma-getrennt)", "")
    additional_clusters = []
    if user_keywords:
        for word in [w.strip().lower() for w in user_keywords.split(",")]:
            additional_clusters.append({"Clustername": word.title(), "Keyword": word.lower()})

    # Kombiniere alle Keywords (aus Datei + Nutzerinput)
    full_keywords_df = pd.concat([df_keywords, pd.DataFrame(additional_clusters)], ignore_index=True)

    if semester_modules.empty:
        st.warning("⚠️ Keine Module für dieses Semester gefunden.")
    else:
        if "lernplan" not in st.session_state:
            st.session_state.lernplan = []

        for index, row in semester_modules.iterrows():
            modulbeschreibung = str(row["Beschreibung"]).lower()
            modulname = row["Modulname"]
            passende_cluster = set()

            for _, k in full_keywords_df.iterrows():
                keyword = str(k["Keyword"]).lower()
                cluster = k["Clustername"]

                if keyword in modulbeschreibung:
                    passende_cluster.add(cluster)

            if passende_cluster:
                st.markdown(f"### 📘 **{modulname}**")
                st.markdown(f"**Themen-Cluster (inkl. Interessen):** {', '.join(passende_cluster)}")

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
