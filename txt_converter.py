import sys
import time


def reader(filename):
    file_text = open(filename, 'r')

    corpus = ""
    for line in file_text:
        corpus += line

    file_text.close()
    return corpus


def main():
    assert len(sys.argv) >= 2
    print("Running conversion script!")

    for i in range(1, len(sys.argv)):
        print("\nConverting ", sys.argv[i])


    print(time.strftime("%d/%m/%Y"))



main()