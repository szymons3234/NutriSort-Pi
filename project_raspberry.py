from ultralytics import YOLO
import cv2
import time
import RPi.GPIO as GPIO

SERVO_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz serwo 
servo.start(6)  # zamknięta pozycja

def open_servo():
	time.sleep(1)
	servo.ChangeDutyCycle(9.6)  # otwórz (90 stopni)
	time.sleep(3)
	servo.ChangeDutyCycle(6)  # zamknij
	time.sleep(1)


model = YOLO('best2.pt')
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

fps = 30
frame_time = 1 / fps
for _ in range(5):
    cap.read()

frame_count = 0
detection_interval = 10
last_annotated_frame = None


circle_center = (320, 240)
circle_radius = 180  # promień okr w środ.
nut_class_id = 0

  while True:
    start_time = time.time()
    ret, frame = cap.read()
    if not ret:
         break

    frame_count += 1

        # Co N klatek detekcja (po to aby tak nie cieło)
        if frame_count % detection_interval == 0:
            results = model.predict(frame, imgsz=128, verbose=False)
            annotated_frame = results[0].plot()

            boxes = results[0].boxes
            if boxes is not None:
                for box in boxes:
                    cls = int(box.cls[0])
                    if cls != nut_class_id:
                        continue  # pomijaj inne klasy

                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    obj_center = ((x1 + x2) // 2, (y1 + y2) // 2)

                    dx = obj_center[0] - circle_center[0]
                    dy = obj_center[1] - circle_center[1]
                    dist = (dx**2 + dy**2)**0.5

                    if dist <= circle_radius:
                        print("Podkładka wykryta – otwieram serwo!")
                        open_servo()
                        break

        else:
            annotated_frame = last_annotated_frame if last_annotated_frame is not None else frame

        
        cv2.circle(annotated_frame, circle_center, circle_radius, (0, 0, 255), 2)

        cv2.imshow('Sortownik', annotated_frame)
        last_annotated_frame = annotated_frame

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

        elapsed = time.time() - start_time
        wait_time = frame_time - elapsed
        if wait_time > 0:
            time.sleep(wait_time)

finally:
    cap.release()
    cv2.destroyAllWindows()
    servo.stop()
    GPIO.cleanup()