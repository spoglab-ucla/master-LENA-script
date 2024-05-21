# ITS File Processing Script

## Description
This script is designed to parse and process `.its` files, extracting various types of utterance information from these files, and saving outputs as CSV files for further analysis. It supports processing individual files as well as batch processing of all `.its` files within a specified directory.

## Requirements

- Python 3.6 or higher
- Libraries: `pandas`, `lxml`, `argparse`, `os`, `numpy`

Make sure to install the necessary Python packages if not already installed:

```bash
pip install pandas lxml numpy
```

## Usage

### Command Line Arguments

- `-f` or `--file`: Path to a specific `.its` file to process.
- `-d` or `--directory`: Directory to process all `.its` files from.
- `-o` or `--output`: Output directory for storing the results.

If no command line arguments are provided, the script will default to processing all `.its` files located in the same directory as the script and store the results under the current working directory.

### Examples

1. **Processing a Single File:**

   ```bash
   python master_LENA.py -f path/to/your/file.its
   ```

2. **Processing All Files in a Directory:**

   ```bash
   python master_LENA.py -d path/to/your/directory
   ```

### Output

CSV files will be generated in the same directory as the input file(s), under a sub-directory named after the child ID found in the file name. For each `.its` file, the following CSV files will be created:
- `<child_id>_CHN_timestamps.csv`
- `<child_id>_FAN_timestamps.csv`
- `<child_id>_MAN_timestamps.csv`
- `<child_id>_OLN_timestamps.csv`
- `<child_id>_OLF_timestamps.csv`
- `<child_id>_CTC_timestamps.csv`
- `<child_id>_its_info.csv`

## Troubleshooting

Ensure all input `.its` files are well-formed and accessible. Check that your Python environment has the necessary permissions to read from the input locations and write to the output directories.
