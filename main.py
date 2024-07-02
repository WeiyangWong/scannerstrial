import argparse
from datetime import datetime
from biometric_matcher import BiometricMatcher
import os
import configparser


def InstantiateMatcher(args):
    if not args.modality:
        print("Modality is not provided")
        return
    if not args.probe_dir:
        print("Probe directory path is not provided")
        return
    if not args.enroll_dir:
        print("Enrollee directory path is not provided")
        return
    return BiometricMatcher(args)


def write_to_file(matching_result, args):
    config = configparser.ConfigParser()
    config.read('config.ini')
    results_folder_path = config['DIR']['results']
    os.makedirs(results_folder_path, exist_ok=True)
    filename = f"{results_folder_path}\{args.modality}_{datetime.now().strftime('%y-%m-%d-%H-%M-%S')}.txt"
    for result in matching_results:
        with open(filename, 'a') as file:
            file.write(f"{result}\n")
    print("---Results written to file---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Face create and verify sample')
    parser.add_argument('--modality', type=str, default="",
                        help='modality for matching')
    parser.add_argument('--probe_dir', type=str, default="",
                        help='directory path for probes folder')
    parser.add_argument('--enroll_dir', type=str, default="",
                        help='directory path for enrollees folder')
    args_ = parser.parse_args()

    matcher = InstantiateMatcher(args_)
    matching_results = matcher.perform_matching()
    write_to_file(matching_results, args_)
