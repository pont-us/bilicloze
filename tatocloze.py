#!/usr/bin/env python3

import wordfreq
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sentence_file", type=str)
    args = parser.parse_args()

    sentence_map = {}
    # word_map = {}
    
    with open(args.sentence_file) as fh:
        while True:
            line = fh.readline()
            if line == "":
                break
            sentence_l1, sentence_l2 = line.strip().split("\t")
            if sentence_l2 not in sentence_map:
                sentence_map[sentence_l2] = []
            sentence_map[sentence_l2].append(sentence_l1)

    top_n_words = wordfreq.top_n_list("fi", 100)

    for word in top_n_words:
        for sentence_l2 in sentence_map:
            if word in sentence_l2:
                cloze = sentence_l2.replace(word, "####")
                print(cloze, sentence_map[sentence_l2][0], word)
                break

if __name__ == "__main__":
    main()
