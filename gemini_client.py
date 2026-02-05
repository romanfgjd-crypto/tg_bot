# gemini_client.py - ОНОВЛЕНА ВЕРСІЯ
import google.generativeai as genai
import os

API_KEY = os.getenv("API_KEY")

class GeminiClient:
    def __init__(self):
        if not API_KEY:
            raise ValueError("❌ API_KEY не знайдено!")
        
        # НОВИЙ СПОСІБ:
        genai.configure(api_key=API_KEY)
        
        self.current_mode = "asistant"
        self.system_instructions = {}
        self._load_instructions_from_files()
        self.model = None  # Ініціалізуємо пізніше
    
    def _load_instructions_from_files(self):
        """Завантажити інструкції"""
        instructions_dir = "instructions"
        
        if os.path.exists(instructions_dir):
            for filename in os.listdir(instructions_dir):
                if filename.endswith(".txt"):
                    mode_name = filename[:-4]
                    filepath = os.path.join(instructions_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            self.system_instructions[mode_name] = f.read()
                    except:
                        pass
    
    def set_mode(self, mode: str):
        """Встановити режим"""
        if mode in self.system_instructions:
            self.current_mode = mode
            return True
        self.current_mode = mode
        return False
    
    def get_available_modes(self):
        """Доступні режими"""
        return list(self.system_instructions.keys())
    
    def ask(self, prompt: str) -> str:
        """Запитати AI"""
        try:
            # Створюємо модель (НОВИЙ API!)
            if not self.model:
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Додаємо системну інструкцію
            system_instruction = None
            if self.current_mode in self.system_instructions:
                system_instruction = self.system_instructions[self.current_mode]
            
            # Генеруємо відповідь
            if system_instruction:
                # З системною інструкцією
                response = self.model.generate_content(
                    f"{system_instruction}\n\n{prompt}"
                )
            else:
                # Без системної інструкції
                response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text
            return "Отримано порожню відповідь."
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg:
                return "Ліміт вичерпано. Спробуй пізніше."
            elif "safety" in error_msg.lower():
                return "Запит заблоковано через політику безпеки."
            else:
                return f"Помилка: {error_msg[:100]}"
