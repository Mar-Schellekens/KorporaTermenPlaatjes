import asyncio
import os
import re
import sys
from random import random
from time import sleep

from PIL import Image, ImageDraw, ImageFont
import pyphen

from Singleton import app
from Term import Term
import string
from wordfreq import zipf_frequency
import SplitCompounds
from Utils import add_base_path

dictionary = pyphen.Pyphen(lang='nl_NL')
# --- Configuration ---
# width, height = 591, 591          # image size
# background_color = (230, 230, 230)  # gray background (R, G, B)
# font_size = 64           # text size
# margin = 30
# max_text_width = width-margin*2
output_path = "images/"  # output file name

def find_max_split_from_chunks(chunks, fnt, max_width):
    final_split = []
    current = ""
    for syl in chunks:
        test = current + syl
        width = fnt.getlength(test + "-")
        if width > max_width:
            if current:
                final_split.append(current)
            current = syl
        else:
            current = test
    if current:
        final_split.append(current)
    return final_split


def split_up_syllables(line, font, max_text_width):
    syllables = dictionary.inserted(line).split('-')
    chunks = find_max_split_from_chunks(syllables, font, max_text_width)
    for chunk in chunks[:-1]:
        idx = chunks.index(chunk)
        chunks[idx] += "-"
    return chunks

def smart_capitalize(text):
    words = text.split()
    for j, w in enumerate(words):
        for i, letter in enumerate(w):
            if letter in ['(', ')']:
                continue
            words[j] = w[:i] + w[i].upper() + w[i+1:]
            break
    return ' '.join(words)


    return ' '.join(
        w[0].upper() + w[1:] for w in words
    )


async def create_picture_test(term, style_cfg, app):
    #sleep(random()*10)
    await asyncio.sleep(random() * 10)
    await app.increment()

def split_up_term(cfg, term, draw, font):
    max_text_width = cfg["width"] - (cfg["margin"] * 2)
    lines = [smart_capitalize(term.text)]
    reachedLastLine = False
    while not reachedLastLine:
        for line in lines:
            left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
            text_width = right - left
            if text_width > max_text_width:
                words = line.split()
                # words = re.split(r'([ /])', line)
                # parts = re.findall(r'/[^/\s]+|[^/\s]+', line)
                # Separate chunks and separators
                # words = parts[::2]  # every even index → text
                # separators = parts[1::2]  # every odd index → separator

                left, top, right, bottom = draw.textbbox((0, 0), words[0], font=font)
                if len(words) > 1 and (right - left) <= max_text_width:  # if line contains multiple words
                    text_width = 0
                    newline_1 = ""
                    newline_2 = ""
                    for word in words:
                        left, top, right, bottom = draw.textbbox((0, 0), newline_1 + word, font=font)
                        text_width = text_width + (right - left)
                        if text_width > max_text_width:
                            idx = words.index(word)
                            newline_2 = " ".join(words[idx:])
                            # newline_2 = "".join([s + c for c, s in zip(words[1:], separators + [""])])
                            break
                        if newline_1:
                            newline_1 += " "
                        newline_1 += word
                    idx = lines.index(line)
                    lines[idx:idx + 1] = [newline_1, newline_2]
                    break
                else:
                    words = line.split(" ")
                    # words = re.split(r'[ /]', line)
                    compounds = SplitCompounds.split_compounds(words[0], font, max_text_width)
                    compounds = find_max_split_from_chunks(compounds, font, max_text_width)
                    compounds[0:-1] = [item + '-' for item in compounds[0:-1]]
                    if (len(words) > 1):
                        compounds[-1] += " " + " ".join(words[1:])
                    # chunks = split_up_syllables(line, font, max_text_width)
                    idx = lines.index(line)
                    # lines[idx:idx+1] = chunks
                    lines[idx:idx + 1] = compounds
                    break
            idx = lines.index(line)
            if idx == len(lines) - 1:
                reachedLastLine = True

    text = "\n".join(lines)

def split_up_term_test(cfg, term, draw, font):
    max_text_width = cfg["width"] - (cfg["margin"] * 2)
    lines = [smart_capitalize(term.text)]
    reachedLastLine = False
    while not reachedLastLine:
        for line in lines:
            left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
            text_width = right - left
            if text_width > max_text_width:
                words = line.split()

                left, top, right, bottom = draw.textbbox((0, 0), words[0], font=font)
                if len(words) > 1 and (right - left) <= max_text_width:  # if line contains multiple words
                    text_width = 0
                    newline_1 = ""
                    newline_2 = ""
                    for word in words:
                        left, top, right, bottom = draw.textbbox((0, 0), newline_1 + word, font=font)
                        text_width = text_width + (right - left)
                        if text_width > max_text_width:
                            idx = words.index(word)
                            newline_2 = " ".join(words[idx:])
                            break
                        if newline_1:
                            newline_1 += " "
                        newline_1 += word
                    idx = lines.index(line)
                    lines[idx:idx + 1] = [newline_1, newline_2]
                    break
                else:
                    words = line.split(" ")
                    compounds = SplitCompounds.split_compounds(words[0], font, max_text_width)
                    compounds = find_max_split_from_chunks(compounds, font, max_text_width)
                    compounds[0:-1] = [item + '-' for item in compounds[0:-1]]
                    if (len(words) > 1):
                        compounds[-1] += " " + " ".join(words[1:])
                    idx = lines.index(line)
                    lines[idx:idx + 1] = compounds
                    break
            idx = lines.index(line)
            if idx == len(lines) - 1:
                reachedLastLine = True

    text = "\n".join(lines)
    return text

def create_picture(term:Term, style_cfg, app):
    #await asyncio.sleep(random())
    cfg = style_cfg

    # --- Create image ---
    image = Image.new("RGB", (cfg["width"], cfg["height"]), cfg["background_color"])
    draw = ImageDraw.Draw(image)

    # Load default font or a TTF font if available
    try:
        font = ImageFont.truetype(cfg["font"], cfg["font_size"])
    except IOError:
        print(f"Font {cfg['font']} niet gevonden. Gebruik standaard font in plaats daarvan.")
        font = ImageFont.truetype("DejaVuSans.ttf", cfg["font_size"])


    text = split_up_term_test(cfg, term, draw, font)

    x = cfg["width"]/2
    y=cfg["height"]/2
    draw.multiline_text((x, y), text, fill=term.text_color, font=font, anchor="mm", align="center")

    # Save as JPG
    image_folder = add_base_path(output_path)
    filename = term.text.replace("/", "_").replace("?", "_")
    image.save(os.path.join(image_folder, filename) + ".jpg", "JPEG")
    #app.get().ui.setMessage(f"Image saved as {output_path+filename + ".jpg"}")
    #print(f"Image saved as {output_path+filename + ".jpg"}")

