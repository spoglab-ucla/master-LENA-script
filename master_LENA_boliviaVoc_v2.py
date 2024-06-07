import argparse
import os
import pandas as pd
from lxml import etree
import numpy as np

#_______________________________________________________________________________

def extract_time(text):
    # removes PT and S from timestamp string and converts it to float
    return float(text[2:-1])

def parse_its_file(its_file):
    chi_utt = []
    child_info = []
    all_rec_info = []

    xmldoc = etree.parse(its_file)
    its_file_name = its_file[its_file.rfind('/') + 1:its_file.rfind('.')]

    # Extract Child Information
    for seg in xmldoc.iter('ChildInfo'):
        DOB = seg.attrib['dob']
        gender = seg.attrib['gender']
        age = seg.attrib['chronologicalAge'][1:3]
        child_info.append([DOB, gender, age])

    # Extract Recording Information
    recordings = list(xmldoc.iter('Recording'))

    if recordings:
        # Get the first Recording element
        first_recording = recordings[0]
        startClockTime = first_recording.attrib['startClockTime']
        startTimeSecs = first_recording.attrib['startTime'][2:]

        # Get the last Recording element
        last_recording = recordings[-1]
        endClockTime = last_recording.attrib['endClockTime']
        endTimeSecs = last_recording.attrib['endTime'][2:]

        # Append the extracted info to the list
        all_rec_info = [startClockTime, endClockTime, startTimeSecs, endTimeSecs, its_file_name]
    
    # Combine all information
    all_info = child_info[0] + all_rec_info

    # Extract Utterances
    chn_seg_id = 0
    for seg in xmldoc.iter('Segment'):
        seg_spkr = seg.attrib.get('spkr')

        onset = extract_time(seg.attrib['startTime'])
        offset = extract_time(seg.attrib['endTime'])
        duration = offset - onset
        avg_dB = seg.attrib['average_dB']
        peak_dB = seg.attrib['peak_dB']  

        if seg_spkr == "CHN":
            chn_seg_id += 1
            childUttCnt = seg.attrib['childUttCnt']
            childUttLen = seg.attrib['childUttLen']
            childCryVfxLen = seg.attrib['childCryVfxLen']
            chi_utt.append([chn_seg_id, onset, offset, duration, avg_dB, peak_dB, childUttCnt, childUttLen, childCryVfxLen, its_file_name])

    return {
        "child_utterances": chi_utt,
        "combined_info": all_info
    }

#_______________________________________________________________________________

def list_to_csv(list_ts, output_file, output_dir): # to remember intermediaries
    try:
        list_ts.to_csv(os.path.join(output_dir, output_file)) # write dataframe to file
    except Exception as e:
        print(f"Error: An unexpected error occurred while writing {output_file} to csv: {e}")    

#_______________________________________________________________________________

def process_one_file(its_file, child_id, output_dir):
    try:
        parsed_data = parse_its_file(its_file)
    except Exception as e:
        print(f"Failed to parse ITS file {its_file}: {e}")     

    # Process Child Utterances
    try:
        all_chn_timestamps = parsed_data["child_utterances"]
        df_chn = pd.DataFrame(all_chn_timestamps, columns=["seg_id", "onset", "offset", "duration", "avg_dB", "peak_dB", "childUttCnt", "childUttLen", "childCryVfxLen", "its_file_name"])
        df_chn['offset'] = pd.to_numeric(df_chn['offset']) 
        df_chn['seconds'] = ((df_chn['offset'] // 30) * 30) + 30
    except Exception as e:
        print(f"Error: An unexpected error occurred while processing Child Utterances in file {its_file}: {e}")

    # Process Child Information
    try:
        all_info = parsed_data["combined_info"]
        df_info = pd.DataFrame([all_info], columns=["DOB", "gender", "age_mos", "startClockTime", "endClockTime", "startTimeSecs", "endTimeSecs", "its_file_name"])

    except Exception as e:
        print(f"Error: An unexpected error occurred while processing Child Information in file {its_file}: {e}")   

    # Write dataframes to CSV
    list_to_csv(df_chn, f"{child_id}_CHN_timestamps.csv", output_dir)
    list_to_csv(df_info, f"{child_id}_its_info.csv", output_dir)

#_______________________________________________________________________________

def process_directory(directory, output_base):
    processed_files = set()
    for f in sorted(os.listdir(directory)):
        if f.endswith(".its") and f not in processed_files:
            filename, _ = os.path.splitext(f)
            its_file = os.path.join(directory, f)

            child_id = '_'.join(filename.split('_')[-3:]) if len(filename.split('_')[-1]) != 6 else '_'.join(filename.split('_')[-2:])
            output_dir = os.path.join(output_base, f"{child_id}_output")
            
            try:
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                process_one_file(its_file, child_id, output_dir)
                processed_files.add(f)
            except Exception as e:
                print(f"Error: An unexpected error occurred while processing file '{f}': {str(e)}")
                
#_______________________________________________________________________________    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process .its files based on the specified mode.")
    parser.add_argument("-f", "--file", help="Path to a specific .its file to process")
    parser.add_argument("-d", "--directory", help="Directory to process all .its files from")
    parser.add_argument("-o", "--output", help="Output directory for storing the results", default=os.getcwd())

    args = parser.parse_args()

    if args.output:
        if not os.path.exists(args.output):
            os.makedirs(args.output)

    if args.file:
        if os.path.exists(args.file):
            directory, filename = os.path.split(args.file)
            child_id = '_'.join(filename.split('_')[-3:]) if len(filename.split('_')[-1]) != 6 else '_'.join(filename.split('_')[-2:])
            output_dir = os.path.join(args.output, f"{child_id}_output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            process_one_file(args.file, child_id, output_dir)
        else:
            print("Specified file does not exist.")
    elif args.directory:
        if os.path.isdir(args.directory):
            process_directory(args.directory, args.output)
        else:
            print("Specified directory does not exist.")
    else:
        # Process all files in the current directory of the script, use default output as current directory
        process_directory(os.path.dirname(__file__), args.output)