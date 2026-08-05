import asyncio
import aiohttp

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import TOKEN
from steam_api import get_steam_game_data
from database import (init_db, add_subscription, get_all_subscriptions,
                      update_price, get_subscriptions_by_user, remove_subscription)

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

async def main():
    init_db()
    scheduler.start()
    await dp.start_polling(bot)


@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Привет! Я бот для отслеживания скидок Steam 🎮"
    )


@dp.message(Command("subscribe"))
async def subscription_handler(message: Message):
    """Позволяет отслеживать игру (по id)"""

    args = message.text.split()

    if len(args) != 2:
        await message.answer("Использование:\n/subscribe APP_ID")
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

    user_id = message.from_user.id
    game_name = game.get("name")

    subscriptions = get_subscriptions_by_user(user_id)
    already_subscribed = False

    for sub in subscriptions:
        if sub[2] == app_id:
            already_subscribed = True
            break

    if already_subscribed:
        await message.answer(f"Среди Ваших подписок уже есть игра {game_name}.")
        return

    price = game.get("price_overview")
    if price:
        last_price = price.get("final")
    else:
        last_price = None

    add_subscription(user_id, app_id, game_name, last_price)
    await message.answer(f"Подписка на {game_name} оформлена ✅")


@dp.message(Command("unsubscribe"))
async def unsubscribe_handler(message: Message):
    """
    Отменяет отслеживание игры (по id)
    """

    args = message.text.split()
    user_id = message.from_user.id
    subscriptions = get_subscriptions_by_user(user_id)
    game_name = None

    if len(args) != 2:
        await message.answer("Использование:\n/unsubscribe APP_ID")
        return

    try:
        app_id = int(args[1])
    except ValueError:
        await message.answer("App ID должен быть числом")
        return

    for sub in subscriptions:
        if sub[2] == app_id:
            game_name = sub[3]
            break

    if game_name:
        remove_subscription(user_id, app_id)
        await message.answer(f"Вы больше не отслеживаете {game_name}.")
    else:
        await message.answer(f"В данный момент Вы не отслеживаете игру с id {app_id}.")


@dp.message(Command("game"))
async def game_handler(message: Message):
    """Выводит актуальные цену и скидку на игру """

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


@dp.message(Command("mysubs"))
async def my_subs_handler(message: Message):
    """
    Показывает список подписок (отслеживаний) на игры у конкретного пользоватея
    """

    user_id = message.from_user.id
    subscriptions = get_subscriptions_by_user(user_id)

    if not subscriptions:
        await message.answer("Вы пока что не отслеживаете какие-либо игры. ")
        return

    lines = []
    for sub in subscriptions:
        game_name = sub[3]
        last_price = sub[4]

        if last_price:
            price_text = f"{int(last_price / 100)} руб"
        else:
            price_text = "цена неизвестна"

        lines.append(f"{game_name} - {price_text}")

    text = "\n".join(lines)
    await message.answer(text)


async def check_prices():
    """Фоном проверяет  цены каждые 3 часа (это время можно изменить)"""
    subscriptions = get_all_subscriptions()

    async with aiohttp.ClientSession() as session:
        for sub in subscriptions:
            subscription_id = sub[0]
            user_id = sub[1]
            app_id = sub[2]
            game_name = sub[3]
            last_price = sub[4]

            game = await get_steam_game_data(session, app_id)
            if not game:
                continue

            price = game.get("price_overview")
            if not price:
                continue

            discount = price.get("discount_percent")
            new_price = price.get("final")

            if last_price and new_price < last_price:
                await bot.send_message(
                    user_id,
                    f"""На игру {game_name}  сейчас действует скидка 
                    {discount} %. С учетом скидки, теперь цена {game_name}
                     составляет {int(new_price / 100)}."""
                )

            update_price(subscription_id, new_price)


scheduler.add_job(check_prices, "interval", hours=3)

if __name__ == "__main__":
    asyncio.run(main())

