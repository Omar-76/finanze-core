import streamlit as st
from supabase import create_client
import sys
import os

# Allineamento automatico dei percorsi per i moduli corti della stessa cartella
dir_attuale = os.path.dirname(os.path.abspath(__file__))
if dir_attuale not in sys.path:
    sys.path.insert(0, dir_attuale)

st.set_page_config(page_title="Gestione Finanze Core", layout="wide", initial_sidebar_state="expanded")

# Canale di comunicazione API Supabase Diretto
URL = "https://supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiNzdXBhYmFzZSIsInJlZiI6Im1ld3pqbnJpb3ByY3FteHljd3h0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTY4ODg3NzMsImV4cCI6MjAzMjQ2NDc3M30.4iL_YVf_6-B05Fz-u7vF7_W0vYf_6-B05Fz-u7vF7_W"

if 'supabase' not in st.session_state:
    st.session_state.supabase = create_client(URL, KEY)
supabase = st.session_state.supabase

# Stati della sessione
if 'user' not in st.session_state: st.session_state.user = None
if 'nav_scelta' not in st.session_state: st.session_state.nav_scelta = "📊 Cruscotto Patrimoniale"

import modulo_utente

# Schermata di Accesso Amministratore (Bypass di Sicurezza Localizzato per Omar)
if st.session_state.user is None:
    st.title("🔐 Accesso Gestione Finanze")
    with st.form("Login_Fisso_Core"):
        email_in = st.text_input("Indirizzo Email:").strip().lower()
        pass_in = st.text_input("Password Amministratore:", type="password")
        if st.form_submit_button("ACCEDI ALLA PLANCIA", type="primary", use_container_width=True):
            if email_in == "omarcorio@libero.it":
                # Assegna le credenziali storiche del tuo account
                st.session_state.user = type('User', (object,), {'email': 'omarcorio@libero.it', 'id': '70b8c646-7dc7-4fbd-bfbd-b97f5aa8f051'})()
                st.rerun()
            else:
                st.error("❌ Accesso riservato esclusivamente all'account di amministrazione.")
else:
    user_data = st.session_state.user
    profilo = modulo_utente.carica_profilo_amministratore(user_data)

    # Importazione dinamica dei moduli corti e puliti
    import modulo_admin, modulo_dashboard, modulo_inserimento, modulo_config_anagrafiche
    
    with st.sidebar:
        st.write(f"👤 **{profilo['s_nome']}**")
        st.caption(f"🔮 Ruolo: {profilo['ruolo'].upper()}")
        st.divider()
        
        voci_menu = ["📊 Cruscotto Patrimoniale", "📝 Registra Spesa", "⚙️ Gestione Anagrafiche"]
        if st.session_state.nav_scelta == "🏛️ Sala di Controllo":
            voci_menu.append("🏛️ Sala di Controllo")
            
        st.session_state.nav_scelta = st.radio("Sezioni:", voci_menu, index=voci_menu.index(st.session_state.nav_scelta) if st.session_state.nav_scelta in voci_menu else 0)
        st.divider()
        
        if profilo['ruolo'] == 'admin':
            st.write("⚙️ **GESTIONE ECOSSISTEMA**")
            if st.button("🚨 Apri Gestione Licenze & Guadagni", use_container_width=True, type="primary"):
                st.session_state.nav_scelta = "🏛️ Sala di Controllo"
                st.rerun()
            st.divider()
            
        if st.button("🚪 Esci", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # Smistamento dei moduli indipendenti
    if st.session_state.nav_scelta == "🏛️ Sala di Controllo": modulo_admin.mostra_pagina_admin(supabase, user_data)
    elif st.session_state.nav_scelta == "📊 Cruscotto Patrimoniale": modulo_dashboard.mostra_dashboard(supabase, user_data)
    elif st.session_state.nav_scelta == "📝 Registra Spesa": modulo_inserimento.mostra_pagina_inserimento(supabase, user_data)
    elif st.session_state.nav_scelta == "⚙️ Gestione Anagrafiche": modulo_config_anagrafiche.mostra_pagina_anagrafiche(supabase, user_data)
