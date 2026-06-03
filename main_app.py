import streamlit as st
from supabase import create_client
import sys
import os

# Mappatura automatica dei moduli corti
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

if 'user' not in st.session_state: st.session_state.user = None
if 'nav_scelta' not in st.session_state: st.session_state.nav_scelta = "🏛️ Sala di Controllo"

# --- INTERFACCIA DI LOGIN AUTENTICATA ---
if st.session_state.user is None:
    st.title("🔐 Accesso Gestione Finanze")
    with st.form("Login_Sistema_SaaS"):
        email_in = st.text_input("Indirizzo Email:").strip().lower()
        pass_in = st.text_input("Password:", type="password")
        
        if st.form_submit_button("ACCEDI ALLA PLANCIA", type="primary", use_container_width=True):
            if email_in and pass_in:
                try:
                    # Autenticazione nativa sul cloud di Supabase
                    res_auth = supabase.auth.sign_in_with_password({"email": email_in, "password": pass_in})
                    if res_auth and res_auth.user:
                        st.session_state.user = res_auth.user
                        st.session_state.nav_scelta = "🏛️ Sala di Controllo"
                        st.rerun()
                except Exception as e:
                    # Riconoscimento e sblocco automatico basato sulla corrispondenza email del database
                    st.error("❌ Credenziali errate o utente non confermato su Supabase.")
            else:
                st.warning("⚠️ Inserisci sia l'email che la password.")
else:
    # --- PROFILAZIONE UTENTE LOGGATO ---
    current_user = st.session_state.user
    ruolo_utente = "user"
    nome_visualizzato = "UTENTE"
    
    try:
        # Estrae in tempo reale l'anagrafica e il ruolo dal database
        res_profile = supabase.table("allowed_users").select("first_name, last_name, role").eq("email", current_user.email).execute().data
        if res_profile and len(res_profile) > 0:
            profilo = res_profile[0]
            ruolo_utente = profilo.get("role", "user")
            nome_visualizzato = f"{profilo.get('last_name', '')} {profilo.get('first_name', '')}".strip().upper()
    except:
        pass

    import modulo_admin
    
    with st.sidebar:
        st.write(f"👤 **{nome_visualizzato}**")
        st.caption(f"🔮 Livello: {ruolo_utente.upper()}")
        st.divider()
        
        # Menu dinamico adattivo basato sul ruolo del database
        voci_menu = []
        if ruolo_utente == "admin":
            voci_menu.append("🏛️ Sala di Controllo")
            
        if voci_menu:
            st.session_state.nav_scelta = st.radio("Sezioni attive:", voci_menu, index=0)
        else:
            st.info("Nessuna sezione abilitata per questo account.")
        st.divider()
        
        if st.button("🚪 Esci", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # Smistamento protetto alla pagina di amministrazione
    if st.session_state.nav_scelta == "🏛️ Sala di Controllo" and ruolo_utente == "admin": 
        modulo_admin.mostra_pagina_admin(supabase, current_user)
