import argparse


from src._tokenizer import Tokenizer
from src.utils.tools import readFile, str2bool, str2file, save_to_pickle, numberToLetter
from src.utils.patterns import ID, WS, EQ, EXPR, COMMENT, RETURN, LET, OPERATOR, GROUP, RULE, CHAR
from src.utils.constants import IDENT, VALUE, MATCH, EXIST, EXTRACT_REMINDER, OR, CONCAT, SPECIAL, SPECIAL2
from src._yal_seq import YalSequencer as YalSeq
from src._expression import Expression
from src._ast import AbstractSyntaxTree as AST
from src.utils.structures.tree_node import TreeNode
from src._dir_dfa import DirectDeterministicFiniteAutomaton as DirDFA
from src.analyzer_serializer import generate_script


def yalex(file_path: str, dir_name: str, draw_subtrees: bool, draw_tree: bool, draw_automatons: bool):

    fileContent = readFile(file_path)
    print(f'✔ File read successfully from {file_path}')

    lexer = Tokenizer(fileContent)
    lexer.addPatterns([COMMENT, WS, ID, EQ, EXPR, RETURN])
    lexer.tokenize()

    if lexer.errorsManager.haveErrors():
        lexer.errorsManager.printErrors(
            '✖ Tokens has not been generated successfully')
        return

    if len(lexer.symbolsTable) == 0:
        print('✖ No tokens generated')
        print('\tError: No tokens generated')
        print('\tSuggestion: Check your .yal file have some content to be tokenized')
        return

    print('✔ Tokens has been generated successfully:')
    for idx, symbol in enumerate(lexer.symbolsTable):
        print(f'\t[{idx}] {symbol}')

    lexer.removeSymbols([COMMENT])

    yal_let = YalSeq(
        lexer,
        [
            [LET, SPECIAL2],
            [WS, EXIST],
            [ID, IDENT],
            [WS, EXIST],
            [EQ, EXIST],
            [WS, EXIST],
            [EXPR, VALUE],
        ],
        [ID, OPERATOR, GROUP, CHAR],
        ID
    )

    yal_let.extractIdent()
    if yal_let.errorsManager.haveErrors():
        yal_let.errorsManager.printErrors('✖ Identities extraction failed')
        return
    print('✔ Identities extraction successful')

    if draw_subtrees:
        if len(yal_let.idents) == 0:
            print('✖ No subtrees to draw')
        else:
            print('✔ Drawing subtrees:')
    else:

        print('✔ Subtrees drawing skipped, as per user request')

    subtreesDict: dict[TreeNode] = {}
    if len(yal_let.idents) != 0:
        for idx, ident in enumerate(yal_let.idents.keys()):
            this_expression: Expression = Expression(yal_let.idents[ident])
            this_expression.hardProcess()
            this_ast: AST = AST(this_expression.infixRegEx)
            subtreesDict[ident] = this_ast
            if draw_subtrees:
                this_ast.draw(ident, dir_name, ident, False)
                print(f'\t[{idx}] \"{ident}\" AST has been drawn successfully')

    yal_rule = YalSeq(
        lexer,
        [
            [RULE, SPECIAL],
            [WS, EXIST],
            [ID, IDENT],
            [WS, EXIST],
            [EQ, EXIST],
            [None, EXTRACT_REMINDER]
        ],
        None,
        None
    )

    yal_rule.extractIdent()

    if yal_rule.errorsManager.haveErrors():
        yal_rule.errorsManager.printErrors(
            '✖ Rule extraction failed')
        return
    elif len(yal_rule.reminders) == 0:
        print('✖ No rule found')
        print('\tError: No rule found')
        print('\tSuggestion: Check you have a rule defined in your .yal file')
        return

    rule_lexer = Tokenizer()
    rule_lexer.symbolsTable = yal_rule.reminders
    rule_lexer.removeSymbols([WS])

    if len(rule_lexer.symbolsTable) == 0:
        print('✖ No rules definition')
        print('\tError: No rule definition found')
        print('\tSuggestion: Check you have a rule defined in your .yal file')
        return

    print('✔ Rule extraction successful')

    print('✔ Building the final AST')

    last = None
    root = None
    left = None

    alphabet: set[str] = set()
    last_symbol = None

    namingSpecialCases = {
        "'+'": 'PLUS',
        "'*'": 'TIMES',
        "'('": 'LPAREN',
        "')'": 'RPAREN',
        "'-'": 'MINUS',
        "'/'": 'DIV'
    }

    returnDict = {}
    idCounter = 0
    returnCounter = 0
    specialNamingCounter = 1
    for symbol in rule_lexer.symbolsTable:
        # print(f'Processing symbol: {symbol}')
        if symbol.type == ID.name:
            idCounter += 1
            last = subtreesDict.get(symbol.original, None)
            last_symbol = symbol.original

        elif symbol.type == RETURN.name:
            returnCounter += 1
            last.root = TreeNode(CONCAT, TreeNode(
                f'#{last_symbol}'), last.root)
            alphabet = alphabet.union(set(last.alphabet))
            alphabet.add(f'#{last_symbol}')

            returnDict[last_symbol] = symbol.original

            if left is None:
                left = last.root
            else:
                left.right = last.root

        elif symbol.type == EXPR.name:
            if symbol.original == OR:
                or_node = TreeNode(OR)
                or_node.left = left
                left = or_node
            else:
                idCounter += 1

                this_expression: Expression = Expression(symbol.original)

                this_expression.hardProcess()
                this_ast: AST = AST(this_expression.infixRegEx)
                last = this_ast

                # Check the symbol.original is a special case else name as tokena, tokenb, ...
                if symbol.original in namingSpecialCases:
                    last_symbol = namingSpecialCases[symbol.original]
                else:
                    # Using the specialNamingCounter to cast to abcd...z
                    last_symbol = f'TOKEN{numberToLetter(specialNamingCounter)}'
                    specialNamingCounter += 1

    if idCounter != returnCounter:
        print('✖ Rule definition failed')
        print('\tError: The number of IDs and Returns does not match')
        print('\tSuggestion: Check the rule definition on your .yal file')
        return

    root = left

    final_ast: AST = AST(' ')
    final_ast.root = root
    final_ast.alphabet = sorted(list(alphabet))

    if final_ast.errorsManager.haveErrors():
        final_ast.errorsManager.printErrors('✖ Final AST building failed')
        print('\tSuggestion: Check the rule definition on your .yal file')
        return

    if draw_tree:
        final_ast.draw('final_ast', dir_name, 'Final AST', False)
        print('✔ Final AST has been drawn successfully')

    print('✔ Final AST has been completed successfully')

    final_dir_dfa = DirDFA(final_ast.root.deepCopy())
    final_dir_dfa.returnDict = returnDict
    if draw_automatons:
        final_dir_dfa.draw('final_dir_dfa', dir_name, 'Final DIR DFA')
        print('✔ Final DIR DFA has been drawn successfully')

    print('✔ Final DIR DFA has been completed successfully')

    print('-' * 10, 'IMPORTANT', '-' * 10)
    save_as = save_to_pickle(final_dir_dfa, directory=dir_name,
                             file_name='YALEX_ANALYZER', structure_name='Final DIR DFA')

    save_as = generate_script(save_as,
                              f'{dir_name}/YALEX_ANALYZER.py')

    print(f'✔ Analyzer Script has been generated successfully to {save_as}')

    print('-'*31)

    print('✔ All Done!')

    return final_dir_dfa


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lexer Analyzers Generator")
    parser.add_argument('yal_path', type=str2file,
                        help='The .yal file path')  # Yal file path
    parser.add_argument('output_path', type=str,
                        help='The directory name to save the results')  # Save to directory
    parser.add_argument('draw_subtrees', type=str2bool,
                        help='A boolean flag to draw the subtrees or not.')  # Draw subtrees

    parser.add_argument('draw_tree', type=str2bool,
                        help='A boolean flag to draw the tree or not.')  # Draw tree

    parser.add_argument('draw_automatons', type=str2bool,
                        help='A boolean flag to draw the automatons or not.')  # Draw automatons

    args = parser.parse_args()

    file_path = args.yal_path
    dir_name = args.output_path
    draw_subtrees = args.draw_subtrees
    draw_tree = args.draw_tree
    draw_automatons = args.draw_automatons

    yalex(file_path, dir_name, draw_subtrees, draw_tree, draw_automatons)

    print('Exiting...')
