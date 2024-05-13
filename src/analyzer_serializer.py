def generate_script(analyzer_path, output_file):
    code_template = """
import csv
import argparse
from colorama import Fore, Style

from src.utils.tools import readFile, load_from_pickle
from src._dir_dfa import DirectDeterministicFiniteAutomaton as DFA
from src._tokenizer import Tokenizer

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


verbose = True

def vrint(*args):
    if verbose:
        print(*args)

def analyze(read_file_path, verb=True):
    analyzer_file_path = "{analyzer_path}"

    global verbose
    verbose = verb
    symbolTable = []
    fileContent = readFile(read_file_path)
    vrint(f'✔ File read successfully from {{read_file_path}}')

    if len(fileContent) == 0:
        vrint('✖ File is empty!')
        return

    tokenized = Tokenizer(fileContent, useExtraSoftCodify=True)
    unCodified = tokenized.unCodified
    codified = tokenized.codified
    codified.append('#')

    structure: DFA = load_from_pickle(analyzer_file_path)
    vrint(f'✔ Analyzer loaded successfully from {{analyzer_file_path}}')

    vrint('-' * 10, 'ANALYSIS', '-' * 10)

    forward = 0
    while forward < len(fileContent):
        match, idx = structure.specialSimulate(codified[forward:])
        if match is False:
            vrint(Fore.RED + '✖ No match found!' + Style.RESET_ALL)
            vrint(f'[{{forward}}:{{forward+idx}}]', 'No match')
            vrint(Fore.YELLOW + 'Skipping this token...' + Style.RESET_ALL)
            vrint(Fore.RED + '-'*31)
            vrint('-'*31 + Style.RESET_ALL)
            forward += 1
        else:
            vrint(Fore.GREEN + '✔ Match found!' + Style.RESET_ALL)
            vrint(f'[{{forward}}:{{forward+idx}}]', match, '->', unCodified[forward:forward + idx])
            symbolTable.append((match, unCodified[forward:forward + idx]))
            vrint(Fore.YELLOW + 'Executing the attached python code...' + Style.RESET_ALL)
            code = structure.returnDict[match][1:-1]
            code = code.encode().decode('unicode_escape')
            vrint(Fore.CYAN + 'Code to be executed:\\n' + code + Style.RESET_ALL)
            try:
                exec(code)
            except Exception as e:
                vrint(Fore.RED + 'On running return, found error:', e, Style.RESET_ALL)
            forward += idx
            vrint(Fore.RED + '-'*31)
            vrint('-'*31 + Style.RESET_ALL)
    vrint('Analysis finished!')
    return symbolTable

def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Lexer Analyzer")
    parser.add_argument('read_file_path', type=str, help='The .txt file to tokenize')
    parser.add_argument('output_file_path', type=str, help='The output .txt file to write the tokens as CSV')
    parser.add_argument('verbose', type=str2bool, help='A boolean flag to show the logs or not.')

    # Parse the command line arguments
    args = parser.parse_args()

    # Set the global verbose flag
    global verbose
    verbose = args.verbose
    
    # Read the file path and process the symbols
    read_file_path = args.read_file_path
    symbols = analyze(read_file_path, verbose)

    # Write the symbols to the specified output file a symbol[0] per line
    with open(args.output_file_path, 'w', newline='') as file:
        for symbol in symbols:
            file.write(symbol[0] + '\\n')

    print(f'Tokens have been written to {{args.output_file_path}}')

if __name__ == "__main__":
    main()
    vrint('Exiting...')
    """
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(code_template.format(analyzer_path=analyzer_path))

    return output_file
