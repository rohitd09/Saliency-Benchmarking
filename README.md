# Video Saliency Benchmarking

This repository aims to benchmark various **video saliency** models using Python. It is inspired by and references another repository, which provides code for these metrics in MATLAB. This repository serves as the Python equivalent for those looking to benchmark saliency models in a more accessible programming environment.

## Calculated Scores

We calculate the following benchmarking scores:

1. AUC Judd
2. AUC Borji
3. AUC Shuffled

## Preparation Before Benchmarking

Please ensure that all saliency maps and fixation maps are organized as follows:

```
└── maps_dir
    ├── fixations     &    saliency 
           ├── images         ├── images
```


Accepted file formats include `.png`, `.jpg`, and `.jpeg`.

## Benchmarking Command

To start the benchmarking process, use the command below:

```bash
python3 run.py --maps_dir /path/to/maps/dir/
```