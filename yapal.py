import argparse
import src.YAPAL_TOKENIZER as tokenizer
from src._yapal_seq import YapalSequencer as yapal_seq
from src.grammar import Grammar
from yalex import yalex


def main():
    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('yal_file', type=str,
                        help='File with the lexical analyzer specification (.yal)')
    parser.add_argument('yapl_file', type=str,
                        help='File with the syntax analyzer specification (.yapl)')
    parser.add_argument('input_file', type=str,
                        help='File with input strings for both generators')

    args = parser.parse_args()

    print('INPUT FILES')

    print(f"Lexical file: {args.yal_file}")
    print(f"Syntax file: {args.yapl_file}")
    print(f"Input file: {args.input_file}")

    print('-'*80)
    print("YALEX")
    print('-'*80)
    # Remove if fails yalex
    # Execute the command below to run the lexical analyzer
    dir_dfa = yalex(args.yal_file, '.', False, False, False)
    tokens = dir_dfa.returnDict.keys()

    print('-'*80)

    yapal_tokens = tokenizer.analyze(args.yapl_file, False)
    if yapal_tokens == None:
        print("✖ No tokens defined in YAPAL")
        return
    elif len(yapal_tokens) == 0:
        print("✖ No tokens defined in YAPAL")
        return

    ypsq = yapal_seq(yapal_tokens)
    if ypsq.sequence():
        print("✔ Tokens have been sequenced successfully")
    else:
        print("✖ Tokens could not be sequenced, missing '%%' token")
        return

    print("YAPAL")

    print('-'*80)

    print(f"Defined tokens: {ypsq.get_defined_tokens()}")
    print(f"Ignored tokens: {ypsq.get_ignored_tokens()}")
    print(f"Terminals: {ypsq.get_terminals()}")
    print(f"Non terminals: {ypsq.get_non_terminals()}")

    # Remove if fails yalex
    if ypsq.compare_tokens(tokens):
        print("✔ All the tokens used in YAPAL are defined in YALEX")

    else:
        print("✖ Some tokens used in YAPAL are not defined in YALEX")

    if ypsq.check_non_terminals_use():
        print("✔ All non-terminals in productions are defined in YAPAL")
    else:
        print("✖ Some non-terminals in productions are not defined in YAPAL")

    if ypsq.get_defined_productions() == None:
        print("✖ No productions defined in YAPAL")
        return

    grammar = Grammar(ypsq.get_defined_productions())

    print("✔ Grammar has been created successfully")

    grammar.augment()

    print("✔ Productions have been augmented successfully:")
    print(grammar)

    C, relations = grammar.items(ypsq.get_symbols())

    print("✔ Items has been generated successfully:")
    for i, items in enumerate(C):
        print(f"\tI{i}:\n{grammar.items_to_str_print(items)}")

    print("✔ Relations has been generated successfully:")
    for i, relation in enumerate(relations):
        print(f"\t[{i}] I{relation[0]} -> I{relation[1]} on {relation[2]}")

    grammar.draw(C, relations, "LRAutomaton")

    grammar.compute_first()
    print("✔ First sets have been computed successfully:")
    # Iterate over keys and values in dictionary
    idx = 0
    for key, value in grammar.first_sets.items():
        print(f"\t[{idx}] {key}: {value}")
        idx += 1


if __name__ == "__main__":
    main()
