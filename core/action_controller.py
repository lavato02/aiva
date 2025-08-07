import pyautogui
import time
import logging
from typing import Dict, Any, Optional
from config import Config

class ActionController:
    def __init__(self):
        self._active = True
        self._emergency_stop = False
        pyautogui.PAUSE = Config.ACTION_DELAY
        pyautogui.FAILSAFE = Config.SAFE_MODE
        
        # DPI Scaling için çarpan (Windows'ta 125% DPI için 1.25)
        self.scaling_factor = self._detect_scaling_factor()

    def execute(self, action: Dict[str, Any]) -> bool:
        """Bir aksiyonu yürütür. Başarı durumunu döndürür."""
        if not self._active or self._emergency_stop:
            return False

        try:
            action_type = action["action"]
            params = action.get("params", {})
            
            # Koordinatları DPI'ya göre ayarla
            if "x" in params and "y" in params:
                params["x"], params["y"] = self._scale_coordinates(params["x"], params["y"])

            if action_type == "click":
                self._click(
                    params.get("x", 0), 
                    params.get("y", 0),
                    button=params.get("button", "left"),
                    clicks=params.get("clicks", 1)
                )
            elif action_type == "type":
                self._type(params.get("text", ""))
            elif action_type == "press":
                self._press(params.get("key", ""))
            elif action_type == "wait":
                time.sleep(params.get("duration", 1.0))
            elif action_type == "drag":
                self._drag(
                    params.get("x", 0),
                    params.get("y", 0),
                    duration=params.get("duration", 1.0),
                    button=params.get("button", "left")
                )
            elif action_type == "draw":
                self._draw(
                    params.get("x", 0),
                    params.get("y", 0),
                    duration=params.get("duration", 1.0),
                    button=params.get("button", "left")
                )
            elif action_type == "scroll":
                self._scroll(params.get("clicks", 1))
                
            return True

        except pyautogui.FailSafeException:
            self._emergency_stop = True
            logging.warning("Acil durdurma tetiklendi! Fare köşeye gitti.")
            return False
        except Exception as e:
            logging.error(f"Aksiyon hatası: {str(e)}")
            return False

    def _scale_coordinates(self, x: int, y: int) -> tuple:
        """DPI scaling için koordinatları ayarlar"""
        return int(x * self.scaling_factor), int(y * self.scaling_factor)

    def _detect_scaling_factor(self) -> float:
        """Windows DPI scaling faktörünü tespit eder (Varsayılan: 1.0)"""
        try:
            import ctypes
            return ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        except:
            return 1.0

    def _click(self, x: int, y: int, button: str = "left", clicks: int = 1):
        """Kontrollü tıklama"""
        pyautogui.moveTo(x, y, duration=0.3)
        pyautogui.click(button=button, clicks=clicks)

    def _type(self, text: str):
        """Güvenli yazma (özel karakterler için clipboard kullanır)"""
        if Config.SAFE_MODE:
            import pyperclip
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
        else:
            pyautogui.write(text, interval=0.05)

    def _press(self, key: str):
        """Tuş basma (kombinasyonları destekler)"""
        if '+' in key:  # Örnek: "ctrl+alt+delete"
            pyautogui.hotkey(*key.split('+'))
        else:
            pyautogui.press(key.lower())

    def _drag(self, x: int, y: int, duration: float = 1.0, button: str = "left"):
        """Sürükle-bırak işlemi"""
        pyautogui.dragTo(x, y, duration=duration, button=button)

    def _draw(self, x: int, y: int, duration: float = 1.0, button: str = "left"):
        """Çizim yapma (mevcut pozisyondan başlar)"""
        current_x, current_y = pyautogui.position()
        pyautogui.moveTo(current_x, current_y)
        pyautogui.dragTo(x, y, duration=duration, button=button)

    def _scroll(self, clicks: int = 1):
        """Fare tekerleği ile kaydırma"""
        pyautogui.scroll(clicks * 120)  # 120 = standart scroll birimi

    def deactivate(self):
        """Aksiyonları devre dışı bırakır"""
        self._active = False

    def emergency_stop(self):
        """Acil durdurma (FAILSAFE dahil)"""
        self._emergency_stop = True
        pyautogui.moveTo(0, 0)  # FAILSAFE tetiklenir