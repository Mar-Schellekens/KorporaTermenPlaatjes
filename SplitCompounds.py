import os
import sys
from itertools import permutations

import pyphen
from wordfreq import zipf_frequency

#dictionary = pyphen.Pyphen(lang='nl_NL')
base = os.path.dirname(sys.executable)
with open(os.path.join(base, "wordlist.txt"), "r", encoding="utf-8") as f:
    dictionary = f.read()
    dictionary = dictionary.split("\n")
with open(os.path.join(base, "wordlist_user.txt"), "r", encoding="utf-8") as f:
    dictionary_user = f.read()
    dictionary.extend(dictionary_user.split("\n"))

def is_dutch_word(word):
    if word in dictionary:
        return True
    else:
        return False

# def is_dutch_word(word, threshold=2):
#     if "/" in word:
#         return False
#     """
#     Check if a word exists in Dutch using its frequency score.
#     threshold: higher -> stricter (only common words)
#     """
#     return zipf_frequency(word, "nl") >= threshold


word = "Alarmeringsapparatuur"

def get_all_possible_compounds(word):
    letters = list(word)
    compounds = []
    for index_start in range(0, len(letters)):
        for index_end in range(index_start + 1, len(letters)+1):
            possible_compound = "".join(letters[index_start:index_end])
            if is_dutch_word(possible_compound):
                compounds.append(possible_compound)
    return compounds


def fix_order(word, chunks):
    for perm in permutations(chunks):
        if "".join(perm) == word:
            return list(perm)
    return None  # no matching permutation

def check_tussen_s(word, possible_compounds, test_compound):
    if test_compound[0] == 's' and is_dutch_word(test_compound[1:]) and len(test_compound[1:]) > 3:
        parts = word.split(test_compound)
        parts= [s for s in parts if s]
        parts.append(test_compound)
        parts = fix_order(word, parts)
        idx = parts.index(test_compound)
        if idx > 0:
            if parts[idx - 1][-1] != 's':
                return test_compound[1:]
    return test_compound



    # for idx, compound in enumerate(compounds):
    #     if compound[0] == 's':
    #         if is_dutch_word(compound[1:]) and idx > 0 and compounds[idx - 1][-1] != 's':
    #             compounds[idx-1] += ('s')
    #             compounds[idx] = compounds[idx][1:]

def split_compounds(word, font, max_width):
    final_compounds = []
    #compounds = get_all_possible_compounds(word)
    finishedFindingCompounds = False
    rest_of_word = [word]
    while len(rest_of_word) != 0:
        compounds = []
        for parts in rest_of_word:
            compounds.extend(get_all_possible_compounds(parts))

        if len(compounds) == 0:
            #final_compounds.append(*rest_of_word)
            final_compounds.extend(rest_of_word)
            break

        sorted_compounds = sorted(compounds, key=len, reverse=True)
        longest_compound = ""
        for compound in sorted_compounds:
            compound = check_tussen_s(word, compounds, compound)
            width = font.getlength(compound+'-'+ 's') #We doen stiekem alsof er altijd een tussen s tussenkomt. Lelijke hack
            if width < max_width:
                longest_compound = compound
                break

        final_compounds.append(longest_compound)
        rest_of_word_new = []
        for idx, part in enumerate(rest_of_word):
            found_compound_removed = part.split(longest_compound)
            for part2 in found_compound_removed:
                if part2:
                    rest_of_word_new.append(part2)

        rest_of_word = rest_of_word_new
        #rest_of_word = rest_of_word.split(longest_compound)
        #rest_of_word = rest_of_word.replace(longest_compound, "")

    compounds = fix_order(word, final_compounds)

    "Fix tussen s"
    if 's' in compounds:
        idx = compounds.index('s')
        if idx != 0:
            compounds.remove('s')
            compounds[idx-1] += 's'



    return compounds




