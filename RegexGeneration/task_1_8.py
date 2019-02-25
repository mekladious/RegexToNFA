import argparse
import re

def task_1_8():
    output_file = open("task_1_8_result.txt", "w+")

    with open(args.file, "r") as file:
        for line in file:
            repl = re.sub(
                pattern="struct\s+(?P<structure_name>\w+)\s+\*(?P<structure_ptr>\w+)",
                repl="struct \\1 *\\2_new",
                string=line.replace('\n','')
            )
            output_file.write(repl+'\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True, description='Sample Commandline')

    parser.add_argument('--file', action="store", help="path of file to take as input", nargs="?",
                        metavar="file")

    args = parser.parse_args()

    print(args.file)

    task_1_8()
