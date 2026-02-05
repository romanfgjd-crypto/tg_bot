import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# Імпорт нашого AI клієнта
from gemini_client import GeminiClient

class TelegramBot:
    def __init__(self, ai_client, token: str):
        self.token = token
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.router = Router()
        
        # Ініціалізація AI (без ядра!)
        self.ai_client = ai_client
        
        # Реєструємо обробники
        self.setup_handlers()
        self.dp.include_router(self.router)
        
    def setup_handlers(self):
        """Налаштування команд бота"""
        
        @self.router.message(Command("start"))
        async def start_cmd(message: Message):
            await message.answer(
                "🤖 Привіт! Я AI-бот на основі Gemini.\n"
                f"Поточний режим: {self.ai_client.current_mode}\n\n"
                "Обери режим або напиши повідомлення.",
                reply_markup=self.get_keyboard()
            )
            print(f"📱 Користувач {message.from_user.id} запустив бота")
        
        @self.router.message(lambda m: m.text in ["👨‍💻 Програміст", "🧠 Психолог", "ℹ️ Режими"])
        async def handle_buttons(message: Message):
            if message.text == "👨‍💻 Програміст":
                self.ai_client.set_mode("programmer")
                await message.answer("✅ Режим 👨‍💻 Програміст активовано")
                
            elif message.text == "🧠 Психолог":
                self.ai_client.set_mode("asistant")
                await message.answer("✅ Режим 🧠 Психолог активовано")
                
            elif message.text == "ℹ️ Режими":
                modes = self.ai_client.get_available_modes()
                await message.answer(
                    "📌 Доступні режими:\n" + "\n".join(f"• {m}" for m in modes)
                )
        
        @self.router.message()
        async def ai_chat(message: Message):
            """Обробка всіх повідомлень"""
            # Ігноруємо команди
            if message.text and message.text.startswith('/'):
                return
            
            print(f"📥 Отримано: {message.text[:50]}...")
            await message.answer("⏳ Думаю...")
            
            # Запитуємо AI
            response = self.ai_client.ask(message.text)
            
            # Надсилаємо відповідь
            max_len = 4000
            for i in range(0, len(response), max_len):
                await message.answer(response[i:i+max_len])
            
            print(f"📤 Відправлено відповідь ({len(response)} символів)")
    
    def get_keyboard(self):
        """Створити клавіатуру"""
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="👨‍💻 Програміст"), KeyboardButton(text="🧠 Психолог")],
                [KeyboardButton(text="ℹ️ Режими"), KeyboardButton(text="🆘 Допомога")]
            ],
            resize_keyboard=True
        )
    
    async def start_polling(self):
        """Запустити бота"""
        print("🤖 Telegram Bot запущено!")
        print("👉 Напиши /start в Telegram")
        await self.dp.start_polling(self.bot)

# ---- Функція для запуску ----
async def main():
    import os
    
    # Отримуємо токен з змінних оточення
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        print("❌ Помилка: BOT_TOKEN не знайдено!")
        print("👉 Додай змінну оточення або вкажи прямо в коді")
        return
    
    ai_client = GeminiClient()
    # Створюємо та запускаємо бота
    bot = TelegramBot(ai_client, BOT_TOKEN)
    await bot.start_polling()

if __name__ == "__main__":
    # Запускаємо бота
    asyncio.run(main())