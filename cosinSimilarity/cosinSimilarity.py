import tensorflow as tf
import tensorflow_hub as hub
from torch import cosine_similarity
from tensorflow.keras import layers
import numpy as np
from numpy import dot
from numpy.linalg import norm
import PIL.Image as Image
from io import BytesIO 

# url = "https://tfhub.dev/google/imagenet/mobilenet_v2_100_96/feature_vector/5" #클라우드
url = "cosinSimilarity\imagenet_mobilenet_v2_100_96_feature_vector_5" #로컬
IMAGE_RES = 96
model = tf.keras.Sequential([
    hub.KerasLayer(url, input_shape=(IMAGE_RES, IMAGE_RES, 3))
])
    
def cos_sim(A, B):
    return dot(A, B)/(norm(A)*norm(B))

def compare(selectedClass, ditectTargetDict, products):# target 이미지 특징 벡터를 가져옵니다.
    targetBytes = ditectTargetDict[selectedClass]
    grace_hopper = Image.open(BytesIO(targetBytes)).resize((IMAGE_RES, IMAGE_RES))
    grace_hopper = np.array(grace_hopper)/97.0
    data = grace_hopper.reshape(1, 96, 96, 3)

    # compare 이미지 특징 벡터를 가져온 후 코사인 유사도 계산을 한 후 유사도 리스트를 생성
    compares = {}
    for product in products:
        compareBytes = product.detected[selectedClass]
        grace_hopper = Image.open(BytesIO(compareBytes)).resize((IMAGE_RES, IMAGE_RES)).convert('RGB')
        grace_hopper = np.array(grace_hopper)/97.0
        data = np.append(data, grace_hopper.reshape(1, 96, 96, 3), axis=0)
        
    Vectors = model.predict(data)
    TargetVector = Vectors[0]
    CompareVectors = Vectors[1:]
    for product, CompareVector in zip(products, CompareVectors):
        similarity = cos_sim(TargetVector, CompareVector)
        similarity = similarity.item()*100
        compares[similarity] = product
    return compares