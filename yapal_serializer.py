import argparse

from src.utils.tools import load_from_pickle
from tabulate import tabulate


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


def print_table(array):
    # Define the headers for the table
    headers = ['Stack', 'Symbols', 'Input', 'Action']

    # Prepare the data for tabulation
    data = []
    for item in array:
        row = [str(item['Stack']), str(item['Symbols']),
               str(item['Input']), str(item['Action'])]
        data.append(row)

    # Print the table using tabulate
    print(tabulate(data, headers=headers, tablefmt='grid'))


def simulate(tokensSequence):
    structure = load_from_pickle('SLR1_TABLE.pkl')
    vrint('✔ Analyzer loaded successfully from SLR1_TABLE.pkl')

    log, result = structure.LRparsing(tokensSequence)
    vrint('✔ SLR1 parsing has been executed successfully:')
    print_table(log)
    print(result)


def main():
    # Receive the .txt file path
    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('read_file', type=str,
                        help='File to be analyzed')
    parser.add_argument('verbose', type=str2bool,
                        help='A boolean flag to show the analysis steps')

    args = parser.parse_args()

    global verbose
    verbose = args.verbose

    # Read the file
    file = args.read_file
    with open(file, 'r', encoding='utf-8') as f:
        # Read lines ensuring to remove the newline character and convert to uppercase
        tokensSequence = [line.rstrip().upper() for line in f.readlines()]

    vrint('Tokens sequence:', tokensSequence)

    simulate(tokensSequence)


if __name__ == "__main__":
    main()
    vrint('Exiting...')
