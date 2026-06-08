import asyncio
import os
import httpx
from datetime import datetime
from app.log.logger import log
from dotenv import load_dotenv

load_dotenv()

class TelegramNotifier:
    BASE_URL = "https://api.telegram.org/bot{token}/sendMessage"
    
    def __init__(self, token: str = "", chat_id: str = ""):
        self.token = token or os.getenv("TELEGRAM_TOKEN", "")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        self.enabled = bool(self.token and self.chat_id)
        
        if not self.enabled:
            log.warning("⚠️ TelegramNotifier desativado: token ou chat_id não configurados")
            
    def _build_message(self, event: dict) -> str:
        label = event.get("label", "")
        sensor_id = event.get("sensor_id", "-")
        desc = event.get("Desc", "")
        anomaly_score = event.get("anomaly_score", 0)
        hora = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        
        icone = "🔴" if label == "Crítico" else "🟡"
        
        return (
            f"{icone} *SENTRYA -- {label.upper()}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🚨 *Alerta de Anomalia* 🚨\n"
            f"📡 *Sensor:* `{sensor_id}`\n"
            f"📊 *Descrição:* `{desc}`\n"
            f"🧠 *Score IA:* `{round(anomaly_score * 100, 1)}%`\n"
            f"🕐 *Hora:* `{hora}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"_Acesse o painel para detalhes._"
        )
        
    async def send_alert(self, event: dict) -> bool:
        
        if not self.enabled:
            return False
        
        url = self.BASE_URL.format(token=self.token)
        message = self._build_message(event)
        
        try: 
            async with httpx.AsyncClient(timeout=8) as client:
                resp = await client.post(url, json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "Markdown",
                })
                if resp.status_code == 200:
                    log.info(f"✅ Telegram: alerta enviado para {self.chat_id}")
                    return True
                else:
                    log.error(f"❌ Telegram erro {resp.status_code}: {resp.text}")
                    return False
        except httpx.TimeoutException:
            log.warning("⚠️  Telegram: timeout — sem internet ou token inválido")
            return False
        except Exception as e:
            log.error(f"❌ Telegram: {e}")
            return False
        
telegram = TelegramNotifier()
 