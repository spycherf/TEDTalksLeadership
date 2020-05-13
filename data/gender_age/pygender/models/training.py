# Used on Google's AudioSet, download here: https://www.dropbox.com/s/sqg7az7fja6rqfw/pygender.zip?dl=0

import os
import pickle

import numpy as np
import python_speech_features as mfcc
from scipy.io.wavfile import read
from sklearn import preprocessing
from sklearn.mixture import GaussianMixture


def get_MFCC(sr, audio):
    features = mfcc.mfcc(audio, sr, 0.025, 0.01, 13, appendEnergy=False)
    features = preprocessing.scale(features)
    return features


def main():
    # Path to training data
    source = "C:\\Users\\spych\\Desktop\\pygender\\train_data\\female\\"  # run for each gender

    # Path to save trained model
    dest =  os.path.dirname(__file__)

    files = [os.path.join(source, f) for f in os.listdir(source) if f.endswith(".wav")]
    features = np.asarray(())

    for f in files:
        sr, audio = read(f)
        vector = get_MFCC(sr, audio)
        if features.size == 0:
            features = vector
        else:
            features = np.vstack((features, vector))

    gmm = GaussianMixture(n_components=8, covariance_type="diag", n_init=3, max_iter=200)
    gmm.fit(features)
    pickle_file = f.split("\\")[-2].split(".wav")[0] + ".gmm"

    pickle.dump(gmm, open(dest + pickle_file, "wb"))
    print("Modeling completed for gender:", pickle_file)


if __name__ == "__main__":
    main()
