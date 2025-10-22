import argparse


def main(input_file, output_file):
    print(f"Source file: {input_file}, output file: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The TuringMini compiler")
    parser.add_argument("--source", required=True, type=str, help="The source file")
    parser.add_argument("--output", required=True, type=str, help="Output file name")
    args = parser.parse_args()
    main(args.source, args.output)
