#!/usr/bin/env python3

from collections import OrderedDict
from typing import List
import re
import wordfreq
import argparse

def main():
    make_clozes(100, 5, 5, 80)


def make_clozes(nwords, max_sentences_per_word,
                max_translations_per_sentence,
                max_characters):
    parser = argparse.ArgumentParser()
    parser.add_argument("sentence_file", type=str)
    args = parser.parse_args()

    sentence_map = OrderedDict()
    word_map = {}
    
    with open(args.sentence_file) as fh:
        while True:
            line = fh.readline()
            if line == "":
                break
            sentence_l1, sentence_l2 = line.strip().split("\t")
            if sentence_l2 not in sentence_map:
                sentence_map[sentence_l2] = []
            sentence_map[sentence_l2].append(sentence_l1)
            words = sentence_to_words(sentence_l2)
            for word in words:
                if word not in word_map:
                    # We use an OrderedDict as an ordered set, since the
                    # Python standard library lacks the latter.
                    word_map[word] = OrderedDict()
                if sentence_l2 not in word_map[word]:
                    word_map[word][sentence_l2] = None

    top_n_words = wordfreq.top_n_list("fi", nwords)

    for word in top_n_words:
        if word in word_map:
            sentences_l2 = list(word_map[word])[:max_sentences_per_word]
            for sentence_l2 in sentences_l2:
                translation_list = \
                    sentence_map[sentence_l2][:max_translations_per_sentence]
                cloze = clozify(sentence_l2, word, "{{c1::%s}}" % word)
                translations = " / ".join(translation_list)
                if len(cloze) <= max_characters and \
                   len(translations) <= max_characters:
                    print("<p>%s</p><p>%s</p>" % (cloze, translations))


def clozify(sentence, word, cloze_marker):
    """Make a cloze out of a sentence.

    >>> clozify("I battered the bat.", "bat", "####")
    'I battered the ####.'
    >>> clozify("A fat pig is a happy pig.", "pig", "??")
    'A fat ?? is a happy ??.'
    >>> clozify("This isn't too hard.", "isn't", "___")
    'This ___ too hard.'
    >>> clozify("It wasn't, alas, correct.", "wasn't", "___")
    'It ___, alas, correct.'
    >>> clozify("First things first.", "first", "---")
    '--- things ---.'
    """

    return re.subn(r"(^\W*| \W*)" + word + r"(\W* |\W*$)",
                   r"\1" + cloze_marker + r"\2",
                   sentence,
                   flags=re.IGNORECASE)[0]


def sentence_to_words(sentence: str) -> List[str]:
    """Put a string in lower case and remove punctuation between words.

    >>> sentence_to_words("Today, they aren't up-to-date any more.")
    ['today', 'they', "aren't", 'up-to-date', 'any', 'more']
    """
    return list(map(clean_word, sentence.split(" ")))


def clean_word(word: str) -> str:
    """Put a string in lower case and remove surrounding punctuation.

    >>> clean_word("Won't!")
    "won't"
    >>> clean_word("Full-time,")
    'full-time'
    """
    return re.sub(r"^[,.'\"()!]+", "",
                  re.sub(r"[,.'\"()!]+$", "", word.lower()))

            
if __name__ == "__main__":
    main()
