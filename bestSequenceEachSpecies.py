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


ProcessedDescription = collections.namedtuple(
    'ProcessedDescription', ['genus', 'species', 'accession', 'description'])


def process_sequence_description(description):
    '''
    Expect description to be a string of the form:
    "ACCESSION GENUS EPITHET [MORE...]"
    New description is:
    "GENUS_EPITHET ACCESSION [MORE...]"
    '''
    fields = description.split()
    if len(fields) < 3:
        # `description` is missing an epithet; this is an error.
        raise ValueError('Unable to parse description: %r' % description)
    (accession, genus, epithet), extra = fields[:3], ' '.join(fields[3:])

    species = '%s_%s' % (genus, epithet)
    new_description = ' '.join([species, accession, extra])
    return ProcessedDescription(genus, species, accession, new_description)


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


def get_best_sequence(values):
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
            best_description, best_sequence, best_score = description, sequence, score
    assert best_description is not None and best_sequence is not None
    return (best_description, best_sequence)


# TODO(halcanry): Add unit tests for this function.
def get_best_sequence_each_species(infile, outfile, genus, logger):
    if genus:
        logger.info('Filtering by Genus %r', genus)

    sourceCount, speciesSequenceListMap = 0, collections.defaultdict(list)
    for (description, sequence) in parse_fasta_format(infile):
        sourceCount += 1
        info = process_sequence_description(description)

        if genus and info.genus != genus:
            logger.debug('BAD MATCH:  %s', description)
            continue
        logger.debug('good match: %s', description)

        speciesSequenceListMap[info.species].append((info.accession, info.description, sequence))

    if len(speciesSequenceListMap) == 0:
        raise RuntimeError('None of %d sequences match given genus %r.' % (sourceCount, genus))

    if logger.isEnabledFor(logging.INFO):
        matchCount = sum(len(v) for v in speciesSequenceListMap.values())
        logger.info('Matched %d of %d sequences.', matchCount, sourceCount)

    # Sort output by sepcies for reproducability.
    for species, values in sorted(speciesSequenceListMap.items()):
        try:
            best_description, best_sequence = get_best_sequence(values)
        except Exception as e:
            raise RuntimeError("Error with species %s" % species) from e
        print_fasta_description(outfile, best_description, best_sequence)
        logger.debug('Best of %3d for species %r', len(values), species)

    logger.info('%d species processed.', len(speciesSequenceListMap))


def parse_args(argv):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        exit_on_error=False, description=__doc__)
    parser.add_argument(
        'INFILE',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help='Path of FASTA file to read. (default: STDIN)')
    parser.add_argument(
        '-o',
        '--outfile',
        nargs='?',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help='Where to write FASTA file. (default: STDOUT)')
    parser.add_argument(
        '-g',
        '--genus',
        help='Genus to filter on. (default: None)')
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
        get_best_sequence_each_species(args.INFILE, args.outfile, args.genus, logging.getLogger())
    except Exception as e:
        logging.error(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
