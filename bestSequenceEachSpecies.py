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
Create a new FASTA database with only best sequence per species.

The accession, genus, and species epithet are assumed to be the first three
fields in the description.
'''

import argparse
import collections
import logging
import os
import sys


###############################################################################
# FASTA file format parsing functions
# These may be moved to another package at a later time.
###############################################################################

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


###############################################################################

def get_values_matching_genus(given_genus, fasta_source, logger):
    '''
    @param given_genus If not '', will filter the sequences by genus.
    @param fasta_source FASTA source, a list (or generator) of tuples of
           form `(description, value)`.
           Each description line is expected to be in the form:
           >ACCESSION_NUMBER GENUS EPITHET EXTRA ...
    @return tuple of (count, dictionary) where count is the number of read
            sequences from the source and the dictionary is
            keyed by species ("{GENUS}_{EPITHET}") with values
            that are lists of tuples, where each tuple is
            `(accession_number, changed_description, sequence)`.
            The new decription is the form:
            >GENUS_EPITHET ACCESSION_NUMBER EXTRA ...
    @raises ValueError if description has less than three fields.
    '''
    count, all_values = 0, collections.defaultdict(list)
    for (description, value) in fasta_source:
        count += 1
        try:
            accession, genus, epithet, extra = description.split(maxsplit=3)
        except ValueError:
            # `split` returned less than four elements; try again, assuming
            # that extra is empty.
            try:
                accession, genus, epithet = description.split(maxsplit=2)
                extra = ''
            except ValueError:
                # `description` is missing an epithet; this is an error.
                raise ValueError(
                    'Unable to parse description: %r' % description)
        if given_genus and genus != given_genus:
            logger.debug('BAD MATCH:  %s', description)
            continue
        logger.debug('good match: %s', description)

        species = '%s_%s' % (genus, epithet)
        new_description = ' '.join([species, accession, extra])
        all_values[species].append((accession, new_description, value))
    return count, dict(all_values)


def get_score(accession, description, sequence):
    '''
    Returns a comparable 4-tuple of non-negative numbers.
    '''
    agtc_count = sum(1 for c in sequence if c in ['A', 'G', 'T', 'C'])
    return (
        1 if ' type strain ' in description else 0,
        float(agtc_count) / len(sequence),
        1 if accession.startswith('NR_') else 0,
        len(sequence),
    )


def process_values(values):
    '''
    @param values nonempty list of (accession, description, sequence) tuples.
    @return the best (description, sequence) pair based on `get_score`
    @raises ValueError if no values are provided
    '''
    best_description, best_sequence, best_score = None, None, (-1, -1, -1, -1)
    if not values:
        raise ValueError('No sequences provided')
    for accession, description, sequence in values:
        score = get_score(accession, description, sequence)
        if score >= best_score:
            best_description, best_sequence = description, sequence
            best_score = score
    assert best_description is not None and best_sequence is not None
    return (best_description, best_sequence)


# TODO(halcanry): Add unit tests for this function.
def get_best_sequence_each_species(infile, outfile, genus, logger):
    if genus:
        logger.info('Filtering by Genus %r', genus)
    count, all_values = get_values_matching_genus(
        genus, parse_fasta_format(infile), logger)

    if len(all_values) == 0:
        raise RuntimeError('None of %d sequences match given genus %r.' % (
            count, genus))

    if logger.isEnabledFor(logging.INFO):
        matchcount = sum(len(v) for v in all_values.values())
        logger.info('Matched %d of %d sequences.', matchcount, count)

    # Sort output by sepcies for reproducability.
    for species, values in sorted(all_values.items()):
        try:
            best_description, best_sequence = process_values(values)
        except Exception as e:
            raise RuntimeError(
                "Error with species %s" % species) from e
        print_fasta_description(outfile, best_description, best_sequence)
        logger.debug('Best of %3d for species %r', len(values), species)

    logger.info('%d species processed.', len(all_values))


def parse_args(argv):
    parser = argparse.ArgumentParser(
        exit_on_error=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__)
    parser.add_argument(
        'INFILE', nargs='?', type=argparse.FileType('r'),
        default=sys.stdin,
        help='Path of FASTA file to read. (default: STDIN)')
    parser.add_argument(
        '-o', '--outfile', nargs='?',
        type=argparse.FileType('w'), default=sys.stdout,
        help='Where to write FASTA file. (default: STDOUT)')
    parser.add_argument(
        '-g', '--genus', help='Genus to filter on. (default: None)')
    parser.add_argument(
        '--loglevel', choices=['debug', 'info', 'warning'],
        default='info', help='Verbosity level. (default: info)')
    return parser.parse_args(argv)

###############################################################################


def main():
    args = parse_args(sys.argv[1:])
    logging.basicConfig(
        format='%(levelname)s:  %(message)s',
        level=args.loglevel.upper())
    try:
        get_best_sequence_each_species(
            args.INFILE, args.outfile, args.genus, logging.getLogger())
    except Exception as e:
        logging.error(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
