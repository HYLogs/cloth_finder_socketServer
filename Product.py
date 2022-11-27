class Product:
    def __init__(self, title, link, image, lprice, imageBytes):
        self.title = title
        self.link = link
        self.image = image
        self.lprice = lprice
        self.imageBytes = imageBytes
        self.detected = dict()
        
    def __str__(self):
        return '&'.join([self.title, self.link, self.image, self.lprice, self.imageBytes])