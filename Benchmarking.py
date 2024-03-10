import numpy as np
import matplotlib.pyplot as plt
import os
from PIL import Image
from scipy.ndimage import zoom
from sklearn.metrics import auc

class Benchmark:
    def __init__(self, maps_dir):
        self.maps_dir = maps_dir

        num_of_videos = len(os.listdir(self.maps_dir))

        if num_of_videos == 0:
            raise ValueError("maps_dir cannot be empty")

    def AUC_Judd(self, saliencyMap, fixationMap, jitter=False):
        if not np.any(fixationMap):
            print('no fixationMap')
            return np.nan, None, None, None

        if saliencyMap.shape != fixationMap.shape:
            saliencyMap = zoom(saliencyMap, [fixationMap.shape[0]/saliencyMap.shape[0], fixationMap.shape[1]/saliencyMap.shape[1]], order=0)

        if jitter:
            saliencyMap = saliencyMap.astype(float) + np.random.rand(*saliencyMap.shape) / 10000000

        saliencyMap = (saliencyMap - np.min(saliencyMap)) / (np.max(saliencyMap) - np.min(saliencyMap))

        if np.isnan(saliencyMap).all():
            print('NaN saliencyMap')
            return np.nan, None, None, None

        S = saliencyMap.flatten()
        F = fixationMap.flatten()

        Sth = S[F > 0]
        Nfixations = len(Sth)
        Npixels = len(S)

        allthreshes = np.sort(Sth)[::-1]
        tp = np.zeros(Nfixations+2)
        fp = np.zeros(Nfixations+2)
        tp[0], tp[-1] = 0, 1
        fp[0], fp[-1] = 0, 1

        for i, thresh in enumerate(allthreshes, start=1):
            aboveth = np.sum(S >= thresh)
            tp[i] = i / Nfixations
            fp[i] = (aboveth - i) / (Npixels - Nfixations)

        score = auc(fp, tp)
        allthreshes = np.insert(allthreshes, [0, len(allthreshes)], [1, 0])

        # return score, tp, fp, allthreshes

        return score

    def AUC_Borji(self, saliencyMap, fixationMap, Nsplits=100, stepSize=0.1):
        if np.sum(fixationMap) <= 1:
            print('no fixationMap')
            return np.nan, None, None

        if saliencyMap.shape != fixationMap.shape:
            saliencyMap = zoom(saliencyMap, (fixationMap.shape[0] / saliencyMap.shape[0], fixationMap.shape[1] / saliencyMap.shape[1]), order=0)

        saliencyMap = (saliencyMap - np.min(saliencyMap)) / (np.max(saliencyMap) - np.min(saliencyMap))

        S = saliencyMap.flatten()
        F = fixationMap.flatten()

        Sth = S[F > 0]
        Nfixations = len(Sth)
        Npixels = len(S)

        auc_scores = []
        for _ in range(Nsplits):
            r = np.random.randint(0, Npixels, (Nfixations,))
            randfix = S[r]

            allthreshes = np.flip(np.arange(0, np.max(np.concatenate([Sth, randfix])) + stepSize, stepSize))
            tp = np.zeros(len(allthreshes) + 2)
            fp = np.zeros(len(allthreshes) + 2)
            tp[0], tp[-1] = 0, 1
            fp[0], fp[-1] = 0, 1

            for i, thresh in enumerate(allthreshes, start=1):
                tp[i] = np.sum(Sth >= thresh) / Nfixations
                fp[i] = np.sum(randfix >= thresh) / Nfixations

            auc_scores.append(auc(fp, tp))

        score = np.mean(auc_scores)

        # return score, tp, fp

        return score

    def AUC_shuffled(self, saliencyMap, fixationMap, otherMap, Nsplits=100, stepSize=0.1):
        if not np.any(fixationMap):
            print('no fixationMap')
            return np.nan, None, None

        if saliencyMap.shape != fixationMap.shape:
            saliencyMap = zoom(saliencyMap, [fixationMap.shape[0]/saliencyMap.shape[0], fixationMap.shape[1]/saliencyMap.shape[1]], order=0)

        saliencyMap = (saliencyMap - np.min(saliencyMap)) / (np.max(saliencyMap) - np.min(saliencyMap))

        if np.isnan(saliencyMap).all():
            print('NaN saliencyMap')
            return np.nan, None, None

        S = saliencyMap.flatten()
        F = fixationMap.flatten()
        Oth = otherMap.flatten()

        Sth = S[F > 0]
        ind = np.where(Oth > 0)[0]

        Nfixations = len(Sth)
        Nfixations_oth = min(Nfixations, len(ind))
        auc_scores = []

        for _ in range(Nsplits):
            np.random.shuffle(ind)
            selected_indices = ind[:Nfixations_oth]
            randfix = S[selected_indices]

            allthreshes = np.flip(np.arange(0, max(np.max(Sth), np.max(randfix)) + stepSize, stepSize))
            tp = np.zeros(len(allthreshes) + 2)
            fp = np.zeros(len(allthreshes) + 2)
            tp[0], tp[-1] = 0, 1
            fp[0], fp[-1] = 0, 1

            for i, thresh in enumerate(allthreshes, start=1):
                tp[i] = np.sum(Sth >= thresh) / Nfixations
                fp[i] = np.sum(randfix >= thresh) / Nfixations_oth

            auc_scores.append(auc(fp, tp))

        score = np.mean(auc_scores)

        # return score, tp, fp

        return score

    def create_other_map(self, fixation_maps_list, M=10):
        if M > len(fixation_maps_list):
            raise ValueError(f"M cannot be greater than the number of available fixation maps, {len(fixation_maps_list)} fixation maps available")

        selected_maps_indices = np.random.choice(len(fixation_maps_list), M, replace=False)
        selected_maps = [fixation_maps_list[i] for i in selected_maps_indices]

        selected_maps = [self.extract_image(f) for f in selected_maps]
        selected_maps = np.array(selected_maps)
        OtherMap = np.any(selected_maps, axis=0).astype(int)

        return OtherMap

    def extract_image(self, file_path):
        with Image.open(file_path) as img:
            map = np.array(img.convert('L'))
        return map

    def find_scores(self, find_AUC_J=True, find_AUC_B=True, find_AUC_Shuffled=True, M=10, jitter=True):
        scores_dict = {"AUC_J": None, "AUC_B": None, "AUC_Shufled": None}

        AUC_J_list = []
        AUC_B_list = []
        AUC_Shuffled_list = []

        videos = os.listdir(self.maps_dir)
        videos.sort()
        for video in videos:
            print(f"-------------------------Processing {video}---------------------------")
            fixation_dir = os.path.join(self.maps_dir, video, "fixations")
            saliency_dir = os.path.join(self.maps_dir, video, "saliency")
            fixation_maps_list = [os.path.join(fixation_dir, f) for f in os.listdir(fixation_dir) if f.endswith(".png") or f.endswith(".jpg") or f.endswith(".jpeg")]
            saliency_maps_list = [os.path.join(saliency_dir, f) for f in os.listdir(saliency_dir) if f.endswith(".png") or f.endswith(".jpg") or f.endswith(".jpeg")]

            if find_AUC_J:
                AUC_J = []
                print(f"Calculating AUC_J for {video}")
                for fixation_map_path, saliency_map_path in zip(fixation_maps_list, saliency_maps_list):
                    fixationMap = self.extract_image(fixation_map_path)
                    saliencyMap = self.extract_image(saliency_map_path)
                    AUC_J.append(self.AUC_Judd(fixationMap=fixationMap, saliencyMap=saliencyMap, jitter=jitter))
                auc_scores = np.mean(AUC_J)
                AUC_J_list.append(auc_scores)
                print(f"AUC_J for {video}: {auc_scores}")

            if find_AUC_B:
                AUC_B = []
                print(f"Calculating AUC_B for {video}")
                for fixation_map_path, saliency_map_path in zip(fixation_maps_list, saliency_maps_list):
                    fixationMap = self.extract_image(fixation_map_path)
                    saliencyMap = self.extract_image(saliency_map_path)
                    AUC_B.append(self.AUC_Borji(fixationMap=fixationMap, saliencyMap=saliencyMap))
                auc_scores = np.mean(AUC_B)
                AUC_B_list.append(auc_scores)
                print(f"AUC_B for {video}: {auc_scores}")

            if find_AUC_Shuffled:
                AUC_Shuffled = []
                print(f"Calculating AUC_Shuffled for {video}")
                otherMap = self.create_other_map(fixation_maps_list, M)
                for fixation_map_path, saliency_map_path in zip(fixation_maps_list, saliency_maps_list):
                    fixationMap = self.extract_image(fixation_map_path)
                    saliencyMap = self.extract_image(saliency_map_path)
                    AUC_Shuffled.append(self.AUC_shuffled(saliencyMap=saliencyMap, fixationMap=fixationMap, otherMap=otherMap))
                auc_scores = np.mean(AUC_Shuffled)
                AUC_Shuffled_list.append(auc_scores)
                print(f"AUC_Shuffled for {video}: {auc_scores}\n")

        scores_dict["AUC_J"] = np.mean(AUC_J_list)
        scores_dict["AUC_B"] = np.mean(AUC_B_list)
        scores_dict["AUC_Shufled"] = np.mean(AUC_Shuffled_list)

        return scores_dict