import argparse
from Benchmarking import Benchmark

parser = argparse.ArgumentParser()
parser.add_argument('--maps_dir', default='/home/rdas/Saliency/results/', type=str)
parser.add_argument('--find_AUCJ', default=True, type=bool)
parser.add_argument('--find_AUCB', default=True, type=bool)
parser.add_argument('--find_shuffled_AUC', default=True, type=bool)
parser.add_argument('--M_value', default=10, type=int)
parser.add_argument('--add_jitter', default=True, type=bool)
args = parser.parse_args()

def getBenchmarkingResults(maps_dir, find_AUC_J, find_AUC_B, find_AUC_shuffled, M, jitter):
    benchmark = Benchmark(maps_dir=maps_dir)
    scores = benchmark.find_scores(find_AUC_J=find_AUC_J, find_AUC_B=find_AUC_B, find_AUC_Shuffled=find_AUC_shuffled, M=M, jitter=jitter)

    if find_AUC_J:
        print(f"AUC_J score: {scores['AUC_J']}")
    if find_AUC_B:
        print(f"AUC_B_score: {scores['AUC_B']}")
    if find_AUC_shuffled:
        print(f"Shuffled AUC score: {scores['AUC_Shufled']}")


if __name__ == "__main__":
    getBenchmarkingResults(maps_dir=args.maps_dir, find_AUC_J=args.find_AUCJ, find_AUC_B=args.find_AUCB, find_AUC_shuffled=args.find_shuffled_AUC, M=args.M_value, jitter=args.add_jitter)