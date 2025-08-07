import time
import threading
import logging
from config import Config  # Eksik import eklendi
from core.screen_capture import ScreenCapturer
from core.gpt_vision import GPTVisionAnalyzer
from core.action_controller import ActionController

class AivaRunner:
    def __init__(self, log_callback):
        self.log_callback = log_callback
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._active = False
        self.capturer = ScreenCapturer()
        self.analyzer = GPTVisionAnalyzer()
        self.controller = ActionController()

    @property
    def is_running(self):
        with self._lock:
            return self._active

    def start(self, custom_prompt):
        with self._lock:
            if self._active:
                self.log("Zaten çalışıyor", "WARNING")
                return
            self._active = True
            self._stop_event.clear()

        try:
            self._run_loop(custom_prompt)
        except Exception as e:
            self.log(f"Kritik hata: {str(e)}", "ERROR")
        finally:
            with self._lock:
                self._active = False
            self.log("Çalışma döngüsü sonlandı", "INFO")

    def _run_loop(self, custom_prompt):
        self.log("Aiva başlatıldı", "INFO")
        
        while not self._stop_event.is_set():
            cycle_start = time.time()
            
            try:
                # 1. Ekran görüntüsü al
                screenshot = self.capturer.capture()
                
                # 2. Analiz et
                action = self.analyzer.analyze(screenshot, custom_prompt)
                
                # 3. Aksiyonu uygula
                if not self._stop_event.is_set():
                    self.controller.execute(action)
                    self.log(f"Aksiyon: {action['action']} | Sebep: {action['reason']}", "DEBUG")
                
            except Exception as e:
                self.log(f"Döngü hatası: {str(e)}", "ERROR")

            # Dinamik bekleme süresi
            elapsed = time.time() - cycle_start
            wait_time = max(0, Config.CAPTURE_INTERVAL - elapsed)
            self._stop_event.wait(wait_time)

    def stop(self):
        with self._lock:
            if not self._active:
                return
            self._stop_event.set()

        # Graceful shutdown
        timeout_time = time.time() + Config.STOP_TIMEOUT
        while time.time() < timeout_time:
            with self._lock:
                if not self._active:
                    break
            time.sleep(0.1)

        self.log("Aiva tamamen durduruldu", "INFO")

    def log(self, message, level="INFO"):
        full_msg = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {level} - {message}"
        self.log_callback(full_msg)