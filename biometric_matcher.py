from nsdk.media import NImage
from nsdk.biometrics import FaceEngine, IrisesEngine, NBiometricOperations
from nsdk.licensing import NLicense, NLicenseManager
import os
import configparser
from typing import List


class BiometricMatcher():

    returnMsg: str

    def __init__(self, args) -> None:
        self.modality = args.modality.lower()
        config = configparser.ConfigParser()
        config.read('config.ini')

        if args.modality.lower() == "face":
            self.modality = args.modality.lower()
            self.engine = FaceEngine()
            self.engine.biometric_engine.faces_minimal_iod = config['FACE']['minimal_iod']
            print(f'{self.modality} minimal iod',
                  self.engine.biometric_engine.faces_minimal_iod)
            self.engine.biometric_engine.faces_confidence_threshold = config[
                'FACE']['confidence_threshold']
            print(f'{self.modality} confidence threshold',
                  self.engine.biometric_engine.faces_confidence_threshold)
            self.engine.biometric_engine.faces_detect_properties = config[
                'FACE']['detect_properties']
            print(f'{self.modality} detect properties',
                  self.engine.biometric_engine.faces_detect_properties)
            self.engine.biometric_engine.faces_detect_feature_points = config[
                'FACE']['detect_feature_points']
            print(f'{self.modality} detect feature points',
                  self.engine.biometric_engine.faces_detect_feature_points)
            self.engine.biometric_engine.faces_quality_threshold = config[
                'FACE']['quality_threshold']
            print(f'{self.modality} quality threshold',
                  self.engine.biometric_engine.faces_quality_threshold)

        elif args.modality.lower() == "iris":
            self.modality = args.modality.lower()
            self.engine = IrisesEngine()
            self.engine.biometric_engine.irises_confidence_threshold = config[
                'IRIS']['confidence_threshold']
            print('iris confidence threshold',
                  self.engine.biometric_engine.irises_confidence_threshold)
            self.engine.biometric_engine.irises_quality_threshold = config[
                'IRIS']['quality_threshold']
            print('iris quality threshold:',
                  self.engine.biometric_engine.irises_quality_threshold)

        else:
            self.modality = None

        self.engine.biometric_engine.matching_threshold = config['ENGINE']['matching_threshold']
        self.probe_filenames_list = []
        self.probe_templates_list = []
        self.enroll_filenames_list = []
        self.enroll_templates_list = []
        self.enroll_dir = args.enroll_dir
        self.probe_dir = args.probe_dir
        returnMsg = f"{self.modality} engine instantiated \nEnrolled Images Dir Path: {self.enroll_dir};\nProbe Images Dir Path: {self.probe_dir}" if self.modality else "Error! No modality is defined!"
        print(returnMsg)

    def perform_matching(self) -> List:

        # =========================================================================
        # TRIAL MODE
        # =========================================================================
        # By default trial is disabled - you have to explicitly set it to enable it.

        # is_trial_mode = True
        is_trial_mode = False
        NLicenseManager.set_trial_mode(is_trial_mode)
        print(f"Trial mode: {is_trial_mode}")

        # =========================================================================
        if self.modality == "face":
            licenses = "FaceMatcher,FaceClient,FaceExtractor"
        if self.modality == "iris":
            licenses = "IrisMatcher,IrisClient,IrisExtractor"
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

        print('matching threshold:',
              self.engine.biometric_engine.matching_threshold)

        self.enroll_filenames_list, self.enroll_templates_list = self.templatize(
            self.enroll_dir)
        self.probe_filenames_list, self.probe_templates_list = self.templatize(
            self.probe_dir)

        return self.get_matching_results()

    def templatize(self, dir_path: str) -> tuple[list, list]:
        templates_list = []
        filenames_list = []
        for filename in os.listdir(dir_path):
            _img = NImage(os.path.join(dir_path, filename))
            filename_noextension = os.path.splitext(filename)[0]
            filenames_list.append(filename_noextension)
            if self.modality == "face":
                fi, enroll_template = self.engine.detect_faces(
                    _img, multiple_face=False, operation=NBiometricOperations.CREATE_TEMPLATE)
            if self.modality == "iris":
                fi, enroll_template = self.engine.detect_iris(
                    _img, operation=NBiometricOperations.CREATE_TEMPLATE)
            templates_list.append(enroll_template[0])
        return filenames_list, templates_list

    def get_matching_results(self) -> list:
        matching_results = []
        count = 0
        for i in range(0, len(self.probe_templates_list)):
            for j in range(0, len(self.enroll_templates_list)):
                matchscore = self.engine.match_templates(
                    self.enroll_templates_list[j], self.probe_templates_list[i])
                print(f"score:{matchscore}")
                matching_result = self.probe_filenames_list[i]+"_" + \
                    self.enroll_filenames_list[j]+"_"+f"{matchscore}"
                matching_results.append(matching_result)
                count += 1
                progress_status = round(
                    (count)/(len(self.probe_templates_list)*len(self.enroll_templates_list))*100, 1)
                print(f"matching completion: {progress_status}%")
        return matching_results
