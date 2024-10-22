import cv2
from pyzbar.pyzbar import decode
import time

def capture_and_decode_qrcode():
    # Open external camera, assumed to be device 1 (adjust if necessary)
    cap = cv2.VideoCapture(0)

    # Set camera resolution (adjust according to your camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("Unable to open camera. Please check the connection.")
        return

    print("Camera started, waiting to detect QR code...")

    while True:
        # Read frame from the camera
        ret, frame = cap.read()

        if not ret:
            print("Failed to read data from camera.")
            break

        # Convert to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
        
        # Apply threshold to enhance contrast
        _, binary_frame = cv2.threshold(blurred_frame, 100, 255, cv2.THRESH_BINARY)

        # Use pyzbar to decode QR codes in the processed frame
        decoded_objects = decode(binary_frame)

        # If a QR code is detected
        if decoded_objects:
            for obj in decoded_objects:
                print("QR code detected!")
                print("QR code data:", obj.data.decode("utf-8"))
                print("QR code type:", obj.type)

            # Save the current frame as an image after detecting QR code
            image_path = "qrcode_detected.jpg"
            cv2.imwrite(image_path, frame)
            print(f"Image saved at {image_path}")
            break  # Exit loop after QR code detection

        # Pause for a short time to reduce CPU usage
        time.sleep(0.1)

    # Release camera resources
    cap.release()

# Wait for user to input a number
while True:
    try:
        user_input = int(input("Please enter a number, then press Enter to start the camera for QR code recognition: "))
        print(f"Entered number is: {user_input}")
        break
    except ValueError:
        print("Invalid input, please enter a valid number.")

# Start QR code detection after user input
capture_and_decode_qrcode()
