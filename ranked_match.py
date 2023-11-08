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
'''


import argparse
import collections
import csv
import sys
import os


Result = collections.namedtuple('Result', ['name', 'topic', 'choice'])


def parseInteger(s):
    s = s.strip('\uFEFF').strip().strip('\xCA')
    try:
        return int(s)
    except ValueError:
        return s if len(s) else None


def parseCSVFile(infile):
    reader = csv.reader(infile)
    data = []
    for line in reader:
        line = [parseInteger(x) for x in line]
        if line:
            data.append(line)
    return data


def getPrefs(csv_data):
    allPrefs = [[] for n in csv_data[0]]
    for idx, prefs in enumerate(allPrefs):
        for row in csv_data[1:]:
            if idx < len(row):
                topic = row[idx]
                if topic is not None:
                    prefs.append(topic)
    return csv_data[0], allPrefs


def rankedMatch(names, allPrefs):
    assignments = dict()
    N = len(names)
    topics = ['' for _ in range(N)]
    choices = [0 for _ in range(N)]
    while any(topic == '' for topic in topics):
        for idx in range(N):
            if topics[idx] != '':
                continue
            prefs = allPrefs[idx]
            if not prefs:
                topics[idx] = None
                continue
            topic = prefs.pop(0)
            choices[idx] += 1
            current_student = assignments.get(topic)
            if current_student is None:
                assignments[topic] = idx
                topics[idx] = topic
            elif current_student > idx:
                # less rank is better
                assignments[topic] = idx
                topics[idx] = topic
                topics[current_student] = ''
    return [Result(n, t, c) for n, t, c in zip(names, topics, choices)]


def print_students(output, students):
    name_length = max(len(s.name) for s in students)
    for student in students:
        output.write('%-*s topic=%r (ranked=%d)\n' % (
              name_length, student.name, student.topic, student.choice))


def main():
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__)
    argparser.add_argument(
        'CSV_FILE',
        type=argparse.FileType('r'),
        help='Path of CSV file to read.')
    args = argparser.parse_args(sys.argv[1:])
    data = parseCSVFile(args.CSV_FILE)
    args.CSV_FILE.close()
    print_students(sys.stdout, rankedMatch(*getPrefs(data)))


if __name__ == '__main__':
    main()
