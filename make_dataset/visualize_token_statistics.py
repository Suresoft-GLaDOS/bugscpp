import json
import numpy as np
import matplotlib.pyplot as plt

def draw_histogram(bug_name):
    # Step 1: Read the JSON file
    with open(f'data/{bug_name}/token_statistics.json') as f:
        data = json.load(f)

    # Step 2: Extract values and buggy function indices
    token_counts = [entry['token_count'] for entry in data]
    locs = [entry['loc'] for entry in data]
    is_bug_indices = [i for i, entry in enumerate(data) if entry['is_bug']]

    # Step 3: Calculate mean and median
    mean_token_count = np.mean(token_counts)
    median_token_count = np.median(token_counts)

    mean_loc = np.mean(locs)
    median_loc = np.median(locs)

    print("Mean:", mean_token_count)
    print("Median:", median_token_count)
    print("Mean:", mean_loc)
    print("Median:", median_loc)

    # Step 4: Plot histograms
    plt.figure(figsize=(10, 5))

    plt.subplot(1, 2, 1)
    plt.hist(token_counts, bins=10, color='blue', alpha=0.7)
    plt.yscale('log')  # Apply logarithmic scale to y-axis
    for index in is_bug_indices:
        plt.axvline(x=token_counts[index], color='red', linestyle='--')  # Mark buggy function with red dashed line
    plt.title('Histogram of Token Count')
    plt.xlabel('Token Count')
    plt.ylabel('Frequency (log scale)')

    plt.subplot(1, 2, 2)
    plt.hist(locs, bins=10, color='green', alpha=0.7)
    plt.yscale('log')  # Apply logarithmic scale to y-axis
    for index in is_bug_indices:
        plt.axvline(x=locs[index], color='red', linestyle='--')  # Mark buggy function with red dashed line
    plt.title('Histogram of Line of Code (LOC)')
    plt.xlabel('LOC')
    plt.ylabel('Frequency (log scale)')

    plt.suptitle(bug_name)
    plt.tight_layout()
    # plt.show()
    plt.savefig(f'data/{bug_name}/token_stats.png')

if __name__ == "__main__":
    draw_histogram('libchewing-1')