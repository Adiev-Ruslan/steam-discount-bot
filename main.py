import asyncio
import aiohttp

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from config import TOKEN
from steam_api import get_steam_game_data

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Привет! Я бот для отслеживания скидок Steam 🎮"
    )


@dp.message(Command("game"))
async def game_handler(message: Message):
    args = message.text.split()

    if len(args) != 2:
        await message.answer("Использование:\n/game APP_ID")
        return

    try:
        app_id = int(args[1])
    except ValueError:
        await message.answer("App ID должен быть числом")
        return

    async with aiohttp.ClientSession() as session:
        game = await get_steam_game_data(session, app_id)

    if not game:
        await message.answer("Игра не найдена")
        return

    name = game.get("name")
    price = game.get("price_overview")

    if price:
        final_price = price.get("final_formatted")
        discount = price.get("discount_percent")
        text = (
            f"{name}\n"
            f"Цена: {final_price}\n"
            f"Скидка: {discount}%"
        )
    else:
        text = f"{name}\nЦена недоступна"

    await message.answer(text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

