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
Concat a set of FASTA files.
'''

import argparse
import logging
import os
import sys


###################################################################################################
# FASTA file format parsing functions
# These may be moved to another package at a later time.
###################################################################################################


def parse_fasta_format(f):
    '''
    @param f file object open for reading in FASTA format.
    @yield tuples of form (description, sequence)

    Ignores data before the first description.
    '''
    description, sequence = None, None
    for line in f:
        if line.startswith('>'):
            if description and sequence:
                yield (description, sequence)
            # Remove '>' character
            description, sequence = line[1:].strip(), ''
        elif sequence is not None:
            sequence += line.strip()
    if description and sequence:
        yield (description, sequence)


def print_fasta_description(o, description, sequence):
    '''
    @param o file object open for writing.
    @param description string describing the sequence.
           The '>' character is prepended.
    @param sequence string in FASTA Sequence Representation.
    '''
    o.write('>%s\n%s\n\n' % (description, split_str(sequence, 70)))


def split_str(s, n):
    '''
    Inserts newlines into string `s` so that lines are no longer than
    `n` characters long.
    '''
    return '\n'.join(s[i:i+n] for i in range(0, len(s), n))


###################################################################################################


def concat(infilenamess, outfile, logger):
    '''
    concatinate a set of FASTA files.
    '''
    count = 0
    for filename in infilenamess:
        with open(filename) as f:
            for (description, sequence) in parse_fasta_format(f):
                description = os.path.basename(filename) + " : " + description
                print_fasta_description(outfile, description, sequence)
                logger.debug('%s + %d', description, len(sequence))
                count += 1
    logger.info('sequence count: %d', count)


def parse_args(argv):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        exit_on_error=False, description=__doc__)
    parser.add_argument(
        'infiles',
        metavar='IN_FILES',
        type=str,
        nargs='+',
        help='Path of FASTA file to read. (default: STDIN)')
    parser.add_argument(
        '-o',
        '--outfile',
        nargs='?',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help='Where to write FASTA file. (default: STDOUT)')
    parser.add_argument(
        '--loglevel',
        choices=['debug', 'info', 'warning'],
        default='info',
        help='Verbosity level. (default: info)')
    return parser.parse_args(argv)


###################################################################################################


def main():
    args = parse_args(sys.argv[1:])
    logging.basicConfig(format='%(levelname)s:  %(message)s', level=args.loglevel.upper())
    try:
        concat(args.infiles, args.outfile, logging.getLogger())
    except Exception as e:
        logging.error(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
