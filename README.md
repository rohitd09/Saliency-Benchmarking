# Video Saliency Benchmarking

This repository aims to benchmark various **video saliency** models using Python. It is inspired by and references another [repository](https://github.com/cvzoya/saliency), which provides code for these metrics in MATLAB. This repository serves as the Python equivalent for those looking to benchmark saliency models in a more accessible programming environment.

## Calculated Scores

We calculate the following benchmarking scores:

I. Location Based Metric

1. AUC Judd
2. AUC Borji
3. AUC Shuffled

II. Distribution Based Metric

1. KL Dievergence

## Results on DHF1K

Here are the following results when comparing the fixations and maps of DHF1K dataset. The dataset can be downloaded from this [link](https://github.com/wenguanwang/DHF1K).

| Metric | Score |
|----------|----------|
| AUC Judd | 0.9927 |
| AUC Borji | 0.9859 |
| AUC Shuffled | 0.9129 |
| KL Divergence | 3.6754 |

Results for Linear Correlation Coefficient will be updated soon.

## Preparation Before Benchmarking

Please ensure that all saliency maps and fixation maps are organized as follows:

```
└── path/to/maps_dir
    ├── fixations     &    saliency 
           ├── images         ├── images
```


Accepted file formats include `.png`, `.jpg`, and `.jpeg`.

## Benchmarking Command

To start the benchmarking process, use the command below:

```bash
python3 run.py --maps_dir /path/to/maps/dir/
```

The 3 AUC metric scores is calculated by default and can be disabled if required. Refer to the below arguments to run a custom benchmarking test.

```
--find_AUCJ (Default = True)
--find_AUCB (Default = True)
--find_shuffled_AUC (Default = True)
--find_KLdiv (Default = False)
--M_value (Default = 10)
--add_jitter (Default = True)
```

M_value is the number of random fixation maps used to find AUC shuffled
add_jitter adds a small noise to each pixel of saliency map to prevent duplicate values in saliency maps if there are any.

## Conclusion

The following metrics are crucial in benchmarking saliency models, and more benchmarking metrics will be added in the future.