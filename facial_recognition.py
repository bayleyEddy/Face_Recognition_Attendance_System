# date: 4/7/25
# authors: Bayley Eddy & Christito De La Cruz Jr
# description: This code serves as our final project for our introductory python course. We decided to work on a facial recognition software that will store a 
#              picture of a user, analyze it and permit them to access an attendance log if a match is found.

################################################################################################################################################################

# Import needed libraries
import face_recognition                   # for facial recognition like encoding and comparing
import cv2                                # for capturing video and image processing using OpenCV
import numpy as np                        # for numerical operations
import os                                 # file directory and handling, for interacting with the OS 
from datetime import datetime             # for timestamp events like attendance and login
import csv                                # for writing and reading CSV files
from pathlib import Path                  # for handling file paths in an OS-independent way
import time                               # for timestamp & delayed pictures
from cryptography.fernet import Fernet    # for symmetric encryption and decryption

# implement thermal scan
# object detection, add admin account
# get all objects and match all of them


# Define the path to the CSV file for user records
csv_file_path: Path = Path("records.csv")

# Define the path to the picture file
certified_folder: Path = Path("certified")

# Define the path to the CSV file for attendance
csv_attendance_path: Path = Path("attendance.csv")

key_path: Path = Path("secret.key")


#=========================================================================================================================================
# function to generate or load an existing Fernet encryption key
def load_or_create_key() -> bytes:
    """
        Generates or loads an existing Fernet encryption key

        Returns:
        key (bytes): The encryption key
    """
    if not key_path.exists():                       # if the key file does not exist
        key = Fernet.generate_key()                 # generate new encryption key
        with open(key_path, "wb") as key_file:      # write a new key to a file
            key_file.write(key)
    else:
        with open(key_path, "rb") as key_file:      # it reads the key from the file if it exists
            key = key_file.read()
    return key                                      # return the encryption key

#=========================================================================================================================================
# function to create the image directory if it does not exist
def file_creation() -> None:
    """
        Creates the file that contains user images, if the folder does not exist then it is created
    """
    # Checks to see if the certified folder is already created
    if not os.path.exists(certified_folder):     
        # create thew folder to store ther encrypted images 
        os.makedirs(certified_folder)
        print("certified folder..created..")
    else:
        print("certified folder..already exists..")

#=========================================================================================================================================
# function to display the main menu
def menu() -> str:
    """
        Displays a menu for users to select various options from

        Return:
            selection(str): The users selection from the menu
    """
    # Options for user to select from
    options: list[str] = ["1", "2", "3"]

    # loop until a valid option is chosen
    while True:
        print("Please select an options below:")
        print(f"\t1. Existing User")
        print(f"\t2. New User")
        print(f"\t3. Exit")

        # Prompt user to enter a value
        selection: str = input("Enter an option: ")
        # If the menu option if found within the list
        if selection in options:
            # Return the menu option the user selected
            return selection
        else:
            # Error message for incorrect inputs
            print("Error: Please enter a value from the menu above")

#=========================================================================================================================================
# function that generate a new user ID
def user_id() -> int:
    """
        Function to calculate a number that will be assigned to each user

        Returns:
            user_num (int): The user ID number 
    """

    # Check if the file exists
    if not csv_file_path.is_file():
        print("File does not exist ...")
        # Assign first user as 1 if none exist
        return 1
    
    # Open the file in read mode
    with open(csv_file_path, "r") as file:
        reader: csv.DictReader = csv.DictReader(file)  # Read rows as dictionaries
        # Set user counter to 0
        user_num: int = 0
        for row in reader:
            user_num += 1      # count rows (users)
    return user_num + 1        # new ID is total users + 1

#=========================================================================================================================================
# function that collect new user's info and store in a dictionary
def user_info() -> dict[str, str]:
    """
        Collects user info to be stored within csv file

        Returns:
            user_record (dict[str, str]): A dictionary containing basic user information
    """
    # Define the user record dictionary
    user_record: dict[str, str] = {}
    print("Please enter the following pieces of information to create your user account: ")
    # Prompt user for their first name
    user_record["first_name"] = input(f"\tFirst name: ")
    # Prompt user for their last name
    user_record["last_name"] = input(f"\tLast name: ")
    # Prompt user for their email address
    user_record["email"] = input(f"\tEmail address: ")
    # Prompt user for their phone number
    user_record["phone_number"] = input(f"\tPhone number: ")
    # Prompt user for their home address
    user_record["home_address"] = input(f"\tHome address: ")

    return user_record      # return user input as dictionary

#=========================================================================================================================================
# function that write a user record to the CSV file   
def write_csv(records: dict[str, str]) -> None:
    """
        Writes user_record data into the csv file. If the file already exists then a record is appended

        Arg:
            user_record (dict[str, str]): Basic user information passed in
    """

    # Check if the file is being written to for the first time
    first_write: bool = not csv_file_path.is_file()
    # If the file hasn't been written in yet
    if first_write:
    # Open the file in write mode
        with open(csv_file_path, "w") as file:
            field_names: list[str] = list(records.keys())                          # Extract field names from the dictionary
            writer: csv.DictWriter = csv.DictWriter(file, fieldnames=field_names)  # Initialize DictWriter
            writer.writeheader()                                                   # Write header row 
            writer.writerow(records)                                               # Write the record 
    else:
        # Open the file in append mode
        with open(csv_file_path, "a") as file:
            field_names: list[str] = list(records.keys())                          # Extract field names from the dictionary
            writer: csv.DictWriter = csv.DictWriter(file, fieldnames=field_names)  # Initialize DictWriter
            writer.writerow(records)                                               # Write the record

#=========================================================================================================================================
# function that capture and encrypt 10 face images for a new user
def new_user(user_num: int, records: dict[str, str]) -> None:
    """
        Captures and encrypts 10 user images using spacebar. Shows webcam feed with guidance.

        Arg:
            user_num (int): Users ID number
            records (dict[str, str]): A users record
    """
    key = load_or_create_key()      # call the function to load the existing encryption key, 
                                    # create a new one if it doesn't exist, then store the returned key (bytes) in the variable (key)
    cipher = Fernet(key)            # initialize Fernet object for encryption

    video = cv2.VideoCapture(0)         # opens the default webcam
    user_id_check: str = str(user_num)  # convert user number to string
    records["id"] = user_id_check       # add user ID to their records
    write_csv(records)                  # write the record to the CSV file

    personalized_folder = os.path.join(certified_folder, user_id_check)     # folder path for this user's images
    if not os.path.exists(personalized_folder):                             # create the folder if it doesn'e exists
        os.makedirs(personalized_folder)
        print(f"... a folder for you.. been created it has...")

    if not video.isOpened():                    # if the webcam fails to open
        print("Error: Couldn't open camera")    # prints the error message
        return

    # instructions to guide the user for each of photo
    instructions:list = [
        "Look straight",
        "Look to your left",
        "Look to your right",
        "Look up",
        "Look down",
        "Slight tilt to left",
        "Slight tilt to right",
        "Smile slightly",
        "Raise your eyebrows",
        "Close your eyes"
    ]

    photo_count: int = 0        # counter for number of photos taken
    print("Press SPACE to take a photo. Press Q to quit.")

    while photo_count < 10:             # loops until 10 photos are captured
        ret, frame = video.read()       # capture a frame from the webcam; 'ret' is True if successful, 'frame' is the image
        if not ret:                     # if the webcam failed to capture a frame
            print("Failed to capture frame from camera.")       # prints the error message
            break                                               # exit the loop

        # show current instruction
        frame_copy = frame.copy()       # create a copy of the captured frame to draw text on it without modifying the original

        # instruction on top of the frame (Look left and etc)
        cv2.putText(frame_copy, f"{instructions[photo_count]}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        #cv2.putText(
        #frame_copy,                        # the image where the text will appear
        #f"{instructions[photo_count]}",    # instruction from the list based on the photo number
        #(10, 30),                          # position of the text (x=10, y=30 pixels from top-left)
        #cv2.FONT_HERSHEY_SIMPLEX,          # font type
        #0.8,                               # font size
        #(0, 255, 0),                       # text color (Green)
        #2                                  # thickness of the text)
        #)

        # secondary instruction to tell user how to capture or quit
        cv2.putText(frame_copy, "Press SPACE to capture, Q to quit.", (10, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        #cv2.putText(
        #frame_copy,                                # image to draw on
        #"Press SPACE to capture, Q to quit.",      # message text
        #(10, 470),                                 # position (near bottom of frame)
        #cv2.FONT_HERSHEY_SIMPLEX,                  # font type
        #0.6,                                       # font size (slightly smaller)
        #(255, 255, 255),                           # text color (White)
        #1                                          # thickness of the text
        #)

        cv2.imshow("Capture Your Face", frame_copy)  # show frame with instructions

        # display the frame with the instructions overlayed
        key_pressed = cv2.waitKey(1) & 0xFF    # wait for 1 millisecond for a key press, and get the lowest 8 bits of the key code

        if key_pressed == ord(' '):  # if the spacebar is pressed
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")            # get current date and time as a string for file naming
            file_name = f"{user_id_check}_{photo_count+1}_{timestamp}.jpg"      # create a unique file name based on user ID, photo number, and timestamp
            raw_path = os.path.join(personalized_folder, file_name)             # build the full file path for saving the image

            # save the captured frame as an unencrypted JPEG fil
            cv2.imwrite(raw_path, frame)

            # encrypt the saved images
            with open(raw_path, "rb") as original_file:                 # open the just-saved image in binary read mode
                encrypted_data = cipher.encrypt(original_file.read())   # encrypt the image data

            with open(raw_path, "wb") as encrypted_file:                # open the same file in binrary write mode
                encrypted_file.write(encrypted_data)                    # save the encrypt image

            print(f"[{photo_count+1}/10] Encrypted image saved as {raw_path}")      # inform user that the photo was saved and encrypted
            photo_count += 1                                                        # move to the next photo

        elif key_pressed == ord('q'):                   # if the user presses 'q' it exit the program
            print("Exiting photo capture early...")     # prints the exit message
            break

    video.release()             # release the webcam
    cv2.destroyAllWindows()     # close the image window

    # after photo capture is done, inform the user whether all 10 photos were successfully captured
    if photo_count == 10:
        print("All photos captured. You're ready to check in!")
    else:
        print(f"Only captured {photo_count} out of 10 photos.")


#=========================================================================================================================================

def existing_user() -> list[object]:
    """
        Accounts for an existing user, will scan users face and grants them access or denies them

        Returns:
            identifiers(list[object]): A list that contains a boolean value to permit users and the permitted users email
    """
    # Prompt user to enter their email
    user_email: str = input("Please enter your email: ")
    
    # Default camera
    video = cv2.VideoCapture(0)
    # List to hold user IDs
    stored_ids: list[str] = []
    # List to hold encodings
    stored_encodings = []

    # Checks if the user records CSV file exists
    if not csv_file_path.is_file():
        print("ERROR: No user records found")
        return [False, ""]
    
    # Open the file in read mode
    with open(csv_file_path, "r") as file:
        reader: csv.DictReader = csv.DictReader(file)  # Read rows as dictionaries
        # Flag to identify if an email was found
        email_identified: bool = False
        for row in reader:
            # Compare the entered email with the email within each row.
            if row["email"] == user_email:
                print(f"Email found..scanning now...")
                # Store that users id
                id_match = row["id"]
                # Store that users first name
                first_name = row["first_name"]
                # Store that users last name
                last_name = row["last_name"]
                # Set email flag true
                email_identified = True
                # If the email was found then exit
                break
        # If the email was not found then print error message
        if not email_identified:
            print("Access denied: Email not found.")
            return [False, ""]

    # Folder path for folder containing encrypted pictures
    folder_for_user: str = os.path.join(certified_folder, id_match)

    # Load or create key to decrypt
    key = load_or_create_key()
    cipher = Fernet(key)

    # Check to see if the user folder exists
    if os.path.isdir(folder_for_user):
        # Looping through every picture within the folder
        for pic_name in os.listdir(folder_for_user):
            pic_path: str = os.path.join(folder_for_user, pic_name)

            # Decrypt image into memory
            with open(pic_path, "rb") as encrypted_file:
                encrypted_data = encrypted_file.read()
                try:
                    decrypted_data = cipher.decrypt(encrypted_data)
                except Exception as e:
                    print(f"Failed to decrypt {pic_name}: {e}")
                    continue

            # Convert decrypted bytes back to image
            nparr = np.frombuffer(decrypted_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                print(f"Error decoding image: {pic_path}")
                continue

            # Encode the face in the picture
            encodings = face_recognition.face_encodings(img)
            if encodings:
                stored_encodings.append(encodings[0])
                stored_ids.append(id_match)

    # If no encodings found then user is denied entry
    if not stored_encodings:
        print("No data available for user")
        return [False, ""]
    

    # If your camera cannot open then error will print
    if not video.isOpened():
        print("Error: Could not open the camera")
        return [False, ""]
    
    # Take a picture
    ret, frame = video.read()
    # Release the camera once picture taken
    video.release()
    # Close OpenCV windows
    cv2.destroyAllWindows()

    # Checks if the webcam worked as intended
    if not ret:
        print("Error: Couldn't take picture")
        return [False, ""]
    
    # Convert picture from BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Locating faces within the corrected picture
    face_locations = face_recognition.face_locations(rgb_frame)
    # Create encodings for the picture
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # If no faces detected then print error
    if not face_encodings:
        print("No faces detected. Please try again.")
        return [False, ""]
    
    # Compare this encoding with all stored face encodings
    for encoding in face_encodings:
        matches = face_recognition.compare_faces(stored_encodings, encoding)

        # If a match is made
        if any(matches):
            # Welcome the user
            print(f"Welcome, {first_name} {last_name}")
            # Mark the user as present
            take_attendance(user_email)
            # Return required information
            return [True, user_email]
        else:
            # If there aren't any matches then deny user
            print("Access denied")
            return [False, ""]
   
#=========================================================================================================================================
# function to record attendance by saving current time and date to a CSV
def take_attendance(email: str) -> None:
    """
        Records the current date and time of when the attendance was taken

        Args:
            email (str): The email of the signed in user
    """
    # Empty dictionary to store attendance records
    user_attendance_record: dict[str, str] = {}
    # Store users email
    user_attendance_record["email"] = email
    # Store the current date
    user_attendance_record["date"] = datetime.now().strftime("%m-%d-%Y")
    # Store the current time
    user_attendance_record["time"] = datetime.now().strftime("%H:%M:%S")

    # Check if the file is being written to for the first time
    first_write: bool = not csv_attendance_path.is_file()
    # If the file hasn't been written in yet
    if first_write:
    # Open the file in write mode
        with open(csv_attendance_path, "w") as file:
            field_names: list[str] = list(user_attendance_record.keys())  # Extract field names from the dictionary
            writer: csv.DictWriter = csv.DictWriter(file, fieldnames=field_names)  # Initialize DictWriter
            writer.writeheader()  # Write header row 
            writer.writerow(user_attendance_record)  # Write the record 
    else:
        # Open the file in append mode
        with open(csv_attendance_path, "a") as file:
            field_names: list[str] = list(user_attendance_record.keys())  # Extract field names from the dictionary
            writer: csv.DictWriter = csv.DictWriter(file, fieldnames=field_names)  # Initialize DictWriter
            writer.writerow(user_attendance_record)  # Write the record

#=========================================================================================================================================
# function to show all attendance records for a given email
def show_attendance(email: str) -> None:
    """
        Prints all attendance records for the logged in user
        
        Args: 
            email (str): Email of the current logged in user
    """
    # Check if the file exists
    if not csv_attendance_path.is_file():
        print("File does not exist...")
        return
    
    # Open the file in read mode
    with open(csv_attendance_path, "r") as file:
        reader: csv.DictReader = csv.DictReader(file)   # Read rows as dictionaries

        for row in reader:
            #Display the attendance records for the entered email
            if row["email"] == email:
                print(f"\t{row['date']}, {row['time']}")



#=========================================================================================================================================

def attendance_menu() -> str:
    """
        Displays a menu for users that are authorized to record and view attendance

        Return:
            selection(str): The users selection from the menu
    """
    # Options for user to select from
    verified_user_options: list[str] = ["1", "2"]
    # Flag for continuous looping
    option_flag: bool = False
    print("Please select an options below:")
    print(f"\t1. View Attendance")
    print(f"\t2. Exit")
    # Loop for correct user input
    if option_flag == False:
        # Prompt user to enter a value
        selection: str = input("Enter an option: ")
        # If the menu option if found within the list
        if selection in verified_user_options:
            # Change flag to true to break loop
            option_flag = True
            # Return the menu option the user selected
            return selection
        else:
            # Error message for incorrect inputs
            print("Error: Please enter a value from the menu above")




#=========================================================================================================================================


def main() -> None:
    """
        The main function that runs the facial recognition attendance program

        Raise:
            ValueError: If the value entered is not within the range displayed
    """
    try:
        file_creation()
        user_select = menu()

        # First option to login as an existing user
        if user_select == "1":
            user_status: list[object] = existing_user()
            # Store status if a user logged in or not
            verified_user: bool = user_status[0]
            # Store email of successful login
            verified_user_email: str = user_status[1]
            # If a user successfully logged in
            if verified_user == True:
                attendance_options = attendance_menu()
                # Option one to print all of the user's attendance records
                if attendance_options == "1":
                    show_attendance(verified_user_email)
                # Option two to exit the program
                elif attendance_options == "2":
                    print("Good bye.. ")
                    exit()

        # Second option to create a new user
        elif user_select == "2":
            user_id_number = user_id()
            user_records = user_info()
            new_user(user_id_number, user_records)

        # Third option to exit the program
        elif user_select == "3":
            print("goodbye.. for now.. ")
            exit()



    except ValueError as e:
        print("Error: ", e)

if __name__ == "__main__":
    main()

