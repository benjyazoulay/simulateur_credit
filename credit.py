import streamlit as st
import pandas as pd
st.set_page_config(page_title="Simulateur de crédit", page_icon="💶", layout="wide")
# CSS pour ajuster les marges latérales et maximiser la largeur
st.markdown(
    """
    <style>
    /* Réduit les marges latérales du conteneur principal et applique des marges négatives */
    .main .block-container {
        padding-left: 0 !important;
        padding-right: 0 !important;
        margin-top: -60px !important;
        margin-left: -50px !important; /* Ajuste selon tes besoins */
        margin-right: -50px !important; /* Ajuste selon tes besoins */
    }

    /* Ajuste le conteneur de la section de données pour utiliser 100% de la largeur */
    .stDataFrame {
        width: calc(100% + 80px) !important; /* Ajuste pour compenser les marges négatives */
        margin-left: -50px !important; /* Ajuste selon tes besoins */
        margin-right: -50px !important; /* Ajuste selon tes besoins */
    }

    </style>
    """,
    unsafe_allow_html=True
)

def calcul_interets_totaux(capital, taux_credit, duree):
    # Convertir la durée en mois
    n = duree * 12
    
    # Calculer le taux d'intérêt mensuel
    taux_mensuel = taux_credit / 12
    
    # Calculer la mensualité
    mensualite = (capital * taux_mensuel) / (1 - (1 + taux_mensuel) ** -n)
    
    # Calculer le coût total des intérêts
    interets_totaux = (mensualite * n) - capital
    
    return interets_totaux

st.title("💶Simulateur de crédit")

with st.sidebar:
    col1, col2 = st.columns(2)

    with col1:
        logement_neuf = st.selectbox("Type de logement", ["Ancien", "Neuf"])

    with col2:
        montant_bien = st.number_input("Montant du bien", value=350000)

    col1, col2 = st.columns(2)

    with col1:
        apport_initial = st.number_input("Apport initial", value=70000)

    with col2:
        taux_credit = st.number_input("Taux du crédit (%)", value=3.39) / 100

    col1, col2 = st.columns(2)

    with col1:
        ptz = st.number_input("Prêt à taux zéro", value=0)

    with col2:
        duree = st.number_input("Durée du crédit (années)", value=20)

    col1, col2 = st.columns(2)

    with col1:
        inflation_annuelle = st.number_input("Inflation annuelle projetée (%)", value=1.7) / 100
    with col2:
        nb_parts = st.number_input("Nombre d'emprunteurs", value=2)


# Création du tableau
df = pd.DataFrame(columns=["Poste", "Montant", "Poste2", "Montant2"])

df.loc[1] = ["Montant du bien", montant_bien,"Apport initial",apport_initial]
# Ajout de la première ligne
if logement_neuf == "Ancien":
    frais_acquisition = montant_bien * 0.07
    df.loc[2] = ["Frais d'acquisition Ancien 7%", frais_acquisition,f"Durée du crédit : {duree} ans",f"Taux : {taux_credit*100}%"]
else:
    frais_acquisition = montant_bien * 0.03
    df.loc[2] = ["Frais d'acquisition Neuf 3%", frais_acquisition,f"Durée du crédit : {duree} ans",f"Taux : {taux_credit*100}%"]

reste_emprunt = montant_bien + frais_acquisition - apport_initial - ptz
interets = calcul_interets_totaux(reste_emprunt, taux_credit, duree)
df.loc[3] = ["Montant à emprunter (hors PTZ)", reste_emprunt,"Montant total des intérêts", interets]

cout_total = montant_bien + frais_acquisition + interets
cout_total_credit = ptz + reste_emprunt + interets
df.loc[4] = ["Coût total de l'opération", cout_total,"Coût total du crédit", cout_total_credit]


mensualite = cout_total_credit / (12 * duree)
annualite = cout_total_credit / duree
df.loc[6] = ["Mensualités", mensualite, "Mensualités/pers.",mensualite/2]
df.loc[7] = ["Annualités", annualite,"Inflation annuelle projetée",f"{format(inflation_annuelle*100,',.2f')}%"]

cout_reel = sum(annualite / ((1 + inflation_annuelle) ** n) for n in range(1, duree + 1))
df.loc[8] = ["Coût réel du crédit (inflation déduite)", cout_reel,"Surcoût réel du crédit (coût réel - montant emprunté)", cout_reel - (reste_emprunt + ptz)]

# Formatage de la colonne Montant
df['Montant'] = df['Montant'].apply(lambda x: format(x, ',.0f').replace(',',' ') +'€')
df['Montant2'] = df['Montant2'].apply(lambda x: format(x, ',.0f').replace(',',' ') +'€' if isinstance(x, (int, float)) else x)

df.columns = ["1","2","3","4"]
st.dataframe(df, use_container_width=True,hide_index=True)
