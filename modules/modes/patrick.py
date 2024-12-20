import random
import keyboard
from typing import Generator

from modules.context import context
from modules.encounter import handle_encounter, EncounterInfo
from modules.gui.multi_select_window import Selection, ask_for_choice
from modules.map_data import MapFRLG, MapRSE
from modules.menuing import PokemonPartyMenuNavigator, StartMenuNavigator
from modules.modes.util.walking import navigate_to
from modules.player import get_player_avatar
from modules.pokemon_party import get_party_size, get_party
from modules.runtime import get_sprites_path
from modules.save_data import get_save_data
from modules.console import console
from ._asserts import SavedMapLocation, assert_save_game_exists, assert_saved_on_map
from time import sleep
from ._interface import BattleAction, BotMode, BotModeError
from .util import (
    ensure_facing_direction,
    soft_reset,
    wait_for_n_frames,
    wait_for_task_to_start_and_finish,
    wait_for_unique_rng_value,
    wait_until_task_is_active,
    wait_until_task_is_not_active,
)
from ..battle_state import get_main_battle_callback, EncounterType
from ..image import ShinyHunter

def spin(direction, times) -> Generator:
    if (direction == 'L'):
        direction1 = "Left"
        direction2 = "Right"
    elif (direction == 'U'):
        direction1 = "Up"
        direction2 = "Down"

    for i in range(times):
        context.emulator.press_button(direction1)
        yield from wait_for_n_frames(10)
        context.emulator.press_button(direction2)
        yield from wait_for_n_frames(10)

def reset() -> Generator:
    for i in range(20):
        context.emulator.press_button("B")
        yield from wait_for_n_frames(10)
    context.emulator.press_button("Left")
    yield from wait_for_n_frames(10)
    context.emulator.press_button("Up")
    random_wait = random.randint(5, 20)
    yield from wait_for_n_frames(random_wait)
    
def battle(self) -> Generator:
    yield from wait_for_n_frames(120)
    context.emulator.press_button("A")
    yield from wait_for_n_frames(240)
    yield from reset()
    shiny = self.hunter.checkForShiny()
    if shiny:
        if (self.doNotStop):
            context.emulator.create_save_state("Manual")
            yield from wait_for_n_frames(120)
        else: 
            context.bot_mode = "Manual"
            context.emulation_speed = 1
            return
    context.emulator.press_button("Right")
    yield from wait_for_n_frames(10)
    context.emulator.press_button("Down")
    yield from wait_for_n_frames(10)
    context.emulator.press_button("A")
    yield from wait_for_n_frames(120)
    context.emulator.press_button("A")

def run_patrick(self) -> Generator:
    profileTitle = str(context.profile.path).split("\\")[-1]
    self.hunter = ShinyHunter(self.pokemonList, self.checkPixels, self.compareColor, profileTitle)
    context.emulation_speed = 32
    while context.bot_mode != "Manual":
        yield from spin('L', 45)
        yield from battle(self)

        if context.bot_mode == "Manual":
            return

        yield from spin('U', 45)
        yield from battle(self)

    return
    
class PatrickMode(BotMode):
    pokemonList = ['lotad', 'ralts', 'wurmple', 'poochyena', 'zigzagoon', 'seedot']
    # pixel to check for shiny
    checkPixels = [(360, 175), (350, 148), (350, 148), (350, 148), (350, 148), (360, 165)]
    # color to compare against for shiny
    compareColor = [(49, 115, 148), (206, 255, 173), (247, 123, 99), (198, 189, 206), (206, 156, 123), (156, 90, 49)]
    doNotStop = True
    @staticmethod
    def name() -> str:
        return "Patrick"

    @staticmethod
    def is_selectable() -> bool:
        return True

    def on_battle_started(self, encounter: EncounterInfo | None) -> BattleAction | None:
        return BattleAction.CustomAction

    def run(self) -> Generator:
        yield from run_patrick(self)

