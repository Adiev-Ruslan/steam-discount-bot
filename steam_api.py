import aiohttp


async def get_steam_game_data(session: aiohttp.ClientSession, app_id: int):
    url = (
        f"https://store.steampowered.com/api/appdetails"
        f"?appids={app_id}&cc=ru&l=russian"
    )

    try:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Ошибка Steam API: {response.status}")
                return None

            data = await response.json()
            app_data = data.get(str(app_id))

            if not app_data:
                print("Игра не найдена")
                return None

            if not app_data.get("success"):
                print("Steam вернул success=False")
                return None

            return app_data.get("data")

    except Exception as e:
        print(f"Ошибка запроса: {e}")
        return None

