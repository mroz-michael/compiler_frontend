### Background & Acknowledgement:

This compiler frontend works on a JSON-like Language. This project was originally a school project for Dalhousie's CSCI 2115 Theory Of Computer Science course. The code is largely written by me, however the JSON-like grammar and general structure for the scanner file were provided as part of the course materials. 

## Usage

running python3 compile.py will prompt the user to enter a txt file. if the file given exists, the 
front end compiler will attempt to tokenize the txt file, producing a token stream, which is then fed into
the parser, which produces a parse tree as output.

The token stream and parse trees are saved as files to the directory of the input file. 

## Grammar

The grammar for the JSON-like language this compiler frontend works on is:

VALUE --> dict
VALUE --> list
VALUE --> STRING
VALUE --> NUMBER
VALUE --> "true"
VALUE --> "false"
VALUE --> "null"

<!--note: ()* signifies a Kleene-* operation -->
list --> "[" value ("," value)* "]"

dict --> "{" pair ("," pair)* "}"

pair --> STRING ":" value


## Syntactic Requirements

The scanner will attempt to tokenize any input
in the given txt file and produce a corresponding
token stream. 

The resulting token stream is fed as input into the
parser, which will produce a parse tree representation of the token stream, as well as an error report (if syntax errors are found). 

To avoid syntax errors, the grammar listed above must
be followed carefully. Examples of syntactically valid and syntactically invalid token streams are included in this repository. 




