from itertools import permutations

from Exceptions import TooSmallException
from Utils import add_base_path
from View import View

wordlist = add_base_path("wordlist.txt")
wordlist_user = add_base_path("wordlist_user.txt")
with open(wordlist, encoding="utf-8") as f:
    dictionary = set(line.strip() for line in f if line.strip())
with open(wordlist_user, encoding="utf-8") as f:
    dictionary.update(line.strip() for line in f if line.strip())

def is_dutch_word(word):
    return word in dictionary

def get_all_possible_chunks(word):
    compounds = set()
    for start in range(len(word)):
        for end in range(start + 1, len(word) + 1):
            sub = word[start:end]
            if is_dutch_word(sub):
                compounds.add(sub)
    return list(compounds)

def fix_order(word, chunks):
    for perm in permutations(chunks):
        if "".join(perm) == word:
            return list(perm)
    return None

def remove_empty_strings(chunks):
    return [chunk for chunk in chunks if chunk]

def fix_tussen_s(chunks):
    fixed_chunks = chunks[:]
    for i, chunk in enumerate(chunks[1:], start=1):
        if chunk.startswith('s') and len(chunk) > 3 and is_dutch_word(chunk[1:]):
            fixed_chunks[i] = chunk[1:]
            fixed_chunks[i-1] += 's'
    return fixed_chunks

def split_chunks(word, font, max_width):
    all_possible_chunks = get_all_possible_chunks(word)
    sorted_chunks = sorted(all_possible_chunks, key=len, reverse=True)

    longest_possible_compound = ""
    for compound in sorted_chunks:
        width = font.getlength(compound+'-'+ 's') #We doen stiekem alsof er altijd een tussen s tussenkomt. Lelijke hack
        if width < max_width:
            longest_possible_compound = compound
            break

    if longest_possible_compound == "":
        raise TooSmallException("De geconfigureerde breedte is te klein! Vergroot de breedte, of verklein de tekstgrootte of marge")

    chunks = [longest_possible_compound]
    chunks.extend(word.split(longest_possible_compound))
    chunks = fix_order(word, chunks)
    chunks = remove_empty_strings(chunks)

    chunks = fix_tussen_s(chunks)

    return chunks




