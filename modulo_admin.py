import streamlit as st
import pandas as pd
import datetime

def mostra_pagina_admin(supabase, user_data):
    st.title("🏛️ Sala di Controllo (Admin Supremo)")
    st.write(f"Gestione Ecosistema SaaS — Collegato come: **{user_data.email}**")
    
    # Tre schede pulite e separate per i controlli di amministrazione
    tab1, tab2, tab3 = st.tabs(["💰 1. Listino Prezzi & Nuove Licenze", "👥 2. Attivazione Utenti & Guadagni", "🌐 3. Emoji di Sistema Pubbliche"])
    
    # Inizializzazione e lettura sicura delle tabelle dal database pulito
    piani = []
    utenti = []
    pagamenti = []
    emojis = []

    try: piani = supabase.table("subscription_plans").select("*").order("id").execute().data
    except: pass

    try: utenti = supabase.table("allowed_users").select("*").order("last_name").execute().data
    except: pass

    try:
        res_pag = supabase.table("payment_ledger").select("*").execute().data
        if res_pag: pagamenti = res_pag
    except: pagamenti = []
        
    try: emojis = supabase.table("system_emojis").select("*").order("id").execute().data
    except: pass

    # --- TAB 1: LISTINO PREZZI & CREAZIONE DIRETTA DA PANNELLO ---
    with tab1:
        st.write("### ➕ Crea Nuovo Piano Commerciale")
        with st.form("Form_Creazione_Nuovo_Piano", clear_on_submit=True):
            col_add1, col_add2 = st.columns(2)
            with col_add1:
                nuovo_tipo = st.text_input("Codice Piano (es. free, mensile, annuale):").strip().lower().replace(" ", "_")
                nuovo_prezzo = st.number_input("Prezzo di Vendita (€):", min_value=0.00, value=0.00, format="%.2f")
            with col_add2:
                nuova_durata = st.number_input("Durata Licenza (Giorni):", min_value=1, value=30, step=1)
                nuova_desc = st.text_input("Descrizione Commerciale Pubblica:").strip()
            
            if st.form_submit_button("🚀 PUBBLICA NUOVO PIANO NEL LISTINO", use_container_width=True, type="primary"):
                if nuovo_tipo and nuova_desc:
                    try:
                        supabase.table("subscription_plans").insert({
                            "plan_type": nuovo_tipo,
                            "price_euro": float(nuovo_prezzo),
                            "duration_days": int(nuova_durata),
                            "description": nuova_desc
                        }).execute()
                        st.success(f"✨ Piano '{nuovo_tipo.upper()}' pubblicato con successo nel database ed attivo!")
                        st.rerun()
                    except Exception as ex: 
                        st.error(f"❌ Errore durante il salvataggio. Verifica che il Codice Piano non sia un duplicato. Errore: {ex}")
                else: 
                    st.warning("⚠️ Compila tutti i campi obbligatori (Codice Piano e Descrizione).")

        st.divider()
        st.write("### ⚙️ Modifica Tariffe Piani Esistenti")
        if piani:
            for p in piani:
                with st.expander(f"➔ Piano {str(p['plan_type']).upper()} — Corrente: € {float(p['price_euro']):.2f}"):
                    st.markdown(f"**Modifica parametri per: {str(p['plan_type']).upper()}**")
                    v_desc = st.text_input("Descrizione Pubblica:", value=str(p['description']), key=f"ds_txt_{p['id']}")
                    v_prezzo = st.number_input("Prezzo (€):", min_value=0.00, value=float(p['price_euro']), format="%.2f", key=f"pr_num_{p['id']}")
                    v_giorni = st.number_input("Durata (Giorni):", min_value=1, value=int(p['duration_days']), key=f"dr_int_{p['id']}")
                    
                    if st.button("💾 SALVA VARIAZIONI", key=f"btn_save_p_{p['id']}", use_container_width=True):
                        try:
                            supabase.table("subscription_plans").update({
                                "price_euro": v_prezzo, "duration_days": v_giorni, "description": v_desc
                            }).eq("id", p['id']).execute()
                            st.success("✔️ Tariffe aggiornate con successo nel cloud!")
                            st.rerun()
                        except Exception as ex: st.error(f"Errore aggiornamento: {ex}")
        else:
            st.info("ℹ️ Nessun piano tariffario configurato nel database. Usa il form sopra per creare il primo piano!")

    # --- TAB 2: ATTIVAZIONE MANUALE LICENZE UTENTI ---
    with tab2:
        st.subheader("💳 Attivazione Licenze al Ricevimento del Pagamento")
        if utenti:
            mappa_scelte = {}
            for u in utenti:
                if u['email'] != 'omarcorio@libero.it':
                    cognome_u = str(u.get('last_name', 'UTENTE')).upper()
                    nome_u = str(u.get('first_name', '')).upper()
                    label = f"{cognome_u} {nome_u} ({u['email']})"
                    mappa_scelte[label] = u
            
            if mappa_scelte:
                scelta_utente = st.selectbox("Seleziona il cliente da attivare:", list(mappa_scelte.keys()))
                utente_scelto = mappa_scelte[scelta_utente]
                
                piani_disponibili = [p['plan_type'] for p in piani] if piani else ["mensile", "annuale"]
                piano_scelto = st.selectbox("Seleziona l'abbonamento acquistato:", piani_disponibili)
                
                if st.button("SBLOCCA UTENTE E REGISTRA INCASSO", type="primary", use_container_width=True):
                    try:
                        info_p = next((p for p in piani if p['plan_type'] == piano_scelto), {"duration_days": 30, "price_euro": 0.00})
                        giorni_estensione = int(info_p['duration_days'])
                        valore_pagato = float(info_p['price_euro'])
                        nuova_scadenza = datetime.date.today() + datetime.timedelta(days=giorni_estensione)
                        
                        # 1. Scrittura contabile nel registro entrate amministratore
                        try:
                            supabase.table("payment_ledger").insert({
                                "user_id": utente_scelto['id'], "user_email": utente_scelto['email'], "amount_paid": valore_pagato, 
                                "plan_assigned": piano_scelto, "expiration_extended_to": str(nuova_scadenza)
                            }).execute()
                        except: pass
                        
                        # 2. Sblocco licenza e aggancio piano_id reale all'anagrafica utente
                        id_piano_scelto = info_p.get('id')
                        supabase.table("allowed_users").update({
                            "license_status": "active", 
                            "plan_start_date": str(datetime.date.today()), 
                            "license_expiration_date": str(nuova_scadenza),
                            "plan_id": id_piano_scelto
                        }).eq("email", utente_scelto['email']).execute()
                        
                        st.success(f"✨ Licenza attivata per {utente_scelto['email']}!")
                        st.rerun()
                    except Exception as ex: st.error(f"Errore attivazione: {ex}")
            else:
                st.info("ℹ️ Nessun utente registrato oltre a te.")
        else:
            st.info("ℹ️ Nessun utente registrato in archivio.")
        
        st.divider()
        st.subheader("📈 Contatore Guadagni SaaS")
        if pagamenti and len(pagamenti) > 0:
            df_pagamenti = pd.DataFrame(pagamenti)
            incasso_totale = df_pagamenti["amount_paid"].apply(float).sum() if "amount_paid" in df_pagamenti.columns else 0.00
            st.metric("Euro Incassati Totali", f"€ {incasso_totale:.2f}")
            st.dataframe(df_pagamenti, use_container_width=True, hide_index=True)
        else:
            st.metric("Euro Incassati Totali", "€ 0.00")
            st.info("Nessun pagamento registrato in archivio.")

    # --- TAB 3: GESTIONE EMOJI PUBBLICHE E COLLABORATIVE ---
    with tab3:
        st.subheader("🌐 Libreria Emoji di Sistema Condivisa")
        st.write("Aggiungi emoji pubbliche. Diventeranno immediatamente visibili a tutti gli utenti dell'app.")
        
        with st.form("Form_Nuova_Emoji", clear_on_submit=True):
            col_em1, col_em2 = st.columns(2)
            with col_em1:
                nuovo_carattere = st.text_input("Carattere Emoji (Incolla una sola emoji, es. 🏦, 🚗):").strip()
            with col_add2:
                nuovo_nome_em = st.text_input("Nome/Descrizione dell'icona (es. banca, auto):").strip().lower()
                
            if st.form_submit_button("📥 INSERISCI EMOJI NELLA LIBRERIA PUBBLICA", use_container_width=True):
                if nuovo_carattere and nuovo_nome_em:
                    try:
                        supabase.table("system_emojis").insert({
                            "emoji": nuovo_carattere,
                            "name": nuevo_nome_em
                        }).execute()
                        st.success("✔️ Emoji salvata e pubblicata globalmente!")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"❌ Impossibile salvare l'emoji: {ex}")
                else:
                    st.warning("⚠️ Compila sia l'emoji che il nome descrittivo.")
                    
        st.divider()
        st.write("### 🖼️ Emoji Pubbliche Correnti nel Database")
        if emojis:
            df_emojis = pd.DataFrame(emojis)
            st.dataframe(df_emojis[["id", "emoji", "name"]], use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ La libreria di emoji è attualmente vuota. Usa il modulo sopra per inserire la prima!")
