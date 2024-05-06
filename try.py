from src.grammar import Grammar
from src._yapal_seq import YapalSequencer as yapal_seq
import src.YAPAL_TOKENIZER as tokenizer


def main():
    yapl_file = './input/tests/slr-1/slr-1-1.yalp'
    yapal_tokens = tokenizer.analyze(yapl_file, False)

    ypsq = yapal_seq(yapal_tokens)
    ypsq.sequence()

    grammar = Grammar(ypsq.get_defined_productions())

    grammar.compute_first()
    print("✔ First sets have been computed successfully:")
    # Iterate over keys and values in dictionary
    idx = 0
    for key, value in grammar.first_sets.items():
        print(f"\t[{idx}] {key}: {value}")
        idx += 1

    grammar.compute_follow()
    print("✔ Follow sets have been computed successfully:")
    # Iterate over keys and values in dictionary
    idx = 0
    for key, value in grammar.follow_sets.items():
        print(f"\t[{idx}] {key}: {value}")
        idx += 1


if __name__ == "__main__":
    main()
