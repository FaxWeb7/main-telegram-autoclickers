import asyncio
from pprint import pprint
from time import time
import aiohttp
import json
from typing import Union
from pyrogram.errors import UserNotParticipant

from bot.config import settings
# from bot.utils.scripts import escape_html
from bot.utils.logger import *

b_name = {
    "b_01": "TapFlix",
    "b_02": "Monument to Toncoin",
    "b_03": "Factory",
    "b_04": "Tapping Guru",
    "b_05": "To the moon!",
    "b_06": "Trampoline",
    "b_07": "Bit Club",
    "b_08": "Karaoke",
    "b_09": "Point of view",
    "b_10": "Prosecco fountain",
    "b_11": "Biker club",
    "b_12": "Istukan",
    "b_13": "Salmon",
    "b_14": "Telegram duck",
    "b_15": "Brewery",
    "b_16": "Webrave",
    "b_17": "Gold button",
    "b_18": "Casino",
    "b_19": "Cooking hub",
    "b_20": "Tap stadium",
}


async def update_build(http_client: aiohttp.ClientSession, b_id: str) -> Union[str, dict]:
    response_text = ""
    try:
        response = await http_client.post(url="https://api.tapswap.club/api/town/upgrade_building",
                                          json={"building_id": b_id})
        response_text = await response.text()
        response.raise_for_status()

        message = json.loads(response_text)

        return message  # возвращаем инфу об обновлении здания

    except Exception as error:
        # logger.error(
        #     f"{self.session_name} | Unknown error when Update [{b_id}] <y>{b_name[b_id]}</y>: {escape_html(error)} | "
        #     f"Response text: {escape_html(response_text)[:128]}..."
        # )
        await asyncio.sleep(delay=3)
        return str(message["message"])


# Возвращает False если что-то идет не так или все строители заняты
async def build_town(self, http_client: aiohttp.ClientSession, profile_data) -> bool:
    global b_name

    # Текущие ресурсы
    b_crystals = profile_data["player"]["crystals"]
    b_blocks = profile_data["player"]["blocks"]
    b_videos = profile_data["player"]["videos"]
    b_reward = profile_data["player"]["stat"]["reward"]
    # Список зданий готовых к апгрейду

    upgrade_list = dict()

    # Создадим словарь зданий возможных к апгрейду с указанием уровня {id: [lvl, rate]}
    for id, name in b_name.items():
        cost = build_new_level(id, profile_data)

        if cost is None:
            continue

        cur_lvl = build_current_level(id, profile_data)

        # Проверим не строится ли здание еще
        is_construct = False
        for data in profile_data["player"]["town"]["buildings"]:
            if data['id'] == id and data["ready_at"] / 1000 > time():
                is_construct = True
                break
        if is_construct:
            continue

        # Проверим достижение максимального уровня
        if cur_lvl >= settings.MAX_TOWN_LEVEL:
            continue

        r_name = r_lvl = None
        if (
                cost["shares"] <= b_reward
                and cost["blocks"] <= b_blocks
                and cost["videos"] <= b_videos
        ):
            if cost["r_id"] is not None:
                r_name = b_name[cost["r_id"]]
                r_lvl = cost["r_level"]
                if r_lvl <= build_current_level(cost["r_id"], profile_data):
                    upgrade_list[id] = [cur_lvl]
                    upgrade_list[id].append(cost["rate"])
                else:
                    continue
            else:
                upgrade_list[id] = [cur_lvl]
                upgrade_list[id].append(cost["rate"])

            logger.info(
                f"{self.session_name} | "
                f"Build <ly>{name}</ly>[<le>{cur_lvl}</le>] i can buy. "
                f"Cost: <lc>{cost['shares']}</lc> "
                f"Block: <lm>{cost['blocks']}</lm> "
                f"Video: <lw>{cost['videos']}</lw> "
                f"Required: <lr>{r_name}</lr>[<le>{r_lvl}</le>] "
                f"<lc>{cost['rate']}</lc><lw>/</lw>h"
            )

    # Выберем лучшее здание с наименьшим уровнем
    while True:
        await_time = builders_free(self, profile_data)
        if await_time > 0:
            logger.info(f"{self.session_name} | Waiting builders time <lw>{await_time:,}s</lw>")

            return False

        id_best = ""
        lvl_min = 100

        # Если список зданий для апгрейда пуст
        if not len(upgrade_list):
            return False

        for id, res in upgrade_list.items():
            if lvl_min > res[0]:
                id_best = id
                lvl_min = res[0]

        if id_best == "":
            break

        logger.success(
            f"{self.session_name} | "
            f"<g>Start update build</g> <y>{b_name[id_best]}</y> "
            f"to level <c>{lvl_min + 1}</c>"
        )

        status = await update_build(http_client=http_client, b_id=id_best)
        if "player" in status:
            # Обновим инфу о пользователе если есть ключ player
            profile_data.update(status)
            del upgrade_list[id_best]
            logger.success(f"{self.session_name} | <g>Update</g> <y>{b_name[id_best]}</y> is check server.")
            await asyncio.sleep(delay=15)

            return True

        elif status == "building_already_upgrading":
            logger.warning(f"{self.session_name} | Building already upgrading. Construction is wait.")
            await asyncio.sleep(delay=15)

            return True
        elif status == "no_available_builders":
            logger.warning(f"{self.session_name} | No available builders. Construction is wait.")
            await asyncio.sleep(delay=15)

            return False
        elif status == "required_building_level_too_low":
            logger.warning(f"{self.session_name} | Required building level too low. Construction is wait.")
            await asyncio.sleep(delay=15)

            return False
        elif status == "not_enough_videos":
            logger.warning(f"{self.session_name} | Not resource Videos. Construction is wait.")
            await asyncio.sleep(delay=15)

            return False
        elif status == "not_enough_shares":
            logger.warning(f"{self.session_name} | Not resource Coins. Construction is wait.")
            await asyncio.sleep(delay=15)

            return False
        elif status == "Unauthorized":
            logger.warning(f"{self.session_name} | Unauthorized. Construction is stop.")
            await asyncio.sleep(delay=5)

            return False
        elif status == "tg_channel_check_failed":
            logger.warning(f"{self.session_name} | TG channel check subscribe failed. Construction is wait.")
            await asyncio.sleep(delay=5)

            await subscribe_channel_task(self)
            await social_channel_task(self, http_client)

            return False
        else:
            logger.error(
                f'{self.session_name} | Unknown error when Update build. Return status: "{status}"'
            )
            await asyncio.sleep(delay=5)
            break

    return False


# Функция возвращает перечень ресурсов для апдейта
def build_new_level(b_id, profile_data) -> dict:
    data = {"id": b_id}

    i = int(b_id.removeprefix("b_")) - 1  # вычислим индекс из id здания

    levels = profile_data["conf"]["town"]["buildings"][i]["levels"][2]

    if levels is None:
        return None

    data.update(levels["cost"])

    # добыча блоков на новом уровне шт/час
    data["rate"] = int(levels["rate"] * 3600)
    req = levels.get("required")  # требование наличие уровня другого здания
    if req:
        data["r_id"] = req.get("id")
        data["r_level"] = req.get("level")
    else:
        data["r_id"] = None
        data["r_level"] = None

    return data


# Функция возвращает текущий уровень здания по его id
def build_current_level(b_id, profile_data) -> int:
    for data in profile_data["player"]["town"]["buildings"]:
        if b_id == data["id"]:
            # Проверка, что уровень уже построен если нет понижаем
            if data["ready_at"] / 1000 > time():
                return data["level"] - 1
            else:
                return data["level"]
    return 0


# Функция возвращает минимально время освобождения строителя
# Вызывать лучше всего после обновления challenge
# Возвращает 0 если хотя бы есть один свободный
def builders_free(self, profile_data) -> int:
    global b_name

    await_time = 0
    player_time = profile_data["player"]["time"]
    builds_stat = profile_data["player"]["town"]["buildings"]
    count_builders = 0
    for build in builds_stat:
        # Время ожидания до окончания стройки
        time_at = build["ready_at"] - player_time
        if time_at > 0:
            count_builders += 1

            if await_time == 0:
                await_time = time_at
            elif await_time > time_at:
                await_time = time_at

            logger.info(
                f"{self.session_name} | "
                f"Build <y>{b_name[build['id']]}</y> "
                f"wait <c>{int(time_at / 1000):,}</c> sec..."
            )

            # Заняты все строители, вернем время освобождения первого
            if count_builders >= profile_data["player"]["town"]["builders"]:
                logger.warning(
                    f"{self.session_name} | <r>All the builders are busy...</r>"
                )
                return int(await_time / 1000)

    logger.success(f"{self.session_name} | <lg>Excellent, there is a free builder!</lg>")

    return 0


# Подписка на каналы
async def subscribe_channel_task(self):
    async with self.tg_client:
        self.user_id = (await self.tg_client.get_me()).id
        await asyncio.sleep(delay=5)

        channels_id = ["tapswapai"]

        for channel_id in channels_id:
            try:
                member = await self.tg_client.get_chat_member(channel_id, self.user_id)
                if member.status not in ["member", "administrator", "creator"]:
                    await self.tg_client.join_chat(channel_id)

                    logger.info(f"{self.tg_client.name} | You are already subscribed to the channel @{channel_id}")
                    await asyncio.sleep(delay=5)
            except UserNotParticipant:
                await self.tg_client.join_chat(channel_id)

                logger.info(f"{self.tg_client.name} | Subscribe channel @{channel_id} for task")
                await asyncio.sleep(delay=5)


async def social_channel_task(self, http_client):
    finish_mission_item = int(await self.finish_mission_item(self, http_client, "M0", "check", 0))
    await asyncio.sleep(delay=5)

    finish_mission_item += await self.finish_mission_item(self, http_client, "M0", "check", 1)
    await asyncio.sleep(delay=5)

    finish_mission_item += await self.finish_mission_item(self, http_client, "M0", "check", 2)
    await asyncio.sleep(delay=5)

    finish_mission = await self.finish_mission(self, http_client, "M0")
    await asyncio.sleep(delay=5)

    if finish_mission and finish_mission_item == 3:
        await self.claim_reward(self, http_client, "M0")
