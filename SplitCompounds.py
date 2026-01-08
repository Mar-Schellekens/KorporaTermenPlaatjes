from itertools import permutations
from Utils import add_base_path

wordlist = add_base_path("wordlist.txt")
wordlist_user = add_base_path("wordlist_user.txt")
with open(wordlist, "r", encoding="utf-8") as f:
    dictionary = f.read()
    dictionary = dictionary.split("\n")
with open(wordlist_user, "r", encoding="utf-8") as f:
    dictionary_user = f.read()
    dictionary.extend(dictionary_user.split("\n"))

def is_dutch_word(word):
    if word in dictionary:
        return True
    else:
        return False

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

def split_compounds(word, font, max_width):
    final_compounds = []
    rest_of_word = [word]
    while len(rest_of_word) != 0:
        compounds = []
        for parts in rest_of_word:
            compounds.extend(get_all_possible_compounds(parts))

        if len(compounds) == 0:
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

    compounds = fix_order(word, final_compounds)

    "Fix tussen s"
    if 's' in compounds:
        idx = compounds.index('s')
        if idx != 0:
            compounds.remove('s')
            compounds[idx-1] += 's'



    return compounds




