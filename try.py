from src.grammar import Grammar
from src._yapal_seq import YapalSequencer as yapal_seq
import src.YAPAL_TOKENIZER as tokenizer


def main():
    yapl_file = './input/tests/slr-1/slr-1-1.yalp'
    yapal_tokens = tokenizer.analyze(yapl_file, False)

    ypsq = yapal_seq(yapal_tokens)

    grammar = Grammar(ypsq.get_defined_productions())

    grammar.compute_first()


if __name__ == "__main__":
    main()
