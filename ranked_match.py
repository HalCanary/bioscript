#! /usr/bin/env python3

# Copyright 2023 Hal W Canary III, Lindsay R Saunders PhD.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''
CSV file format:

   NAME, NAME, NAME, NAME
   40,   34,   2,    19
   27,   40,   17,   4
   1,    1,    3,    34
   3,    19,   7,    4

To Run:

    Lindsays-MBP:~ Lindsay$ .../ranked_match.py  PATH_TO_CSV_FILE
'''


import csv
import sys
import os


class Student:
    def __init__(self, name, prefs, rank):
        self.name = name
        self.prefs = [p for p in prefs if p]
        self.rank = rank
        self.topic = ''
        self.choice = 0

    def __str__(self):
        return '%s %r' % (self.name, self.prefs)


def parseInteger(s):
    s = s.replace('\xCA', '').strip()
    try:
        return int(s)
    except ValueError:
        if len(s):
            raise
        return None


def parseCSVFile(infile):
    reader = csv.reader(infile)
    names = [n.strip().strip('\uFEFF') for n in next(reader)]
    num_names = len(names)
    inverse_prefs = []
    for line in reader:
        assert len(line) <= num_names
        line = [parseInteger(x) for x in line]
        if not any(line):
            continue
        if len(line) < num_names:
            line.extend([None for x in range(len(line), num_names)])
        inverse_prefs.append(line)
    return (names, inverse_prefs)


def rangedMatch(names, inverse_prefs):
    all_prefs = [list(x) for x in zip(*inverse_prefs)]

    number_topics = max(topic for prefs in all_prefs for topic in prefs if topic is not None)

    assert number_topics >= len(all_prefs[0])

    assert all(topic is None or topic > 0 for prefs in all_prefs for topic in prefs)

    for prefs in all_prefs:
        prefs.extend([None for x in range(len(prefs), number_topics)])

    students = [Student(name, prefs, rank)
                for rank, (name, prefs) in enumerate(zip(names, all_prefs))]

    assignments = dict((i, None) for i in range(1, number_topics + 1))

    while any(student.topic == '' for student in students):
        for student in students:
            if student.topic != '':
                continue
            if not student.prefs:
                student.topic = None
                continue
            topic = student.prefs.pop(0)
            student.choice += 1
            current_student = assignments[topic]
            if current_student is None:
                assignments[topic] = student
                student.topic = topic
            elif current_student.rank > student.rank:
                # less rank is better
                assignments[topic] = student
                student.topic = topic
                current_student.topic = ''

    return students


def main():
    if len(sys.argv) < 2:
        sys.stdout.write("Usage:\n\t%s CSV_FILE_PATH\n" % (
            os.path.basename(sys.argv[0])))
        sys.stdout.write(__doc__ + '\n')
        exit(1)

    with open(sys.argv[1], 'r') as infile:
        names, inverse_prefs = parseCSVFile(infile)
    students = rangedMatch(names, inverse_prefs)
    name_length = max(len(s.name) for s in students)
    for student in students:
        sys.stdout.write('%-*s topic=%r (ranked=%d)\n' % (
              name_length, student.name, student.topic, student.choice))


if __name__ == '__main__':
    main()
