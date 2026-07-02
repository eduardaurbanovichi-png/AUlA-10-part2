import cv2
import numpy as np
from datetime import datetime
from config.settings import logger

class ComputerVisionService:
    @staticmethod
    def analisar_imagem(image_bytes: bytes) -> dict:
        """Processamento nativo em OpenCV para análise de imagem completa."""
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Matriz de imagem corrompida ou inválida.")

            height, width, _ = img.shape
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Cálculo de Nitidez estrutural
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            nitidez = "Alta" if laplacian_var > 80 else "Média" if laplacian_var > 25 else "Baixa"

            # Análise de Luminosidade técnica
            brightness = float(np.mean(gray))
            luminosidade = "Alta" if brightness > 160 else "Normal" if brightness > 75 else "Baixa"

            # Cores Predominantes
            pixels = img.reshape(-1, 3)
            canal_azul_predominante = int(np.argmax(np.bincount(pixels[:, 0])))
            cor_pred = "Fria (Espectro Azul)" if canal_azul_predominante > 120 else "Quente (Espectro Vermelho)"

            # Preparação para futuros modelos (OpenAI / Gemini) via chaves abertas no dicionário
            agora = datetime.now()
            return {
                "descricao": f"Captura processada via OpenCV. Resolução nativa de {width}x{height} pixels.",
                "objetos": "Elemento de Primeiro Plano Detectado",
                "quantidade_pessoas": 0,
                "rostos": 0,
                "idade": "Não disponível sem IA externa",
                "emocao": "Não disponível sem IA externa",
                "cores": cor_pred,
                "luminosidade": luminosidade,
                "nitidez": f"{nitidez} (Var: {laplacian_var:.1f})",
                "resolucao": f"{width}x{height}",
                "data_captura": agora.strftime("%Y-%m-%d"),
                "horario": agora.strftime("%H:%M:%S")
            }
        except Exception as e:
            logger.error(f"Falha na execução do pipeline OpenCV: {e}")
            raise e