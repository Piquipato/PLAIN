try:
    from plainchecker.cli import plainchecker
except ModuleNotFoundError:
    from cli import plainchecker

if __name__ == "__main__":
    plainchecker()