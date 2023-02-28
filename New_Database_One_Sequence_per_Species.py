#! /usr/bin/env python

# Copyright 2023 Hal W Canary III, Lindsay R Saunders PhD.
# Use of this program is governed by contents of the LICENSE file.

import collections
import logging
import os
import sys

DEFAULT_GENUS = 'Glutamicibacter'
DEFAULT_INPUT_FILE = os.path.expanduser('~/Desktop/SP23_NewGeneraDatabases/Glutamicibacter_spp.fasta')
DEFAULT_PATH_MODIFIER = '_16s'
DEFAULT_LOG_LEVEL = 'INFO'

# NOTE: log level can be overridden with the
# BIOSCRIPT_LOG_LEVEL environment variable:
#   'DEBUG' for diagnosing bugs.
#   'INFO' for succinct information.
#   'WARNING' for quieter behavior.

# TODO (halcanary): remove DEFAULT_GENUS and DEFAULT_INPUT_FILE.
# TODO (halcanary): can we get GENUS from INPUT_FILE name?
# TODO (halcanary): should we handle stdin and stdout?

################################################################################

################################################################################
# FASTA file format parsing functions
# These may be moved to another package at a later time.
################################################################################

def parse_fasta_format(f):
    '''
    @param f file object open for reading in FASTA format.
    @yield tuples of form (description, sequence)
    '''
    description, sequence = None, None
    for line in f:
        if line.startswith('>'):
            if description and sequence:
                yield (description, sequence)
            #remove '>' character
            description, sequence = line[1:].strip(), ''
        elif sequence is not None:
            sequence += line.strip()
    if description and sequence:
        yield (description, sequence)

def print_fasta_description(o, description, sequence):
    '''
    @param o file object open for writing.
    @param description string describing the sequence.
    @param sequence string in FASTA Sequence Representation.
    '''
    o.write('>%s\n' % description) # prepend '>' character.
    for i in range(0, len(sequence), 70):
        o.write(sequence[i:i+70])
        o.write('\n')
    o.write('\n')

################################################################################

def truncate(s, l):
    return s if len(s) <= l else s[:l-3] + '...'

def get_values_matching_genus(given_genus, fasta_source):
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
    '''
    count, all_values = 0, collections.defaultdict(list)
    for (description, value) in fasta_source:
        count += 1
        try:
            accession, genus, epithet, extra = description.split(maxsplit=3)
        except ValueError:
            try:
                (accession, genus, epithet), extra = description.split(maxsplit=2), ''
            except ValueError:
                logging.error.write('Unable to parse description: %r', description)
                continue
        if given_genus != '' and genus != given_genus:
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug('BAD MATCH:  %s', truncate(description, 68))
            continue
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug('good match: %s', truncate(description, 68))

        species = '%s_%s' % (genus, epithet)
        new_description = ' '.join([species, accession, extra])
        all_values[species].append((accession, new_description, value))
    return count, dict(all_values)


def process_values(species, values):
    best_description, best_sequence, best_score = None, None, (-1, -1, -1, -1)
    for accession, description, sequence in values:
        # score is a comparable 4-tuple of non-negative numbers.
        score = (1 if ' type strain ' in description else 0,
                float(sum(1 for c in sequence if c in ['A', 'G', 'T', 'C'])) / len(sequence),
                1 if accession.startswith('NR_') else 0,
                len(sequence))
        if score >= best_score:
            best_description, best_sequence, best_score = description, sequence, score
    if best_description is None or best_sequence is None:
        raise Exception('Unexpected problem with species %r.' % species)
    return (best_description, best_sequence)


################################################################################

def main(given_genus, input_file, pathmod):
    '''
    @param given_genus If not '', will filter the sequences by genus.
    @param input_file The path of the FASTA format input file.
    @param pathmod If imput_file is 'foo/bar.baz.fasta' and pathmod is
           '_filtered', then the output file will be
           'foo/bar.baz_filtered.fasta'.
    @return 0 on success, 1 othewrwise.
    '''
    pathroot, pathext = os.path.splitext(input_file)
    output_file = pathroot + pathmod + pathext

    logging.info('Genus  is %r', given_genus)
    logging.info('Input  is %r', input_file)
    logging.info('Output is %r', output_file)

    with open(input_file) as f:
        count, all_values = get_values_matching_genus(given_genus, parse_fasta_format(f))
    if logging.getLogger().isEnabledFor(logging.INFO):
        logging.info('Read %d sequences.', count)
        logging.info('Matched %d sequences.', sum(len(v) for v in all_values.values()))
    if len(all_values) == 0:
        logging.error('No sequences match.')
        return 1

    with open(output_file, 'w') as o:
        # Sort output by sepcies for reproducability.
        for species, values in sorted(all_values.items()):
            try:
                best_description, best_sequence = process_values(species, values)
            except Exception as e:
                logging.error(e)
                continue
            print_fasta_description(o, best_description, best_sequence)
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug('Best of %3d for species %r', len(all_values[species]), species)
    logging.info('%d species processed.', len(all_values))
    logging.info('Wrote to file %r', output_file)
    return 0


if __name__ == '__main__':
    logging.basicConfig(
        format='%(levelname)-5s:  %(message)s',
        level=os.getenv('BIOSCRIPT_LOG_LEVEL', default=DEFAULT_LOG_LEVEL))
    if len(sys.argv) == 4:
        sys.exit(main(*sys.argv[1:4]))
    elif len(sys.argv) == 3:
        sys.exit(main(*sys.argv[1:3], DEFAULT_PATH_MODIFIER))
    elif len(sys.argv) == 1:
        sys.exit(main(DEFAULT_GENUS, DEFAULT_INPUT_FILE, DEFAULT_PATH_MODIFIER))
    else:
        sys.stderr.write('\nUsage:\n %s GENUS INPUT_FILE_PATH PATH_MODIFIER_STRING\n\n' % sys.argv[0])
        sys.exit(1)