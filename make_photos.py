import cv2
import os

output_dir = "zdjecia"
os.makedirs(output_dir, exist_ok=True)


counter = len([name for name in os.listdir(output_dir) if name.startswith("zdj_") and name.endswith(".jpg")])


cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Nie można otworzyć kamery")
    exit()

print("Naciśnij 's', aby zapisać zdjęcie. Naciśnij 'q', aby wyjść.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Nie udało się przechwycić klatki")
        break

    cv2.imshow("Kamera", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        counter += 1
        filename = os.path.join(output_dir, f"zdj_{counter}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Zapisano {filename}")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
