import os
from config.settings import logger

class AudioTranscriptionService:
    def __init__(self):
        self.model = None

    def _inicializar_modelo_seguro(self):
        """Lazy loading preventivo: impede travamento de inicialização do Streamlit."""
        if self.model is None:
            from faster_whisper import WhisperModel
            logger.info("Carregando pesos binários do Faster-Whisper...")
            # Configuração ultra-leve para evitar gargalos em CPUs locais / Render
            self.model = WhisperModel("tiny", device="cpu", compute_type="int8")

    def transcrever_audio(self, audio_path: str) -> str:
        try:
            if not os.path.exists(audio_path):
                return "Mídia de áudio não encontrada."
            
            self._inicializar_modelo_seguro()
            segments, _ = self.model.transcribe(audio_path, beam_size=1)
            texto_list = [segment.text for segment in segments]
            resultado = " ".join(texto_list).strip()
            return resultado if resultado else "Áudio processado (Sem fala detectada)."
        except Exception as e:
            logger.error(f"Erro na execução do Speech-to-Text: {e}")
            return f"Falha na transcrição automática: {str(e)}"