import argparse
from nsdk.media import NImage, NPixelFormat
from nsdk.biometrics import FaceEngine, NBiometricOperations
from nsdk.licensing import NLicense, NLicenseManager
import cv2
import os
from datetime import datetime
from configparser import ConfigParser



def perform_matching(args):
    if not args.probe_dir:
        print("Probe directory path is not provided")
        return
    
    if not args.enroll_dir:
        print("Enrollee directory path is not provided")
        return

    # =========================================================================
    # TRIAL MODE
    # =========================================================================
    # By default trial is disabled - you have to explicitly set it to enable it.

    # is_trial_mode = True
    is_trial_mode = False
    NLicenseManager.set_trial_mode(is_trial_mode)
    print(f"Trial mode: {is_trial_mode}")

    # =========================================================================

    licenses = "FaceMatcher,FaceClient,FaceExtractor"
    failed = False
    for license in licenses.split(','):
        if not NLicense.obtain("/local", 5000, license):
            # if not NLicense.obtain("D:\\Neurotec_Biometric_13_1_Python_Win_2024-02-13\\Activation\\Licenses", 5000, license):
            print(f"Failed to obtain license: {license}")
            failed = True
        else:
            print(f"License obtained successfully: {license}")

    if failed:
        return

    engine = FaceEngine()
    engine.biometric_engine.faces_minimal_iod = 8
    engine.biometric_engine.faces_confidence_threshold = 1
    engine.biometric_engine.faces_detect_properties = True
    engine.biometric_engine.faces_detect_feature_points = True
    engine.biometric_engine.faces_quality_threshold = 0
    engine.biometric_engine.matching_threshold = 0
    print('faces confidence threshold:',
          engine.biometric_engine.faces_confidence_threshold)
    print('faces detect properties:',
          engine.biometric_engine.faces_detect_properties)
    print('faces detect feature points:',
          engine.biometric_engine.faces_detect_feature_points)
    print('faces quality threshold:',
          engine.biometric_engine.faces_quality_threshold)
    print('matching threshold:', engine.biometric_engine.matching_threshold)

    print(f'{args.probe_dir}')
    print(f'{args.enroll_dir}')
    
    enroll_templates_list = []
    enroll_filenames_list = []
    probe_templates_list = []
    probe_filenames_list = []
    
    
    for enroll_filename in os.listdir(args.enroll_dir):        
        enroll_img = NImage(os.path.join(args.enroll_dir,enroll_filename))
        enroll_filename_noextension = os.path.splitext(enroll_filename)[0]
        enroll_filenames_list.append(enroll_filename_noextension)
        fi, enroll_template = engine.detect_faces(enroll_img,multiple_face=False,operation=NBiometricOperations.CREATE_TEMPLATE)
        
        enroll_templates_list.append(enroll_template[0])
    
        
    print(enroll_filenames_list)
    
    for probe_filename in os.listdir(args.probe_dir):        
        probe_img = NImage(os.path.join(args.probe_dir,probe_filename))
        probe_filename_noextension = os.path.splitext(probe_filename)[0]
        probe_filenames_list.append(probe_filename_noextension)
        _, probe_template = engine.detect_faces(probe_img,multiple_face=False,operation=NBiometricOperations.CREATE_TEMPLATE)
        probe_templates_list.append(probe_template[0])
        
    print(probe_filenames_list)
    
    matching_results = []
    count = 0
    for i in range(0,len(probe_templates_list)):        
        for j in range(0,len(enroll_templates_list)):
            matchscore = engine.match_templates(enroll_templates_list[j],probe_templates_list[i])
            print(f"score:{matchscore}")
            matching_result = probe_filenames_list[i]+"_"+enroll_filenames_list[j]+"_"+f"{matchscore}"
            matching_results.append(matching_result)
            count += 1
            progress_status = round((count)/(len(probe_templates_list)*len(enroll_templates_list))*100,1)
            print(f"matching completion: {progress_status}%")
    
    return matching_results
    
def write_to_file(matching_result):
    filename = f"{datetime.today().date().strftime('%y-%m-%d')}.txt"
    for result in matching_results:
        with open(filename,'a') as file:
            file.write(f"{result}\n")
        
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Face create and verify sample')
    # parser.add_argument('--file_name', type=str, default="", help='file name')
    parser.add_argument('--probe_dir', type=str, default="", help='directory path for probes folder')
    parser.add_argument('--enroll_dir', type=str, default="", help='directory path for enrollees folder')
    args_ = parser.parse_args()
    matching_results = perform_matching(args_)
    write_to_file(matching_results)
