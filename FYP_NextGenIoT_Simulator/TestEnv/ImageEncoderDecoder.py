from PIL import Image
from io import BytesIO


out = BytesIO()

with Image.open(rf"FYP_NextGenIoT_Simulator\SNR_BER.png") as img:
    img.save(out, format="png")

image_in_bytes = out.getvalue()

encoded_b2 = "".join([format(n, '08b') for n in image_in_bytes])
print(encoded_b2)
decoded_b2 = [int(encoded_b2[i:i + 8], 2) for i in range(0, len(encoded_b2), 8)]

with open(rf"FYP_NextGenIoT_Simulator\SNR_BER_decoded.png", 'wb') as f:
    f.write(bytes(decoded_b2))