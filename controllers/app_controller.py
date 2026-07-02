import os
from uuid import uuid4
from typing import Optional, List
from config.settings import UPLOAD_FOLDER, logger
from database.connection import SessionLocal
from models.analise import AnaliseModel
from repositories.analise_repository import AnaliseRepository
from services.cv_service import ComputerVisionService
from services.audio_service import AudioTranscriptionService

class AppController:
    def __init__(self):
        self.db = SessionLocal()
        self.repository = AnaliseRepository(self.db)
        self.cv_service = ComputerVisionService()
        self.audio_service = AudioTranscriptionService()

    def executar_fluxo_completo(self, image_bytes: bytes, audio_bytes: Optional[bytes]) -> Optional[AnaliseModel]:
        try:
            # 1. Armazenamento da imagem
            img_filename = f"cv_{uuid4().hex}.jpg"
            img_path = UPLOAD_FOLDER / img_filename
            with open(img_path, "wb") as f:
                f.write(image_bytes)

            # 2. Execução da análise computacional
            dados_analise = self.cv_service.analisar_imagem(image_bytes)

            # 3. Execução do processamento de áudio (se capturado)
            texto_transcrito = "Nenhum áudio associado a este registro."
            if audio_bytes:
                audio_filename = f"audio_{uuid4().hex}.wav"
                audio_path = UPLOAD_FOLDER / audio_filename
                with open(audio_path, "wb") as f:
                    f.write(audio_bytes)
                
                texto_transcrito = self.audio_service.transcrever_audio(str(audio_path))
                
                if os.path.exists(audio_path):
                    os.remove(audio_path)

            # 4. Construção do modelo relacional
            nova_analise = AnaliseModel(
                image_path=str(img_path),
                descricao=dados_analise["descricao"],
                objetos=dados_analise["objetos"],
                quantidade_pessoas=dados_analise["quantidade_pessoas"],
                rostos=dados_analise["rostos"],
                idade=dados_analise["idade"],
                emocao=dados_analise["emocao"],
                cores=dados_analise["cores"],
                luminosidade=dados_analise["luminosidade"],
                nitidez=dados_analise["nitidez"],
                transcricao=texto_transcrito,
                json_resultado=dados_analise
            )

            # 5. Persistência de dados segura
            return self.repository.save(nova_analise)
        except Exception as e:
            logger.error(f"Erro de orquestração no controlador: {e}")
            return None

    def obter_historico(self, search: str = "", start_date=None, end_date=None) -> List[AnaliseModel]:
        return self.repository.get_all(search, start_date, end_date)

    def remover_registro_completo(self, registro_id: int, image_path: str) -> bool:
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                logger.error(f"Não foi possível limpar o arquivo físico: {e}")
        return self.repository.delete(registro_id)

    def fechar_sessoes(self):
        self.db.close()