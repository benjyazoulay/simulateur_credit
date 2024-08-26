import streamlit as st
import pandas as pd

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

st.title("Simulateur de crédit")
# Entrées utilisateur
col1, col2 = st.columns(2)

with col1:
    logement_neuf = st.selectbox("Type de logement", ["Ancien", "Neuf"])

col1, col2, col3 = st.columns(3)

with col1:
    montant_bien = st.number_input("Montant du bien", value=350000)

with col2:
    apport_initial = st.number_input("Apport initial", value=70000)

with col3:
    taux_credit = st.number_input("Taux du crédit (%)", value=3.39) / 100

col1, col2, col3 = st.columns(3)

with col1:
    ptz = st.number_input("Prêt à taux zéro", value=0)

with col2:
    duree = st.number_input("Durée du crédit (années)", value=20)

with col3:
    inflation_annuelle = st.number_input("Inflation annuelle projetée (%)", value=1.7) / 100

# Création du tableau
df = pd.DataFrame(columns=["Poste", "Montant"])

# Ajout de la première ligne
if logement_neuf == "Ancien":
    frais_acquisition = montant_bien * 0.07
    df.loc[1] = ["Frais d'acquisition Ancien", frais_acquisition]
else:
    frais_acquisition = montant_bien * 0.03
    df.loc[1] = ["Frais d'acquisition Neuf", frais_acquisition]

reste_emprunt = montant_bien + frais_acquisition - apport_initial - ptz
df.loc[2] = ["Montant à emprunter (hors PTZ)", reste_emprunt]

interets = calcul_interets_totaux(reste_emprunt, taux_credit, duree)
df.loc[3] = ["Montant total des intérêts", interets]

cout_total = montant_bien + frais_acquisition + interets
df.loc[4] = ["Coût total de l'opération", cout_total]

cout_total_credit = ptz + reste_emprunt + interets
df.loc[5] = ["Coût total du crédit", cout_total_credit]

mensualite = cout_total_credit / (12 * duree)
annualite = cout_total_credit / duree
df.loc[6] = ["Mensualités", mensualite]
df.loc[7] = ["Annualités", annualite]

cout_reel = sum(annualite / ((1 + inflation_annuelle) ** n) for n in range(1, duree + 1))
df.loc[8] = ["Coût réel du crédit (inflation déduite)", cout_reel]
df.loc[9] = ["Surcoût réel du crédit (coût réel - montant emprunté)", cout_reel - (reste_emprunt + ptz)]

# Formatage de la colonne Montant
df['Montant'] = df['Montant'].apply(lambda x: format(x, ',.0f') +'€')

# Affichage du tableau
st.dataframe(df)