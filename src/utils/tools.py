import argparse
import os
import pickle as pkl


class Error(object):
    '''
    This class represents an error.
    '''

    def __init__(self, error: str, consequence: str):
        '''
        This is the constructor of the class.
        Parameters:
        - error: A string representing the error.
        - consequence: A string representing the consequence of the error.
        '''
        self.error = error
        self.consequence = consequence


class errorsManager(object):
    '''
    This class represents the errors manager.
    '''

    def __init__(self):
        '''
        This is the constructor of the class.
        '''
        self.errors: list[Error] = []

    def haveErrors(self) -> bool:
        '''
        This function returns True if there are errors in the errors list, False otherwise.
        '''
        return len(self.errors) > 0

    def addError(self, error: str, consequence: str):
        '''
        This function adds an error to the errors list.
        Parameters:
        - error: A string representing the error.
        - consequence: A string representing the consequence of the error.
        '''
        self.errors.append(Error(error, consequence))

    def printErrors(self, scope: str):
        '''
        This function prints all the errors in the errors list.
        '''
        if self.errors:
            print(f'{scope}')
            for error in self.errors:
                print(
                    f'\tError: {error.error}, Consequence: {error.consequence}')
        else:
            print(f'No errors in {scope}')


def readFile(file: str) -> str:
    '''
    This function reads a YAL file and returns its content.
    Parameters:
    - file: A string representing the file name.
    Returns:
    - The content of the file.
    '''
    with open(file, 'r', encoding='utf-8') as f:
        return f.read()


def numberToLetter(number: int) -> str:
    '''
    This function return a letter from A to Z based on the number.
    If the number is greater than 26, it calls itself recursively using the difference between the number and 26 to obtain a new combination.
    '''
    if number <= 26:
        return chr(96 + number)
    else:
        return numberToLetter((number - 1) // 26) + numberToLetter((number - 1) % 26 + 1)


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def str2file(v):
    '''
    Check if a file exists.
    '''
    if not os.path.isfile(v):
        raise argparse.ArgumentTypeError(f'File {v} does not exist')
    return v


def str2dir(v):
    '''
    Check if the name is valid to be assigned to a directory, this means any character may cause an error in naming
    '''
    if not v.isidentifier():
        raise argparse.ArgumentTypeError(
            f'The name {v} is not a valid directory name')
    return v


def save_to_pickle(structure, directory, file_name, structure_name='structure'):
    save_as = f'{directory}/{file_name}.pkl'

    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(save_as), exist_ok=True)

    with open(save_as, 'wb') as f:
        pkl.dump(structure, f)
    print(f'✔ {structure_name} saved to {save_as}')

    return save_as


def load_from_pickle(file_path):
    with open(file_path, 'rb') as f:
        return pkl.load(f)
