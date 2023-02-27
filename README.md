# Bioscript

Biology Scripts

*Copyright 2023 Hal W Canary III, Lindsay R Saunders PhD.*  
*Use of this program is governed by contents of the LICENSE file.*

* * *

## Install

1.  Install Python 2.7.x or 3.x (3.x preferrably). <https://www.python.org/downloads/>

    Verify that the command

    ```
    python --version
    ```

    or

    ```
    python3 --version
    ```

    works.  Remember which one and use that when running the scripts.

2.  Clone this repo:

    ```
    cd ~
    git clone https://github.com/HalCanary/bioscript.git
    ```

    or, if you have Github permissions:

    ```
    cd ~
    git clone git@github.com:HalCanary/bioscript.git
    ```

* * *

## Running `New_Database_One_Sequence_per_Species.py`

Suppose the input file is `~/Desktop/foobar.fasta` and the genus to be filterted is `Foobar`.

Run:

```
python ~/bioscript/New_Database_One_Sequence_per_Species.py Foobar ~/Desktop/foobar.fasta _new
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
