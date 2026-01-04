"""
Console progress bar utility for displaying algorithm progress.

This module provides a simple terminal progress bar function adapted from
Stack Overflow. It displays progress as a visual bar with percentage completion,
useful for long-running evolutionary algorithm processes.

Source: Stack Overflow (https://stackoverflow.com/a/...)
License: CC BY-SA 4.0
Retrieved: 2025-12-11
"""

#######################################################################################################
#######################################################################################################
#######################################################################################################
#
#
# function from stackoverflow at
# https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
#
#
#######################################################################################################
#######################################################################################################
#######################################################################################################







# Source - https://stackoverflow.com/a
# Posted by Greenstick, modified by community. See post 'Timeline' for change history
# Retrieved 2025-12-11, License - CC BY-SA 4.0

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()
