import streamlit as st
import pandas as pd
import base64
import json

st.set_page_config(page_title="Simulateur de crédit", page_icon="", layout="wide")

# Fonctions d'encodage/décodage de l'état pour l'URL
def encode_state(state):
    json_string = json.dumps(state)
    return base64.urlsafe_b64encode(json_string.encode()).decode()

def decode_state(encoded_state):
    json_string = base64.urlsafe_b64decode(encoded_state.encode()).decode()
    return json.loads(json_string)

# Récupération de l'état depuis l'URL ou définition de l'état initial
if 'state' in st.experimental_get_query_params():
    state = decode_state(st.experimental_get_query_params()['state'][0])
else:
    state = {
        'logement_neuf': "Ancien",
        'montant_bien': 380000,
        'montant_travaux': 50000,
        'apport_initial': 70000,
        'taux_credit': 3.25,
        'ptz': 0,
        'duree': 20,
        'inflation_annuelle': 1.7,
        'nb_parts': 2,
        'taux_assurance': 0.127,
        'frais_agence': 4
    }

# Titre avec style CSS intégré
st.markdown("""
    <style>
    @media only screen and (max-width: 600px) {
        h1 { text-align: center; }
    }
    </style>
    <h1><a href="https://simulateur-credit.streamlit.app/" target="_self" style="color: inherit; text-decoration: none;"> Simulateur de crédit</a></h1>
""", unsafe_allow_html=True)

# Sidebar pour les entrées utilisateur
with st.sidebar:
    col1, col2 = st.columns(2)
    with col1:
        state['logement_neuf'] = st.selectbox("Type de logement", ["Ancien", "Neuf"], index=["Ancien", "Neuf"].index(state['logement_neuf']))
    with col2:
        state['montant_bien'] = st.number_input("Montant du bien (avec frais d'agence)", value=state['montant_bien'])

    col1, col2 = st.columns(2)
    with col1:
        state['montant_travaux'] = st.number_input("Montant des travaux", value=state['montant_travaux'])

    col1, col2 = st.columns(2)
    with col1:
        state['apport_initial'] = st.number_input("Apport initial", value=state['apport_initial'])
    with col2:
        state['taux_credit'] = st.number_input("Taux du crédit (%)", value=state['taux_credit']) / 100

    col1, col2 = st.columns(2)
    with col1:
        state['ptz'] = st.number_input("Prêt à taux zéro", value=state['ptz'])
    with col2:
        state['duree'] = st.number_input("Durée du crédit (années)", value=state['duree'])

    col1, col2 = st.columns(2)
    with col1:
        state['inflation_annuelle'] = st.number_input("Inflation annuelle projetée (%)", value=state['inflation_annuelle']) / 100
    with col2:
        state['nb_parts'] = st.number_input("Nombre d'emprunteurs", value=state['nb_parts'])

    col1, col2 = st.columns(2)
    with col1:
        state['taux_assurance'] = st.number_input("Taux de l'assurance emprunteur (%)", value=state['taux_assurance']) / 100
    with col2:
        state['frais_agence'] = st.number_input("Frais d'agence (%)", value=state['frais_agence']) / 100

# Encodage de l'état dans l'URL (après toutes les modifications)
encoded_state = encode_state(state)
st.experimental_set_query_params(state=encoded_state)

# CSS pour ajuster les marges
st.markdown("""
    <style>
    .main .block-container {
        padding-left: 1 !important;
        padding-right: 0 !important;
        margin-top: -60px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Fonction de calcul des intérêts
def calcul_interets_totaux(capital, taux_credit, duree):
    n = duree * 12
    taux_mensuel = taux_credit / 12
    mensualite = (capital * taux_mensuel) / (1 - (1 + taux_mensuel) ** -n)
    interets_totaux = (mensualite * n) - capital
    return interets_totaux

# Calculs et création du DataFrame
montant_bien_hors_frais_agence = state['montant_bien'] / (1 + state['frais_agence'] / 100)
total_frais_agence = state['montant_bien'] - montant_bien_hors_frais_agence
montant_total = state['montant_bien'] + state['montant_travaux']

df = pd.DataFrame(columns=["Poste", "Montant", "Poste2", "Montant2"])
df.loc[1] = ["Montant du bien (avec frais d'agence)", state['montant_bien'], "Montant des travaux", state['montant_travaux']]

frais_acquisition = montant_bien_hors_frais_agence * (0.07 if state['logement_neuf'] == "Ancien" else 0.03)
df.loc[2] = ["Frais d'acquisition " + state['logement_neuf'] + " " + ("7%" if state['logement_neuf'] == "Ancien" else "3%"), frais_acquisition, f"Durée du crédit : {state['duree']} ans", f"Taux : {format(state['taux_credit'],',.2f')}%"]

df.loc[3] = ["Frais d'agence", total_frais_agence, "Montant du bien sans frais d'agence", montant_bien_hors_frais_agence]

reste_emprunt = montant_total + frais_acquisition + total_frais_agence - state['apport_initial'] - state['ptz']
total_emprunt = reste_emprunt + state['ptz']
total_assurance = state['duree'] * total_emprunt * (state['taux_assurance'] / 100)
interets = calcul_interets_totaux(reste_emprunt, state['taux_credit'] / 100, state['duree'])

df.loc[4] = ["Montant à emprunter (hors PTZ)", reste_emprunt, "Montant total des intérêts", interets]
df.loc[5] = ["Montant total à emprunter (avec PTZ)", total_emprunt, "Assurance emprunteur", total_assurance]

cout_total = montant_total + frais_acquisition + interets + total_assurance
cout_total_credit = total_emprunt + interets + total_assurance
df.loc[6] = ["Coût total de l'opération", cout_total, "Coût total du crédit assuré", cout_total_credit]

mensualite = (cout_total_credit) / (12 * state['duree'])
annualite = (cout_total_credit) / state['duree']
df.loc[7] = ["Mensualités", mensualite, "Mensualités/pers.", mensualite/state['nb_parts']]
df.loc[8] = ["Annualités", annualite, "Inflation annuelle projetée", f"{format(state['inflation_annuelle'],',.2f')}%"]

cout_reel = sum(annualite / ((1 + state['inflation_ann
