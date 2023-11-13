import torch
import torch.nn as nn
from torchvision import transforms
import numpy as np
from numpy import dot
from numpy.linalg import norm
from PIL import Image
from io import BytesIO

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
IMAGE_RES = 224
mean = (0.5592392, 0.5234271, 0.50873935)
std = (0.21591803, 0.21961282, 0.22185005)

testTransform = transforms.Compose([
    transforms.Resize((IMAGE_RES, IMAGE_RES)),          # 사진 파일의 크기가 다르므로, Resize로 맞춰줍니다.
    transforms.ToTensor(), 
    transforms.Normalize(mean,std) # 이미지 정규화
])

# model 불러오기
model = torch.load("./cosinSimilarity/MobileNetV2.pt", map_location=device)
model.to(device)
model.eval()

# 특징 벡터만 필요하기 때문에 classifier는 제거
model.classifier = nn.Sequential()

def cos_sim(A, B):
    return dot(A, B)/(norm(A)*norm(B))

def compare(selectedClass, ditectTargetDict, products):# target 이미지 특징 벡터를 가져옵니다.
    # target Image 추론
    targetBytes = ditectTargetDict[selectedClass]
    img = Image.open(BytesIO(targetBytes))
    inputImg = testTransform(img).to(device).unsqueeze(0)
    out = model(inputImg)
    TargetVector = out.detach().cpu().numpy()[0]
    
    # compare 이미지 특징 벡터를 추론 후 코사인 유사도 계산을 한 후 유사도 리스트를 생성
    compares = {}
    for product in products:
        compareBytes = product.detected[selectedClass]
        img = Image.open(BytesIO(compareBytes))
        inputImg = testTransform(img).to(device).unsqueeze(0)
        out = model(inputImg)
        CompareVector = out.detach().cpu().numpy()[0]
        
        similarity = cos_sim(TargetVector, CompareVector)
        similarity = max(round(similarity * 100, 2), 0)
        compares[similarity] = product
    return compares