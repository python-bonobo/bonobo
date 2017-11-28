if __name__ == '__main__':
    from bonobo.commands import entrypoint
    import sys

    entrypoint(['examples'] + sys.argv[1:])
