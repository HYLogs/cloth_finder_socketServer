from PIL import Image
import io
import json

color_dict = {'black':'검정','white':'흰색','gray':'회색','red':'빨강','pink':'분홍','orange':'오렌지색',
            'beige':'베이지','brown':'브라운','yellow':'노랑','green':'초록','kakky':'카키','mint':'민트',
            'blue':'파랑','navy':'네이비','skyblue':'하늘색','purple':'보라색','lavander':'라벤더색',
            'wine':'와인색','neon':'형광','gold':'금색','silver':'은색'}
category_dict = {'top':'탑','blouse':'블라우스','Tshirt':'티셔츠','neatwear':'니트','shirt':'셔츠',
            'bratop':'브라탑','hoodTshirt':'후드티','jeans':'청바지','pants':'바지','skirt':'스커트',
            'leggings':'레깅스','joggerpants':'조거팬츠','coat':'코트','jacket':'재킷','jumper':'점퍼',
            'padding':'패딩','vest':'조끼','kardigan':'가디건','zipup':'집업','dress':'드레스','jumpsuit':'점프수트'}
    
def bytesToImagePath(byte, path):
        with open(path, "wb") as f:
            f.write(byte)
        image1 = Image.open(path)
        image1 = image1.convert('RGB')
        image1_re = image1.resize((800,800))
        image1_re.save(path)

def exportModel(img_input_bytes, model_path):
    
    # initialize
    model = model_path
    model.eval()
    dict_result = dict()

    data = img_input_bytes
    target_img = Image.open(io.BytesIO(data))
    results = model(target_img,size=640)
    data = results.pandas().xyxy[0].to_json(orient="index") 
    data_json = json.loads(data)
      

    # save detected result
    for k in data_json:
        label = data_json[k]['name'].split(" ")
        color = color_dict[label[0]]
        cloth = category_dict[label[1]]
        
        target_area = (data_json[k]['xmin'], data_json[k]['ymin'], data_json[k]['xmax'], data_json[k]['ymax']) # find coordinate for crop target image
        target_img.crop(target_area)
        
        img_byte_arr = io.BytesIO()
        target_img.save(img_byte_arr, format='jpeg')
        
        dict_result[color+ ' ' +cloth]=img_byte_arr.getvalue()

    return dict_result  # output ex) {'Jeans': 'img_path', 'Coat': 'img_path'}