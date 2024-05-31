# Pokerogue OCR Assistant (POCRA)
Tired of looking up Pokemon and their abilities or consulting a type effectiveness chart? POCRA scans your screen, recognizes the Pokemon you're fighting, and automatically opens the 
Ydarissep Pokedex page for that Pokemon. 
## Usage
After opening the application, two windows will appear: one will be Ydarissep's PokeRogue Pokedex (using their version online [here](https://ydarissep.github.io/PokeRogue-Pokedex))
and one will be the application interface. Position these however you like; this is how I personally position them:

![image](https://github.com/ruan-xian/POCRA/assets/55116848/6281f97e-ca54-40eb-8304-4a1a9b21d17c)

To begin, press the "Set OCR area" button. Drag and resize the window that opens over the area you want to scan for text, then close the window to set the scanned area.
This is where I usually position the window so that both Pokemon are detected in a double battle:

![image](https://github.com/ruan-xian/POCRA/assets/55116848/c56b3521-c4fc-4fe0-8679-e386d133bc8b)

The app will now automatically start to scan the selected area for Pokemon names. If the "Auto-open Pokedex" option is enabled (as it is by default), the Ydarissep Pokedex page
will attempt to automatically search for and open that Pokedex entry.

![image](https://github.com/ruan-xian/POCRA/assets/55116848/e1f1845a-a50e-479a-aecb-961b34514c75)

You may also click the detected Pokemon in the Detection Results box at any time to open its Pokedex entry and bring the Pokedex page to the top. In a double battle, the first 
Pokemon will have its Pokedex entry automatically opened, but you can switch to the other Pokemon by clicking its corresponding button in the Detection Results box.

![image](https://github.com/ruan-xian/POCRA/assets/55116848/33f2dbe5-40a2-4cf4-a9b3-5b586d24eb3b)

## Customization
If the OCR is not particularly accurate for your resolution or graphical settings, you can attempt to fine-tune the image preprocessing to try to improve your results.
Clicking "Preprocessing settings" will open a series of options:
- Invert OCR text color: By default, this app expects light text on a dark background. If you are playing on the Legacy UI theme (dark text on a light background), you should check this box.
- Threshold: A number from 0 to 255 representing the brightness level at which the image will be separated into black or white pixels. Likely OK to leave it at its default setting;
note that if you use the invert option, the threshold should be different.
- Resize factor: I play on a 2560x1080 monitor. Depending on the size of your game screen, you may want to increase or decrease the resize factor (increase the factor if your screen is smaller).
- Blur size: How much blur to apply to the image. Probably OK at 0, but the option is here for legacy purposes.
- Minfilter size: How much to "thicken" the pixels in the image. This has a large effect on the resulting text detection quality.
- Preview image: View an annotated screenshot showing what the application "sees" and what it interpreted the output as, according to the current preprocessing settings.
## Blacklisting
POCRA supports a user blacklist to exclude terms from being recognized as valid Pokemon. This is useful when you don't want to, for example, recognize Pokemon in your team, or a term commonly gets interpreted as a Pokemon when it is not (like S.ATK being read as Sawk). You can press the "Blacklist" button under a Pokemon's button in the Detection Results box to add that Pokemon's name to the blacklist (*not* the recognized text), or you can press "Edit Blacklist" to manually edit the blacklist. Enter your terms one per line.

After the blacklist is set, any text that matches a blacklist term as well as (or better than) any Pokemon will be discarded. 
## Other notes
- All settings are saved when the app is exited in `pocra_settings.json`
- POCRA may fail to recognize or open the proper pages for mega evolutions and gigantamax Pokemon
- POCRA will not account for regional variations
- An internet connection *is* required to use POCRA (to load the Pokedex page)

