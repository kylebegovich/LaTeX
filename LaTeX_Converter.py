import sys
import os
import time


SQUIGGLES = "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
RUNNING_CONVERSION_MESSAGE = "\nRunning conversion script!\n" + SQUIGGLES + "\n"
SUCCESS_MESSAGE = "Success! Saving..."
BAD_FILE_PATH_MESSAGE = " ~ skipping bad file path ~\n"
END_DOC_STR = "\n\end{document}"
MAKING_OUT_DIR_MESSAGE = "Creating output directory: LaTeX_Outputs/\n\n"
IOERROR_MESSAGE = "Unable to read file under path, or file does not exist.\nIOError for path: "
NOT_ENOUGH_ARGS_ERROR_MESSAGE = "Not enough arguments!\n    usage: python3 LaTeX_Converter.py <file_path> [files ...]"
BASE_TEXT_NOT_FOUND_ERROR_MESSAGE = "base_text.tex file not found!\nPlease do one of the following:" \
                "\n    Unix: $ curl http://www.kylebegovich.com/wp-content/uploads/2017/11/LaTeX.txt -o base_text.tex" \
                "\n    otherwise: re-install from GitHub"
COMPLETED_MESSAGE = "\nFinished conversion! Find your files with the .tex extension:\n" + SQUIGGLES
OVERWRITE_WARNING = "WARNING!!! There is a file under the same name as the destination of conversion." \
                    "The conversion process will overwrite this file.\nProceed? (y/n)\n"


def does_file_exist(filename):
    return os.path.isfile(filename) or os.path.isfile("LaTeX_Outputs/"+filename)


def reader(filename):
    """Raises IOError if filename does not exist"""
    file = open(filename, 'r')

    corpus = ""
    for line in file:
        corpus += line

    file.close()
    return corpus


def writer(filename, content):
    """WILL OVERWRITE ANY EXISTING FILE!"""
    file = open("LaTeX_Outputs/"+filename, 'w')
    file.write(content)
    file.close()


def starting_process():
    try:
        assert len(sys.argv) >= 2
        if not does_file_exist("base_text.tex"):  # I'm bad, so this is how I handled refactoring this all
            raise IOError
    except AssertionError:
        print(NOT_ENOUGH_ARGS_ERROR_MESSAGE)
        return False
    except IOError:
        print(BASE_TEXT_NOT_FOUND_ERROR_MESSAGE)
        return False

    print(RUNNING_CONVERSION_MESSAGE)

    if not os.path.exists("LaTeX_Outputs"):  # verify output directory
        print(MAKING_OUT_DIR_MESSAGE)
        os.makedirs("LaTeX_Outputs")

    return True


def pre_process(corpus):

    tab_size = -1

    for line in corpus.split("\n"):
        if len(line) > 4 and line[0] == ' ':
            for i in range(min(len(line), 8)):
                if line[i] == '*':
                    tab_size = i
                    break
                elif not line[i] == ' ':
                    i = len(line)
            if not tab_size == -1:
                break
    return tab_size


def converter(input_file_path):
    base = reader("base_text.tex")\
        .replace("replace_with_title", input_file_path.split("/")[-1].split(".")[0].upper())\
        .replace("replace_with_date", time.strftime("%d/%m/%Y"))

    new = reader(input_file_path)
    arr = new.split('\n')
    out_arr = list()
    heading_cutoff = 30

    tab_size = pre_process(new)

    if 1 < len(arr[0]) < heading_cutoff:
        out_arr.append("\section*{%s}" % arr[0])
    else:
        out_arr.append(arr[0])

    list_depth = 0  # way to track how deep down a nested list we are
    enumr8 = False
    itemize = False
    for i in range(1, len(arr)):
        if len(arr[i]) == 0:    # add a line break
            if list_depth > 0:
                if enumr8:
                    for j in range(list_depth, 0, -1):
                        out_arr.append("\end{enumerate}")
                elif itemize:
                    for j in range(list_depth, 0, -1):
                        out_arr.append("\end{itemize}")
                list_depth = 0
            enumr8 = False
            itemize = False

        elif arr[i][0] == '1':  # beginning of numbered list
            enumr8 = True
            out_arr.append("\\begin{enumerate}")
            out_arr.append("\item " + arr[i][3:])
            list_depth = 1

        elif enumr8:
            tabs_over = 0
            for j in range(0, len(arr[i]), tab_size):
                if not arr[i][j] == ' ':
                    tabs_over = j // tab_size

            #print(tabs_over, list_depth, arr[i])
            if tabs_over >= list_depth:
                #print("right", tabs_over, list_depth, tabs_over-list_depth+1)
                for k in range(tabs_over-list_depth+1):
                    out_arr.append("\\begin{enumerate}")

            elif tabs_over < list_depth-1:
                #print("left", tabs_over, list_depth, list_depth-tabs_over)
                for k in range(list_depth-tabs_over-1):   # check this argument
                    out_arr.append("\end{enumerate}")

            out_arr.append("\item " + arr[i].lstrip()[3:])
            list_depth = tabs_over + 1

        elif itemize:
            tabs_over = 0
            for j in range(0, len(arr[i]), tab_size):
                if arr[i][j] == '*':
                    tabs_over = j // tab_size

            if tabs_over >= list_depth:
                #print("right", tabs_over, list_depth, tabs_over-list_depth+1)
                for k in range(tabs_over-list_depth+1):
                    out_arr.append("\\begin{itemize}")

            elif tabs_over < list_depth-1:
                #print("left", tabs_over, list_depth, list_depth-tabs_over)
                for k in range(list_depth-tabs_over-1):   # check this argument
                    out_arr.append("\end{itemize}")

            out_arr.append("\item " + arr[i].lstrip().lstrip('*'))
            list_depth = tabs_over + 1
        elif arr[i][0] == "*":  # part of left-most bulleted list
            if not itemize:
                itemize = True
                out_arr.append("\\begin{itemize}")
            out_arr.append("\item " + arr[i].lstrip("*"))
            list_depth = 1

        elif arr[i-1] == "" and len(arr[i]) < heading_cutoff:  # add a heading
            out_arr.append("\subsection*{%s}" % arr[i])

        else:
            out_arr.append(arr[i])

    out_var = ""
    for elem in out_arr:
        out_var += elem + "\n"
    return base + out_var + END_DOC_STR


def main():
    if not starting_process():
        return

    args = list(set(sys.argv[1:]))  # actual filepath arguments, removes repeats and the script name

    force = "-f" in args
    if "-a" in args:
        args = [f for f in os.listdir('.') if os.path.isfile(f) and f[-4:] == ".txt"]

    completed_list = list()

    for filepath in args:

        if not does_file_exist(filepath):
            if not filepath == "-f":
                print(IOERROR_MESSAGE, filepath, "\n" + BAD_FILE_PATH_MESSAGE)
            continue

        file_name = str(filepath).split("/")[-1]
        print("Converting ", file_name, "...")

        corpus = converter(file_name)
        print(SUCCESS_MESSAGE)

        new_file_name = file_name.split(".")[0] + ".tex"
        if does_file_exist(new_file_name) and not force:
            response = input(OVERWRITE_WARNING)
            if response == "y" or response == "Y":
                print("Overwritting", new_file_name)
            else:
                print("Skipping", new_file_name)
                continue

        writer(new_file_name, corpus)
        print()
        completed_list.append(new_file_name)




    # finish program and print converted files
    print(COMPLETED_MESSAGE)
    [print("LaTeX_Outputs/"+elem) for elem in completed_list]
    print("~~~\n")


main()
