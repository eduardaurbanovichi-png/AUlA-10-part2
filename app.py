import streamlit as st
import pandas as pd
import cv2
import numpy as np
from database.connection import Base, engine
from controllers.app_controller import AppController

# Configurações de interface
st.set_page_config(page_title="Vision Insight Platform", layout="wide", page_icon="👁️")

# Inicialização automática de tabelas relacionais no Neon.tech
Base.metadata.create_all(bind=engine)

if "app_controller" not in st.session_state:
    st.session_state.app_controller = AppController()

controller = st.session_state.app_controller

# Menu Lateral (Interface)
st.sidebar.title("👁️ Vision Architecture")
st.sidebar.markdown("---")
st.sidebar.info("🟢 Conectado ao PostgreSQL (Neon.tech)")

aba_selecionada = st.sidebar.selectbox("Navegar", ["Captura & Processamento", "Histórico de Análises", "Dashboard Analítico"])

if aba_selecionada == "Captura & Processamento":
    st.title("📸 Captura de Dados Multimídia")
    st.write("Acesse sua webcam e grave observações em áudio integradas ao sistema de gerenciamento.")

    col_view1, col_view2 = st.columns(2)

    with col_view1:
        st.subheader("📷 Entrada de Vídeo")
        camera_data = st.camera_input("Capturar Imagem")
        
        st.markdown("---")
        st.subheader("🎙️ Entrada de Observações em Áudio")
        audio_data = st.file_uploader("Selecione o arquivo de áudio (.wav ou .mp3)", type=["wav", "mp3"])

    with col_view2:
        st.subheader("⚡ Resultados do Processamento")
        if camera_data:
            img_raw_bytes = camera_data.getvalue()
            
            # Conversão e exibição via OpenCV pura (Livre de Pillow)
            nparr = np.frombuffer(img_raw_bytes, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            st.image(img_rgb, caption="Preview da Captura Atual", use_container_width=True)
            
            if st.button("💾 Executar Análise Automática e Salvar", use_container_width=True):
                with st.spinner("Processando fluxos de imagem e áudio..."):
                    audio_raw_bytes = audio_data.read() if audio_data else None
                    registro = controller.executar_fluxo_completo(img_raw_bytes, audio_raw_bytes)
                    
                    if registro:
                        st.success("Dados enviados e persistidos com sucesso no Neon.tech!")
                        st.write(f"**Descrição:** {registro.descricao}")
                        st.write(f"**Métricas:** Luminosidade: {registro.luminosidade} | Nitidez: {registro.nitidez}")
                        st.markdown("**Texto Transcrito (Speech-to-Text):**")
                        st.info(registro.transcricao)
                    else:
                        st.error("Falha ao salvar dados no pipeline de produção.")

elif aba_selecionada == "Histórico de Análises":
    st.title("🗄️ Histórico Geral")
    
    col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
    with col_f1:
        termo_busca = st.text_input("Filtrar por texto (descrição/objetos):")
    with col_f2:
        data_ini = st.date_input("Data de Início", value=None)
    with col_f3:
        data_fim = st.date_input("Data Limite", value=None)

    registros = controller.obter_historico(termo_busca, data_ini, data_fim)

    if not registros:
        st.warning("Nenhum registro encontrado correspondente aos critérios passados.")
    else:
        # Geração de Relatórios estruturados para download
        dados_lote = [{
            "ID": r.id, "Data Criação": r.created_at, "Descrição": r.descricao,
            "Objetos": r.objetos, "Pessoas": r.quantidade_pessoas, "Transcrição": r.transcricao
        } for r in registros]
        df = pd.DataFrame(dados_lote)

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button("📊 Exportar como CSV", data=df.to_csv(index=False), file_name="export_historico.csv", mime="text/csv")
        with col_d2:
            st.download_button("📋 Exportar como JSON", data=df.to_json(orient="records"), file_name="export_historico.json", mime="application/json")

        st.markdown("---")

        for r in registros:
            with st.container():
                c_media, c_details = st.columns([1, 2])
                with c_media:
                    try:
                        img_bgr_disk = cv2.imread(r.image_path)
                        img_rgb_disk = cv2.cvtColor(img_bgr_disk, cv2.COLOR_BGR2RGB)
                        st.image(img_rgb_disk, use_container_width=True)
                        
                        with open(r.image_path, "rb") as f_img:
                            st.download_button("Baixar Imagem", data=f_img, file_name=f"img_{r.id}.jpg", mime="image/jpeg", key=f"dl_i_{r.id}")
                    except Exception:
                        st.error("Mídia local indisponível no servidor.")
                
                with c_details:
                    st.markdown(f"### Registro #{r.id} — {r.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
                    st.write(f"**Descrição:** {r.descricao}")
                    st.write(f"**Objetos Extraídos:** {r.objetos} | **Paleta:** {r.cores}")
                    st.write(f"**Transcrição Gravada:**")
                    st.caption(r.transcricao)
                    
                    if st.button(f"🗑️ Excluir permanentemente #{r.id}", key=f"del_{r.id}"):
                        if controller.remover_registro_completo(r.id, r.image_path):
                            st.success("Excluído!")
                            st.rerun()

elif aba_selecionada == "Dashboard Analítico":
    st.title("📊 Painel Executivo e Métricas")
    registros = controller.obter_historico()
    
    if registros:
        df_dash = pd.DataFrame([{
            "Pessoas": r.quantidade_pessoas,
            "Luminosidade": r.luminosidade,
            "Data": r.created_at.date()
        } for r in registros])

        m1, m2 = st.columns(2)
        m1.metric("Análises Acumuladas", len(df_dash))
        m2.metric("Média de Rostos Monitorados", round(df_dash["Pessoas"].mean(), 2))

        st.subheader("Volume de Processamento Operacional")
        st.line_chart(df_dash["Data"].value_counts())
    else:
        st.info("Nenhum dado cadastrado para consolidar os gráficos operacionais.")