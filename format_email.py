#!/usr/bin/python3
#coding:utf-8

from sys import stdin
from queue import Queue

email_line_len = 78

indented_symbol = ">>>>>"

words = []
indented = False
for line in stdin:
    line = line.rstrip()
    l = line.lstrip()
    if len(l) < len(line):
        # there are some space in front of the line
        if not indented:
            words.append(indented_symbol)
        indented = True
        words.append("".join(
            [" " for _ in range(len(line)-len(l))]
            ))
    else:
        if indented:
            words.append(indented_symbol)
            indented = False
        if len(l) == 0:
            words.append("\n")

    words.extend(l.split())

def all_space(word):
    for char in word:
        if not char == " ":
            return False
    return True

current_len = 0
result = []
indented = False
last_indenting_spaces = ""
for word in words:
    if word == "\n":
        current_len = 0
        if result[len(result)-1] != "\n":
            result.append("\n")
        result.append("\n")
        continue

    if all_space(word):
        if not indented:
            if result[len(result)-1] != "\n":
                result.append("\n")
            current_len = 0
            current_len = len(word)
            result.append(word)
            # keep indent distance as the first one
            last_indenting_spaces = word
        indented = True
        continue

    new_word = word + " "
    if current_len + len(new_word) > email_line_len:
        result[len(result)-1] = result[len(result)-1].rstrip()
        result.append("\n")
        current_len = 0
        if indented:
            # still indenting
            result.append(last_indenting_spaces)
            current_len += len(last_indenting_spaces)

    if word == indented_symbol:
        indented = False
    else:
        current_len += len(new_word)
        result.append(new_word)

print("".join(result))
