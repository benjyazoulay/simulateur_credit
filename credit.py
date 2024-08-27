import streamlit as st
import pandas as pd
import base64
import json

st.set_page_config(page_title="Simulateur de crédit", page_icon="💶", layout="wide")

# Function to encode state to URL
def encode_state(state):
    json_string = json.dumps(state)
    return base64.urlsafe_b64encode(json_string.encode()).decode()

# Function to decode state from URL
def decode_state(encoded_state):
    json_string = base64.urlsafe_b64decode(encoded_state.encode()).decode()
    return json.loads(json_string)

# Récupération de l'état de l'URL
if 'state' in st.experimental_get_query_params():
    state = decode_state(st.experimental_get_query_params()['state'][0])
else:
    state = {
        'logement_neuf': "Ancien",
        'montant_bien': 350000,
        'apport_initial': 80000,
        'taux_credit': 3.39,
        'ptz': 30000,
        'duree': 20,
        'inflation_annuelle': 1.7,
        'nb_parts': 2,
        'taux_assurance': 0.127,
        'frais_agence': 0
    }

#st.title("💶 Simulateur de crédit")
st.markdown("""
    <style>
    /* Style spécifique pour les mobiles */
    @media only screen and (max-width: 600px) {
        h1 {
            text-align: center; /* Centre le texte */
        }
    }
    </style>
    <h1> 
        <a href="https://simulateur-credit.streamlit.app/" target="_self" style="color: inherit; text-decoration: none;">
            💶 Simulateur de crédit
        </a> 
    </h1>
    """, unsafe_allow_html=True)

with st.sidebar:
    col1, col2 = st.columns(2)

    with col1:
        logement_neuf = st.selectbox("Type de logement", ["Ancien", "Neuf"], index=["Ancien", "Neuf"].index(state['logement_neuf']))

    with col2:
        montant_bien = st.number_input("Montant du bien (hors frais d'agence)", value=state['montant_bien'])

    col1, col2 = st.columns(2)

    with col1:
        apport_initial = st.number_input("Apport initial", value=state['apport_initial'])

    with col2:
        taux_credit = st.number_input("Taux du crédit (%)", value=state['taux_credit']) / 100

    col1, col2 = st.columns(2)

    with col1:
        ptz = st.number_input("Prêt à taux zéro", value=state['ptz'])

    with col2:
        duree = st.number_input("Durée du crédit (années)", value=state['duree'])

    col1, col2 = st.columns(2)

    with col1:
        inflation_annuelle = st.number_input("Inflation annuelle projetée (%)", value=state['inflation_annuelle']) / 100
    with col2:
        nb_parts = st.number_input("Nombre d'emprunteurs", value=state['nb_parts'])
        
    col1, col2 = st.columns(2)

    with col1:
        taux_assurance = st.number_input("Taux de l'assurance emprunteur (%)", value=state['taux_assurance']) / 100
    with col2:
        frais_agence = st.number_input("Frais d'agence (%)", value=state['frais_agence']) / 100

# Mise à jour de l'état avec les valeurs actuelles
current_state = {
    'logement_neuf': logement_neuf,
    'montant_bien': montant_bien,
    'apport_initial': apport_initial,
    'taux_credit': taux_credit * 100,  # Conversion pour le stockage
    'ptz': ptz,
    'duree': duree,
    'inflation_annuelle': inflation_annuelle * 100,  # Conversion pour le stockage
    'nb_parts': nb_parts,
    'taux_assurance': taux_assurance * 100,  # Conversion pour le stockage
    'frais_agence': frais_agence * 100  # Conversion pour le stockage
}

# Encodage de l'état dans l'URL
encoded_state = encode_state(current_state)
st.experimental_set_query_params(state=encoded_state)

# CSS pour ajuster les marges latérales et maximiser la largeur
st.markdown(
    """
    <style>
    /* Réduit les marges latérales du conteneur principal et applique des marges négatives */
    .main .block-container {
        padding-left: 1 !important;
        padding-right: 0 !important;
        margin-top: -60px !important;
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




# Création du tableau
df = pd.DataFrame(columns=["Poste", "Montant", "Poste2", "Montant2"])

df.loc[1] = ["Montant du bien (hors frais d'agence)", montant_bien,"Apport initial",apport_initial]
# Ajout de la première ligne
if logement_neuf == "Ancien":
    frais_acquisition = montant_bien * 0.07
    df.loc[2] = ["Frais d'acquisition Ancien 7%", frais_acquisition,f"Durée du crédit : {duree} ans",f"Taux : {format(taux_credit*100,',.2f')}%"]
else:
    frais_acquisition = montant_bien * 0.03
    df.loc[2] = ["Frais d'acquisition Neuf 3%", frais_acquisition,f"Durée du crédit : {duree} ans",f"Taux : {format(taux_credit*100,',.2f')}%"]

total_frais_agence = frais_agence * montant_bien
df.loc[3] = ["Frais d'agence", total_frais_agence,"Montant du bien avec frais d'agence", montant_bien + total_frais_agence]

reste_emprunt = montant_bien + frais_acquisition + total_frais_agence - apport_initial - ptz
total_emprunt = reste_emprunt + ptz
total_assurance = duree*(reste_emprunt + ptz)*taux_assurance
interets = calcul_interets_totaux(reste_emprunt, taux_credit, duree)
df.loc[4] = ["Montant à emprunter (hors PTZ)", reste_emprunt,"Montant total des intérêts", interets]
df.loc[5] = ["Montant total à emprunter (avec PTZ)", total_emprunt,"Assurance emprunteur", total_assurance]

cout_total = montant_bien + frais_acquisition + interets + duree*(reste_emprunt + ptz)*taux_assurance
cout_total_credit = ptz + reste_emprunt + interets + duree*(reste_emprunt + ptz)*taux_assurance
df.loc[6] = ["Coût total de l'opération", cout_total,"Coût total du crédit assuré", cout_total_credit]


mensualite = (cout_total_credit + total_assurance) / (12 * duree)
annualite = (cout_total_credit + total_assurance) / duree
df.loc[7] = ["Mensualités", mensualite, "Mensualités/pers.",mensualite/2]
df.loc[8] = ["Annualités", annualite,"Inflation annuelle projetée",f"{format(inflation_annuelle*100,',.2f')}%"]

cout_reel = sum(annualite / ((1 + inflation_annuelle) ** n) for n in range(1, duree + 1))
df.loc[9] = ["Coût réel du crédit (inflation déduite)", cout_reel,"Surcoût réel du crédit (coût réel - montant emprunté)", cout_reel - (reste_emprunt + ptz)]

# Formatage de la colonne Montant
df['Montant'] = df['Montant'].apply(lambda x: format(x, ',.0f').replace(',',' ') +'€')
df['Montant2'] = df['Montant2'].apply(lambda x: format(x, ',.0f').replace(',',' ') +'€' if isinstance(x, (int, float)) else x)

df.columns = ["1","2","3","4"]
st.dataframe(df, use_container_width=True,hide_index=True)
