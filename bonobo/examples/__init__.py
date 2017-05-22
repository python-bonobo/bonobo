def require(package, requirement=None):
    requirement = requirement or package

    try:
        return __import__(package)
    except ImportError:
        from colorama import Fore, Style
        print(
            Fore.YELLOW,
            'This example requires the {!r} package. Install it using:'.
            format(requirement),
            Style.RESET_ALL,
            sep=''
        )
        print()
        print(
            Fore.YELLOW,
            '  $ pip install {!s}'.format(requirement),
            Style.RESET_ALL,
            sep=''
        )
        print()
        raise
