from PIL import ImageGrab
import time
import requests
from pynput.keyboard import Key, Controller
import pyautogui
import pygetwindow as gw
import pytesseract
import difflib
from modules.console import console

class ShinyHunter:
    def __init__(self, pokemonList, checkPixels, compareColor, windowTitle):
        self.pokemonList = pokemonList
        self.checkPixels = checkPixels
        self.compareColor = compareColor
        self.keyboard = Controller()
        self.checkConst = 5
        self.windowTitle = windowTitle
        self.window = None

        if not (len(self.pokemonList) == len(self.checkPixels) == len(self.compareColor)):
            print("Error: pokemonList, checkPixels, and compareColor must have the same length.")
            quit()

    def checkForShiny(self):
        if not self.window:
            windows = gw.getAllWindows()
            windows = [window for window in windows if 'Test' in window.title]
            for window in windows:
                if '|' in window.title:
                    title = window.title.split('|')[0].strip()
                if self.windowTitle and self.windowTitle == title:
                    self.window = window
                    break
            if not self.window:
                console.log(f"Window with title '{self.windowTitle}' not found.")
                return False
        ourWindow = self.window
        x, y = ourWindow.topleft
        width, height = ourWindow.size
        # program is offset from what gw actually returns
        x += 10
        height -= 10
        width -= 20
        # only grab the pokemon nameplate to reduce tesseract load time
        region = (20, 70, 220, 150)
        image = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        w, h = image.size
        window_image = image.crop(region)
        # window_image.show()
        text = pytesseract.image_to_string(window_image)

        found_pokemon = None
        for index, pokemon in enumerate(self.pokemonList):
            # print(f"Checking for {pokemon.capitalize()} in text:", text)
            close_matches = difflib.get_close_matches(pokemon.lower(), text.lower().split(), n=1, cutoff=0.6)
            if close_matches:
                # print(f"{pokemon.capitalize()} found in text:", text)
                found_pokemon = (pokemon, index)
                break
        if not found_pokemon:
            console.log("No target pokemon found in text:", text)
            return

        console.log(f"Checking for {found_pokemon[0].capitalize()} in window {self.windowTitle}")
        check = (self.checkPixels[found_pokemon[1]][0], self.checkPixels[found_pokemon[1]][1])
        pixel = image.getpixel((check[0], check[1]))

        # uncomment to get a window of the check pixel, it will be the top left pixel.
        # just needs to at least be on the pokemon, so we can know if it's shiny or not
        # (assuming that 1 pixel will change if its shiny)
        # print(pixel, check)
        # region = (check[0], check[1], check[0]+70, check[1]+70)
        # window_image = image.crop(region)
        # window_image.show()

        # check if any of the 3 rgb values are different than the compareColor by 5 values (indicates shiny)
        if any(abs(pixel[i] - self.compareColor[found_pokemon[1]][i]) >= self.checkConst for i in range(3)):
            console.log(f"Shiny {found_pokemon[0].capitalize()} found!")
            region = (max(0, check[0] - 70), max(0, check[1] - 70), min(w, check[0] + 70), min(h, check[1] + 70))
            shiny_image = image.crop(region)
            shiny_image.save("shiny.png")
            with open("shiny.png", "rb") as f:
                requests.post(
                    "https://discord.com/api/webhooks/1317348223609868298/AdZqwW0O-hbMAQG4puOiPzKSiZCUDQv70R-sYNjV8Clhxj5iUSGfHerKp4M2CX7NoIdu",
                    files={"file": f},
                    data={"content": f"Shiny {found_pokemon[0].capitalize()} Found!" + f" in window {self.windowTitle}"}
                )
            return True
        return False


pokemonList = ['lotad', 'ralts', 'wurmple', 'poochyena', 'zigzagoon', 'seedot']
# pixel to check for shiny
checkPixels = [(360, 175), (350, 148), (350, 148), (350, 148), (350, 148), (360, 165)]
# color to compare against for shiny
compareColor = [(49, 115, 148), (206, 255, 173), (247, 123, 99), (198, 189, 206), (206, 156, 123), (156, 90, 49)]

# shiny_hunter = ShinyHunter(pokemonList, checkPixels, compareColor, "Test")
# shiny_hunter.checkForShiny()
# while True:
#     roto(pokemonList, checkPixels, compareColor)
