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
    fan_utt = []
    man_utt = []
    oln_utt = []
    olf_utt = []
    ct_cnt = []
    child_info = []
    all_rec_info = []

    xmldoc = etree.parse(its_file)

    # Extract Child Information
    for seg in xmldoc.iter('ChildInfo'):
        DOB = seg.attrib['dob']
        gender = seg.attrib['gender']
        age = seg.attrib['chronologicalAge'][1:3]
        child_info.append([DOB, gender, age])

    # Extract Recording Information
    for s in xmldoc.iter('Recording'):
        startClockTime = s.attrib['startClockTime']
        endClockTime = s.attrib['endClockTime']
        startTimeSecs = s.attrib['startTime'][2:]
        endTimeSecs = s.attrib['endTime'][2:]
        all_rec_info.append([startClockTime, endClockTime, startTimeSecs, endTimeSecs])
    
     # Combine all information
    all_info = child_info[0] + all_rec_info[0]

    # Extract Utterances
    chn_seg_id = 0
    fan_seg_id = 0
    man_seg_id = 0
    oln_seg_id = 0
    olf_seg_id = 0
    ct_seg_id = 0
    for seg in xmldoc.iter('Segment'):
        seg_spkr = seg.attrib.get('spkr')

        onset = extract_time(seg.attrib['startTime'])
        offset = extract_time(seg.attrib['endTime'])
        duration = offset - onset
        avg_dB = seg.attrib['average_dB']
        peak_dB = seg.attrib['peak_dB']  
        its_file_name = its_file[its_file.rfind('/') + 1:its_file.rfind('.')]    

        if seg_spkr == "CHN":
            chn_seg_id += 1
            childUttCnt = seg.attrib['childUttCnt']
            childUttLen = seg.attrib['childUttLen']
            childCryVfxLen = seg.attrib['childCryVfxLen']
            chi_utt.append([chn_seg_id, onset, offset, duration, avg_dB, peak_dB, childUttCnt, childUttLen, childCryVfxLen, its_file_name])

        elif seg_spkr == "FAN":
            fan_seg_id += 1
            uttCnt = seg.attrib['femaleAdultUttCnt']
            uttLength = seg.attrib['femaleAdultUttLen']
            wordCount = seg.attrib['femaleAdultWordCnt']
            nonSpeechDur = seg.attrib['femaleAdultNonSpeechLen']
            fan_utt.append([fan_seg_id, onset, offset, duration, avg_dB, peak_dB, wordCount, nonSpeechDur, uttCnt, uttLength, its_file_name])

        elif seg_spkr == "MAN":
            man_seg_id += 1
            uttCnt = seg.attrib['maleAdultUttCnt']
            uttLength = seg.attrib['maleAdultUttLen']
            wordCount = seg.attrib['maleAdultWordCnt']
            nonSpeechDur = seg.attrib['maleAdultNonSpeechLen']
            man_utt.append([man_seg_id, onset, offset, duration, avg_dB, peak_dB, wordCount, nonSpeechDur, uttCnt, uttLength, its_file_name])            
        
        elif seg_spkr == "OLN":
            oln_seg_id += 1
            uttCnt = 'NA'
            uttLength = 'NA'            
            wordCount = 'NA'
            nonSpeechDur = 'NA'
            oln_utt.append([oln_seg_id, onset, offset, duration, avg_dB, peak_dB, wordCount, nonSpeechDur, uttCnt, uttLength, its_file_name])

        elif seg_spkr == "OLF":
            olf_seg_id += 1
            uttCnt = 'NA'
            uttLength = 'NA'            
            wordCount = 'NA'
            nonSpeechDur = 'NA'
            olf_utt.append([olf_seg_id, onset, offset, duration, avg_dB, peak_dB, wordCount, nonSpeechDur, uttCnt, uttLength, its_file_name])

        else:
            continue

    # Extract Conversation Turns
    for seg in xmldoc.iter('Conversation'):
        if seg.attrib.get('turnTaking') != '0':
            ct_seg_id += 1
            onset = extract_time(seg.attrib['startTime'])
            offset = extract_time(seg.attrib['endTime'])
            duration = offset - onset
            avg_dB = seg.attrib['average_dB']
            peak_dB = seg.attrib['peak_dB']
            cnt = seg.attrib['turnTaking']
            ct_type = seg.attrib['type']
            femaleAdultInitiation = seg.attrib.get('femaleAdultInitiation', '0')
            maleAdultInitiation = seg.attrib.get('maleAdultInitiation', '0')
            childResponse = seg.attrib.get('childResponse', '0')
            childInitiation = seg.attrib.get('childInitiation', '0')
            femaleAdultResponse = seg.attrib.get('femaleAdultResponse', '0')
            maleAdultResponse = seg.attrib.get('maleAdultResponse', '0')
            adultWordCnt = seg.attrib.get('adultWordCnt', '0')
            femaleAdultWordCnt = seg.attrib.get('femaleAdultWordCnt', '0')
            maleAdultWordCnt = seg.attrib.get('maleAdultWordCnt', '0')
            femaleAdultUttCnt = seg.attrib.get('femaleAdultUttCnt', '0')
            maleAdultUttCnt = seg.attrib.get('maleAdultUttCnt', '0')
            femaleAdultUttLen = seg.attrib.get('femaleAdultUttLen', 'P0.00S')
            maleAdultUttLen = seg.attrib.get('maleAdultUttLen', 'P0.00S')
            femaleAdultNonSpeechLen = seg.attrib.get('femaleAdultNonSpeechLen', 'P0.00S')
            maleAdultNonSpeechLen = seg.attrib.get('maleAdultNonSpeechLen', 'P0.00S')
            childUttCnt = seg.attrib.get('childUttCnt', '0')
            childUttLen = seg.attrib.get('childUttLen', 'P0.00S')
            childCryVfxLen = seg.attrib.get('childCryVfxLen', 'P0.00S')
            TVF = seg.attrib.get('TVF', 'P0.00S')
            FAN = seg.attrib.get('FAN', 'P0.00S')  
            ct_cnt.append([
                ct_seg_id, onset, offset, duration, avg_dB, peak_dB, cnt, its_file_name,
                ct_type, femaleAdultInitiation, maleAdultInitiation, childResponse, childInitiation,
                femaleAdultResponse, maleAdultResponse, adultWordCnt, femaleAdultWordCnt,
                maleAdultWordCnt, femaleAdultUttCnt, maleAdultUttCnt, femaleAdultUttLen,
                maleAdultUttLen, femaleAdultNonSpeechLen, maleAdultNonSpeechLen, childUttCnt,
                childUttLen, childCryVfxLen, TVF, FAN
            ])

    return {
        "child_utterances": chi_utt,
        "female_utterances": fan_utt, 
        "male_utterances": man_utt, 
        "overlapping_near_utterances": oln_utt, 
        "overlapping_far_utterances": olf_utt, 
        "conversation_turns": ct_cnt,
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
        df_chn['seconds'] = ((df_chn['offset'] // 60) * 60) + 60
        df_chn['child_id'] = child_id
    except Exception as e:
        print(f"Error: An unexpected error occurred while processing Child Utterances in file {its_file}: {e}")

    # Process Female Utterances
    try:
        all_fan_timestamps = parsed_data["female_utterances"]
        df_fan = pd.DataFrame(all_fan_timestamps, columns=["seg_id", "onset", "offset", "duration", "avg_dB", "peak_dB", "wordCount", "nonSpeechDur", "uttCnt", "uttLength", "its_file_name"])
        df_fan['offset'] = pd.to_numeric(df_fan['offset']) 
        df_fan['seconds'] = ((df_fan['offset'] // 60) * 60) + 60
        df_fan['child_id'] = child_id    
    except Exception as e:
        print(f"Error: An unexpected error occurred while processing Female Utterances in file {its_file}: {e}")

    # Process Male Utterances
    try:
        all_man_timestamps = parsed_data["male_utterances"]
        df_man = pd.DataFrame(all_man_timestamps, columns=["seg_id", "onset", "offset", "duration", "avg_dB", "peak_dB", "wordCount", "nonSpeechDur", "uttCnt", "uttLength", "its_file_name"])
        df_man['offset'] = pd.to_numeric(df_man['offset']) 
        df_man['seconds'] = ((df_man['offset'] // 60) * 60) + 60
        df_man['child_id'] = child_id    
    except Exception as e:
        print(f"Error: An unexpected error occurred while processing Male Utterances in file {its_file}: {e}")  

    # Process Overlapping Near Utterances
    try:
        all_oln_timestamps = parsed_data["overlapping_near_utterances"]
        df_oln = pd.DataFrame(all_oln_timestamps, columns=["seg_id", "onset", "offset", "duration", "avg_dB", "peak_dB", "wordCount", "nonSpeechDur", "uttCnt", "uttLength", "its_file_name"])
        df_oln['offset'] = pd.to_numeric(df_oln['offset']) 
        df_oln['seconds'] = ((df_oln['offset'] // 60) * 60) + 60
        df_oln['child_id'] = child_id    
    except Exception as e:
        print(f"Error: An unexpected error occurred while processing Overlapping Near Utterances in file {its_file}: {e}")

    # Process Overlapping Far Utterances
    try:
        all_olf_timestamps = parsed_data["overlapping_far_utterances"]
        df_olf = pd.DataFrame(all_olf_timestamps, columns=["seg_id", "onset", "offset", "duration", "avg_dB", "peak_dB", "wordCount", "nonSpeechDur", "uttCnt", "uttLength", "its_file_name"])
        df_olf['offset'] = pd.to_numeric(df_olf['offset']) 
        df_olf['seconds'] = ((df_olf['offset'] // 60) * 60) + 60
        df_olf['child_id'] = child_id    
    except Exception as e:
        print(f"Error: An unexpected error occurred while processing Overlapping Far Utterances in file {its_file}: {e}")

    # Process Conversation Turns
    try:
        all_ct_timestamps = parsed_data["conversation_turns"]
        df_ct = pd.DataFrame(all_ct_timestamps, columns=["seg_id", "onset", "offset", "duration", "avg_dB", "peak_dB", 
                                                        "convo_count", "its_file_name", "ct_type", "femaleAdultInitiation", 
                                                        "maleAdultInitiation", "childResponse", "childInitiation", 
                                                        "femaleAdultResponse", "maleAdultResponse", "adultWordCnt", 
                                                        "femaleAdultWordCnt", "maleAdultWordCnt", "femaleAdultUttCnt", 
                                                        "maleAdultUttCnt", "femaleAdultUttLen", "maleAdultUttLen", 
                                                        "femaleAdultNonSpeechLen", "maleAdultNonSpeechLen", "childUttCnt", 
                                                        "childUttLen", "childCryVfxLen", "TVF", "FAN"])
        df_ct['offset'] = pd.to_numeric(df_ct['offset']) 
        df_ct['seconds'] = ((df_ct['offset'] // 60) * 60) + 60
        df_ct['child_id'] = child_id
    except Exception as e:
        print(f"Error: An unexpected error occurred while processing Conversation Turns in file {its_file}: {e}")

    # Process Child Information
    try:
        all_info = parsed_data["combined_info"]
        df_info = pd.DataFrame([all_info], columns=["DOB", "gender", "age_mos", "startClockTime", "endClockTime", "startTimeSecs", "endTimeSecs"])
        df_info['child_id'] = child_id
        df_info['filename'] = its_file
    except Exception as e:
        print(f"Error: An unexpected error occurred while processing Child Information in file {its_file}: {e}")   

    # Write dataframes to CSV
    list_to_csv(df_chn, f"{child_id}_CHN_timestamps.csv", output_dir)
    list_to_csv(df_fan, f"{child_id}_FAN_timestamps.csv", output_dir)
    list_to_csv(df_man, f"{child_id}_MAN_timestamps.csv", output_dir)
    list_to_csv(df_oln, f"{child_id}_OLN_timestamps.csv", output_dir)
    list_to_csv(df_olf, f"{child_id}_OLF_timestamps.csv", output_dir)
    list_to_csv(df_ct, f"{child_id}_CTC_timestamps.csv", output_dir)
    list_to_csv(df_info, f"{child_id}_its_info.csv", output_dir)

#_______________________________________________________________________________

def process_directory(directory, output_base):
    processed_files = set()
    for f in sorted(os.listdir(directory)):
        if f.endswith(".its") and f not in processed_files:
            if f[-6] == '_':
                print(f"Warning: Multiple files might be present for the same day. Skipping file {f}")
                continue

            filename, _ = os.path.splitext(f)
            its_file = os.path.join(directory, f)
            child_id = filename[:7]
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
            child_id = filename[:7]
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