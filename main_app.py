import streamlit as st
from supabase import create_client
import hashlib
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

# --- INTERFACCIA DI LOGIN NATURALE E DIRETTA DA DATABASE ---
if st.session_state.user is None:
    st.title("🔐 Accesso Gestione Finanze")
    with st.form("Login_Database_Standard"):
        email_in = st.text_input("Indirizzo Email:").strip().lower()
        pass_in = st.text_input("Password:", type="password")
        
        if st.form_submit_button("ACCEDI ALLA PLANCIA", type="primary", use_container_width=True):
            if email_in and pass_in:
                try:
                    # Cifratura della password inserita per il confronto
                    hash_inserito = hashlib.sha256(pass_in.encode()).hexdigest()
                    
                    # Interrogazione diretta della tabella utenti
                    res_user = supabase.table("allowed_users").select("*").eq("email", email_in).eq("password_hash", hash_inserito).execute().data
                    
                    if res_user and len(res_user) > 0:
                        utente_valido = res_user[0]
                        st.session_state.user = type('User', (object,), {
                            'email': utente_valido['email'], 
                            'id': utente_valido['id'],
                            'role': utente_valido['role'],
                            'nome_completo': f"{utente_valido.get('last_name', '')} {utente_valido.get('first_name', '')}".strip().upper()
                        })()
                        st.session_state.nav_scelta = "🏛️ Sala di Controllo"
                        st.rerun()
                    else:
                        st.error("❌ Email o password errate.")
                except Exception as e:
                    st.error(f"❌ Errore di comunicazione con il database: {e}")
            else:
                st.warning("⚠️ Inserisci sia l'email che la password.")
else:
    current_user = st.session_state.user
    ruolo_utente = getattr(current_user, 'role', 'user')
    nome_visualizzato = getattr(current_user, 'nome_completo', 'UTENTE')

    import modulo_admin
    
    with st.sidebar:
        st.write(f"👤 **{nome_visualizzato}**")
        st.caption(f"🔮 Livello: {ruolo_utente.upper()}")
        st.divider()
        
        voci_menu = []
        if ruolo_utente == "admin":
            voci_menu.append("🏛️ Sala di Controllo")
            
        if voci_menu:
            st.session_state.nav_scelta = st.radio("Sezioni attive:", voci_menu, index=0)
        st.divider()
        
        if st.button("🚪 Esci", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    if st.session_state.nav_scelta == "🏛️ Sala di Controllo" and ruolo_utente == "admin": 
        modulo_admin.mostra_pagina_admin(supabase, current_user)
