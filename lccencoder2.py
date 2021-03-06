import numpy as np
import time
import os
import cv2
import requests
import json

def gen_Lagrange_coeffs(alpha_s,beta_s):
    U = np.zeros((len(alpha_s), len(beta_s)))
    for i in range(len(alpha_s)):
        for j in range(len(beta_s)):
            cur_beta = beta_s[j];
            den = np.prod([cur_beta - o   for o in beta_s if cur_beta != o])
            num = np.prod([alpha_s[i] - o for o in beta_s if cur_beta != o])
            U[i][j] = num/den 
    return U


def LCC_encoding(X,N,M):
    w,l = X[0].shape
    n_beta = M
    beta_s, alpha_s = range(1,1+n_beta), range(1+n_beta,N+1+n_beta)

    U = gen_Lagrange_coeffs(alpha_s,beta_s)
    X_LCC = []
    for i in range(N):
        X_zero = np.zeros(X[0].shape)
        for j in range(M):
            X_zero = X_zero + U[i][j]*X[j]
        X_LCC.append(X_zero)
    return X_LCC



def task(filelist, pathin, pathout):    
    snapshot_time = filelist[0].partition('_')[2].partition('.')[0]  #store the data&time info 
    
    hdr = {
            'Content-Type': 'application/json',
            'Authorization': None #not using HTTP secure
                                }
    # message for requesting job_id
    payload = {'class_image': 2}
    # address of flask server for class2 is 0.0.0.0:5000 and "post-id" is for requesting id
    url = "http://0.0.0.0:5000/post-id"
    # request job_id
    job_id = requests.post(url, headers = hdr, data = json.dumps(payload))

    # Parameters
    L = 10 # Number of images in a data-batch
    M = 2 # Number of data-batches
    N = 3 # Number of workers (encoded data-batches)
    
    # Dimension of resized image
    width = 400
    height = 400
    dim = (width, height)
    
    
    # Read M batches
    Image_Batch = []
    for j in range(M):
        for i in range(j*L,(j+1)*L):
            img = cv2.imread(os.path.join(pathin, filelist[i])) 
            # resize image
            img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
            img = np.float64(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)) 
            img -= img.mean()
            img /= img.std()
            img_w ,img_l = img.shape
            img = img.reshape(1,img_w*img_l)
            if i == j*L:
                Images = img
            else:
                Images = np.concatenate((Images,img), axis=0)  
        Image_Batch.append(Images)
    
    # Encode M data batches to N encoded data
    En_Image_Batch = LCC_encoding(Image_Batch,N,M)
    
    
    # Save each encoded data-batch i to a csv 
    for i in range(N):
        #np.savetxt(os.path.join(pathout,'job'+str(job_id)+'outlccencoder'+str(i+1)+'_'+snapshot_time+'.csv'), En_Image_Batch[i], delimiter=',')
        np.savetxt(os.path.join(pathout,'lccencoder2_score2'+chr(i+97)+'_'+'job'+str(job_id)+'_'+snapshot_time+'.csv'), En_Image_Batch[i], delimiter=',')
    
    
if __name__ == '__main__': ##THIS IS FOR TESTING - DO THIS
    filelist= ['outclass'+'school'+str(i+1)+'_20200507.jpg' for i in range(20)] 
    task(filelist,'./schoolbus', './Enc_Data') 
