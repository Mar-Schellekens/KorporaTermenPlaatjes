import asyncio
import os
from PIL import Image, ImageDraw, ImageFont

import Constants
from Constants import CfgFields
from Term import Term
import SplitCompounds
from Utils import add_base_path


def find_optimal_split_from_chunks(chunks, font, max_width):
    final_split = []
    current = ""
    for chunk in chunks:
        text = current + chunk
        text_width = font.getlength(text + "-")
        if text_width > max_width:
            if current:
                final_split.append(current)
            current = chunk
        else:
            current = text
    if current:
        final_split.append(current)
    return final_split

def capitalize_each_word(text):
    words = text.split()
    for word_index, word in enumerate(words):
        for letter_index, letter in enumerate(word):
            if letter.isalpha():
                words[word_index] = capitalize_current_letter(word, letter_index)
                break
    return ' '.join(words)

def capitalize_current_letter(word, letter_index):
    return word[:letter_index] + word[letter_index].upper() + word[letter_index + 1:]

def split_in_two_lines_by_words(words, draw, font, max_text_width):
    text_width = 0
    newline_1 = ""
    newline_2 = ""

    for idx, word in enumerate(words):
        left, top, right, bottom = draw.textbbox((0, 0), newline_1 + word, font=font)
        word_width = right - left
        text_width += word_width
        if text_width > max_text_width:
            newline_2 = " ".join(words[idx:])
            return newline_1, newline_2
        newline_1 += word

    return newline_1, newline_2

def add_dash_to_split_compounds(compounds):
    return [item + '-' for item in compounds[:-1]]

def add_left_over_words_back_to_compounds(compounds, words):
    compounds[-1] += " " + " ".join(words[1:])
    return compounds

def split_text(draw, line, font, max_text_width, lines):
    words = line.split()
    left, top, right, bottom = draw.textbbox((0, 0), words[0], font=font)
    text_width_first_word = right - left
    if len(words) > 1 and text_width_first_word <= max_text_width:
        new_splits = split_in_two_lines_by_words(words, draw, font, max_text_width)
    else:
        compounds = SplitCompounds.split_chunks(words[0], font, max_text_width)
        compounds = find_optimal_split_from_chunks(compounds, font, max_text_width)
        compounds[0:-1] = add_dash_to_split_compounds(compounds)
        if len(words) > 1:
            new_splits = add_left_over_words_back_to_compounds(compounds, words)
        else:
            new_splits = compounds

    idx = lines.index(line)
    lines[idx:idx + 1] = new_splits
    return lines

def reached_last_line(line, lines):
    idx = lines.index(line)
    return idx == len(lines) - 1

def draw_text(cfg, text, draw, font):
    max_text_width = cfg[CfgFields.WIDTH.value] - (cfg[CfgFields.MARGIN.value] * 2)
    capitalized_text = capitalize_each_word(text)

    lines = [capitalized_text]
    reachedLastLine = False
    while not reachedLastLine:
        for line in lines:
            left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
            text_width = right - left
            if text_width > max_text_width:
                lines = split_text(draw, line, font, max_text_width, lines)
                break

            reachedLastLine = reached_last_line(line, lines)

    text = "\n".join(lines)
    return text

async def create_picture_async(term, style_cfg):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, create_picture, term, style_cfg)

def create_picture(term:Term, cfg):
    imageFormat = Image.new("RGB", (cfg[CfgFields.WIDTH.value], cfg[CfgFields.HEIGHT.value]), cfg[CfgFields.BACKGROUND_COLOR.value])
    image = ImageDraw.Draw(imageFormat)

    # Load default font or a TTF font if available
    try:
        font = ImageFont.truetype(cfg[CfgFields.FONT.value], cfg[CfgFields.FONT_SIZE.value])
    except IOError:
        print(f"Font {cfg[CfgFields.FONT.value]} niet gevonden. Gebruik standaard font in plaats daarvan.")
        font = ImageFont.truetype("DejaVuSans.ttf", cfg[CfgFields.FONT_SIZE.value])


    text = draw_text(cfg, term.text, image, font)

    x = cfg["width"]/2
    y=cfg["height"]/2
    image.multiline_text((x, y), text, fill=term.text_color, font=font, anchor="mm", align="center")

    # Save as JPG
    image_folder = add_base_path(Constants.OUTPUT_FOLDER)
    filename = term.text.replace("/", "_").replace("?", "_")
    imageFormat.save(os.path.join(image_folder, filename) + ".jpg", "JPEG")

