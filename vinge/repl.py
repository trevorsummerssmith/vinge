from kct.argparse import ArgumentParser
import kct.output as output
import sys

import vinge.cmd as cmd

class _CommandParsingError(Exception):
    def __init__(self, message):
        self.message = message

class _DontDieArgumentParser(ArgumentParser):
    """
    ArgumentParser prints a message then calls exit upon reaching an error.
    Override the error method to raise an exception instead. This is used to
    parse the input on our REPL.
    """
    def error(self, message):
        raise _CommandParsingError(message)

def _setup_command_parser():
    command_parser = _DontDieArgumentParser(description='foo')
    subparsers = command_parser.add_subparsers()

    # go command
    go_parser = subparsers.add_parser('go', aliases=['g'])
    go_parser.add_argument('idx', type=int)
    go_parser.set_defaults(func=cmd.go_by_neighbor_index)

    # quit
    quit_parser = subparsers.add_parser('quit')
    quit_parser.set_defaults(func=cmd.quit)
    return command_parser

def repl(ctx):
    parser = _setup_command_parser()
    while True:
        output.pp("> ", newline=False)
        str_args = sys.stdin.readline().rstrip()
        parser_args = str_args.split()
        try:
            args = parser.parse_args(parser_args)
        except _CommandParsingError, cpe:
            print "Error %s" % cpe.message
            continue
        args.func(ctx, args)
