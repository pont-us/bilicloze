#!/usr/bin/env python3

# clgplot is Copyright 2019 Pontus Lurcock (pont@talvi.net) and released
# under the MIT license:

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from collections import OrderedDict
from typing import List
import re
import wordfreq
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Create clozes from a bilingual sentence list.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-w", "--words", type=int,
                        default=100,
                        help="number of words for which to create clozes"),
    parser.add_argument("-s", "--sentences-per-word", type=int,
                        default=5,
                        help="number of L2 sentences to clozify for each word"),
    parser.add_argument("-t", "--translations-per-sentence", type=int,
                        default=5,
                        help="number of L1 translations for each L2 sentence"),
    parser.add_argument("-m", "--max-characters", type=int,
                        default=80,
                        help="maximum characters in sentence or translations")
    parser.add_argument("language", type=str,
                        choices=sorted(wordfreq.available_languages().keys()),
                        help="two-letter language code for L2")
    parser.add_argument("sentence_file", type=str,
                        help="file containing sentence data")
    args = parser.parse_args()
    make_clozes(args.sentence_file, args.language,
                args.words, args.sentences_per_word,
                args.translations_per_sentence, args.max_characters)


def make_clozes(sentence_file, language, nwords, max_sentences_per_word,
                max_translations_per_sentence, max_characters):
    sentence_map = OrderedDict()
    word_map = {}
    
    with open(sentence_file) as fh:
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

    top_n_words = wordfreq.top_n_list(language, nwords)

    for word in top_n_words:
        if word in word_map:
            sentences_l2 = list(word_map[word])[:max_sentences_per_word]
            for sentence_l2 in sentences_l2:
                translation_list = \
                    sentence_map[sentence_l2][:max_translations_per_sentence]
                cloze = make_anki_cloze(sentence_l2, word)
                translations = " / ".join(translation_list)
                if len(cloze) <= max_characters and \
                   len(translations) <= max_characters:
                    print("<p>%s</p><p>%s</p>" % (cloze, translations))


def make_anki_cloze(sentence, word):
    """Make an Anki-formatted cloze out of a sentence.

    >>> make_anki_cloze("I battered the bat.", "bat")
    'I battered the {{c1::bat}}.'
    >>> make_anki_cloze("A fat pig is a happy pig.", "pig")
    'A fat {{c1::pig}} is a happy {{c1::pig}}.'
    >>> make_anki_cloze("This isn't too hard.", "isn't")
    "This {{c1::isn't}} too hard."
    >>> make_anki_cloze("It wasn't, alas, correct.", "wasn't")
    "It {{c1::wasn't}}, alas, correct."
    >>> make_anki_cloze("First things first.", "first")
    '{{c1::First}} things {{c1::first}}.'
    """

    return re.subn(r"(^\W*| \W*)(%s)(\W* |\W*$)" % word,
                   r"\1{{c1::\2}}\3",
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
