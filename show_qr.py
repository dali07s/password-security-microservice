import base64

qr_base64 = input("Paste the QR Base64 value: ")

image_data = base64.b64decode(qr_base64)

with open("totp_qr.png", "wb") as file:
    file.write(image_data)

print("QR code saved as totp_qr.png")