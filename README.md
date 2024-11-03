# Bioscript

Biology Scripts

*Copyright 2023 Hal W Canary III, Lindsay R Saunders PhD.*
*Use of this program is governed by contents of the LICENSE file.*

* * *

## Install

0.  Open a terminal.  For MacOS, get the instructions here:
    <https://google.com/search?q=OPEN+MACOS+TERMINAL>

1.  Install Python (version ≥ 3.) <https://www.python.org/downloads/>

    Verify that the command

    ```
    python3 --version
    ```

    works.

2.  Install `git`.  Check if it is installed with the command `git --version` .
    "If you don’t have it installed already, it will prompt you to install it."

3.  Clone this repo with `git`:

    ```
    cd ~
    git clone https://github.com/HalCanary/bioscript.git
    ```

    or, if you have Github permissions:

    ```
    cd ~
    git clone git@github.com:HalCanary/bioscript.git
    ```

    This will install into the directory `~/bioscript/` .


* * *

## Unit Testing

To execute all tests:

```
./test_bioscript.py
```

* * *

## Running `concat_fasta.py`

After installing the `bioscript` repository, execute the following, (after
changing the filenames appropriately:

```
~/bioscript/concat_fasta.py \
    --outfile ~/Desktop/EnvUn_SP24_Round1.fasta \
    ~/Desktop/SP24_Round1_Environmental_Sequences_seq/*.seq
```

* * *

## Running `bestSequenceEachSpecies.py`

Suppose the input file is `~/Desktop/foobar.fasta` and the genus to be filterted is `Foobar`.

Run:

```
~/bioscript/bestSequenceEachSpecies.py \
    -g Foobar \
    --count 2 \
    ~/Desktop/foobar.fasta \
    -o ~/Desktop/foobar_new.fasta
```

This should write to a file `~/Desktop/foobar_new.fasta`.

What it does:

*   Descriptions of the form

    ```
    >XX999999.9 Foobar baz strain Ind Int 3 16S ribosomal RNA gene, partial sequence
    ```

    will be renamed

    ```
    >Foobar_baz XX999999.9 strain Ind Int 3 16S ribosomal RNA gene, partial sequence
    ```

*   Given the above input description, the genus is assumed to be `Foobar`.
    Only exact matches for the genus are used.

*   Given the above input description, the species is assumed to be `Foobar_baz`.

    Only the "best" sequence for each species is kept, according to the
    following criteria:

    1.  If one has the string "` type strain `" in its description and the
        other does not, use the former, otherwise:

    2.  If one has a higher ratio of `AGTC` characters in the sequence than the other,
        use that one, but otherwise:

    3.  If one's accession string starts with "`NR_`", and the other does not,
        use that one, otherwise:

    4.  Use the one with the longer sequence.

* * *

## Running `ranked_match.py`

To run the ranked match program, first install `python3` and `~/bioscript` as
described above.  Then, from a Terminal, first navigate to the directory where
your rankings CSV file is located.

```
$ cd ~/Desktop
$
```

(_Here, the string "`$`" represents your entire prompt.  You don't type it,
only the text after the `$`._)

To see what files are located here, use the `ls` command.  For example:

```
$ ls
Bio212_FA20_Topic_Rankings.csv	Bio212_FA20_Topic_Rankings_OUTPUT.txt
$
```

To produce rankings:

```
$ ~/bioscript/ranked_match.py Bio212_FA20_Topic_Rankings.csv
Francesca Russo    topic=36 (ranked=1)
Jamie Costa        topic=68 (ranked=1)
Robin Ortega       topic=37 (ranked=1)
Kobe Davis         topic=77 (ranked=1)
Mia Beard          topic=7 (ranked=1)
Nathanael Rangel   topic=76 (ranked=2)
Gloria Conley      topic=55 (ranked=1)
Marvin Richmond    topic=13 (ranked=1)
Whitney Wang       topic=6 (ranked=1)
Cohen Aguilar      topic=19 (ranked=1)
Josie Rodriguez    topic=72 (ranked=1)
Henry Zimmerman    topic=34 (ranked=1)
Ariyah Valdez      topic=10 (ranked=3)
Kyler McDaniel     topic=35 (ranked=2)
Dahlia Taylor      topic=20 (ranked=3)
Jackson Avalos     topic=38 (ranked=1)
Paloma Williams    topic=52 (ranked=2)
Oliver Moon        topic=57 (ranked=1)
Naya Riley         topic=63 (ranked=3)
Amari Fischer      topic=53 (ranked=2)
Maci Fuentes       topic=54 (ranked=5)
Bowen Potter       topic=24 (ranked=2)
Rory Pollard       topic=50 (ranked=3)
Jad Warren         topic=65 (ranked=3)
Sloane Pham        topic=27 (ranked=1)
Russell Tapia      topic=69 (ranked=2)
Michaela Rodriguez topic=43 (ranked=1)
Henry Archer       topic=49 (ranked=1)
Kadence Lyons      topic=71 (ranked=1)
Cyrus Ball         topic=None (ranked=2)
Abby Decker        topic=None (ranked=2)
```

Alternatively, to save the output to a text file:

```
$ ~/bioscript/ranked_match.py Bio212_FA20_Topic_Rankings.csv > Bio212_FA20_Topic_Rankings_OUTPUT.txt
```

* * *
