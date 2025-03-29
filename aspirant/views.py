from django.http import HttpResponse
from django.utils.timezone import now  # ✅ Correct way to import 'now'
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import *
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
import random
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import cv2
import os
import numpy as np
from PIL import Image
import re
from Admin.models import ReadAloud
from difflib import SequenceMatcher
from django.shortcuts import render, get_object_or_404
from .models import Final_Result, AspirantReg, ReadingTestResult
from django.contrib.auth.decorators import login_required
# Create your views here.


def validate_password_strength(password):
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one number.")
    if not re.search(r"[@$!%*?&]", password):
        raise ValidationError("Password must contain at least one special character (e.g., @$!%*?&).")
    return password


def aspirant_registration(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        dob = request.POST.get("dob")
        p_email = request.POST.get("p_email")
        password = request.POST.get("password")
        re_password = request.POST.get("re_password")
        current_date = datetime.now()
        dob = datetime.strptime(dob, "%Y-%m-%d")
        age = current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day))
        print(name, email, mobile, dob, p_email, password, re_password, current_date, age)

        try:
            validate_password_strength(password)
        except ValidationError as e:
            messages.warning(request, str(e))
            return render(request, "aspirant_registration.html")

        if password == re_password:
            if User.objects.filter(username=email).exists():
                messages.warning(request, "Email exist!!!!")

            elif age < 16 and not p_email:
                messages.warning(request, "Parent's email is required for users under 16.")

            elif age < 16 and User.objects.filter(email=p_email).exists():
                messages.warning(request, "Parent's email already exists in the system.")

            else:
                # Generate a unique 9-digit registration ID
                def generate_reg_id():
                    return random.randint(101, 999)

                reg_id = generate_reg_id()

                # Ensure the reg_id is unique
                while AspirantReg.objects.filter(reg_id=reg_id).exists():
                    reg_id = generate_reg_id()

                request.session['reg_id'] = reg_id
                # Hash the password
                user = User.objects.create_user(first_name=name, username=email, password=password, email=p_email)
                user.save()
                aspirant_reg = AspirantReg.objects.create(user=user, dob=dob, mobile=mobile, reg_id=reg_id)
                aspirant_reg.save()
                print(reg_id, "Hello")
                print("Data Inserted")
                return redirect(face_image)

        else:
            messages.warning(request, "Password mismatch")
    return render(request, "aspirant_registration.html")




def face_image(request):
    reg_id = request.session.get('reg_id')
    print(reg_id, "hi")
    if request.method == "POST":

        # Show message to wait for the camera to come
        #     messages.info(request, "Please wait, camera will come now...")

            if not os.path.exists(r"D:/PTEBB/Capture"):
                os.makedirs("D:/PTEBB/Capture")

            faceCascade = cv2.CascadeClassifier(
                "D:/PTEBB/haarcascade_frontalface_default.xml")
            cam = cv2.VideoCapture(0)
            cam.set(3, 640)
            cam.set(4, 480)
            count = 0

            print("\n [INFO] Initializing face capture. Look the camera and wait ...")

            # # Initial message
            # messages.info(request, "Camera is now on. Please look at the camera...")

            while True:
                ret, img = cam.read()
                # print(img)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = faceCascade.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    count += 1
                    # Save the captured image into the images directory

                    cv2.imwrite(
                        "D:/PTEBB/Capture/" + str(
                            reg_id) + '.' + str(count) + ".jpg", gray[y:y + h, x:x + w])
                    cv2.imshow('image', img)
                # Press Escape to end the program.
                k = cv2.waitKey(100) & 0xff
                if k < 60:
                    break
                # Take 60 face samples and stop video. You may increase or decrease the number of images.
                # The more is better while training the model.
                elif count >= 60:
                    break

            print("\n [INFO] Exiting Program.")
            cam.release()
            cv2.destroyAllWindows()

            # # Notify that the camera has stopped and training is going on
            # messages.warning(request, "Training faces... Please Wait...!!!")

            path = "D:/PTEBB/Capture"
            recognizer = cv2.face.LBPHFaceRecognizer_create()

            # Haar cascade file

            def getImagesAndLabels(path):
                imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
                faceSamples = []
                ids = []
                for imagePath in imagePaths:
                    #         print(imagePath)
                    # convert it to grayscale
                    PIL_img = Image.open(imagePath).convert('L')
                    img_numpy = np.array(PIL_img, 'uint8')
                    id = int(os.path.split(imagePath)[-1].split(".")[0])
                    faces = faceCascade.detectMultiScale(img_numpy)
                    for (x, y, w, h) in faces:
                        faceSamples.append(img_numpy[y:y + h, x:x + w])
                        ids.append(id)

                return faceSamples, ids

            print("\n[INFO] Training faces...")

            faces, ids = getImagesAndLabels(path)
            print(ids)
            recognizer.train(faces, np.array(ids))
            # Save the model into the current directory.
            recognizer.write('D:/PTEBB/trainer.yml')

            # Final message
            # messages.info(request, "Training complete, redirecting to login.")
            # return JsonResponse({'status': 'success', 'message': 'Training complete!'})

            return redirect(aspirant_login)

    return render(request, "face_image.html", {'reg_id': reg_id})





def aspirant_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        print(email, password)
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            print(f"User {email} logged in successfully.")

            # Store aspirant ID in session for use in face_identity
            request.session['aspirant_id'] = user.id
            print("Email and password validated. Proceed to face recognition.")
            return redirect(face_identity)

        else:
            messages.warning(request, "Invalid email or password")
    return render(request, "aspirant_login.html")




def face_identity(request):
    aspirant_id = request.session.get('aspirant_id')
    print(aspirant_id, "hello")
    if not aspirant_id:
        messages.warning(request, "Session expired. Please log in again.")
        return redirect(aspirant_login)

    # Fetch the student based on session ID
    aspirant = AspirantReg.objects.filter(user_id=aspirant_id).first()
    if not aspirant:
        messages.warning(request, "No student found. Please register.")
        return redirect(aspirant_registration)

    label = ''
    # deep learning code starts
    detector = cv2.CascadeClassifier(
        r"D:/PTEBB/haarcascade_frontalface_default.xml")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("D:/PTEBB/trainer.yml")

    # Load the image
    cam = cv2.VideoCapture(0)
    face_recognized = False  # Track face recognition status

    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = detector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(30, 30))
        if len(faces) == 0:
            cv2.putText(img, "No face detected!", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        for (x, y, w, h) in faces:
            # Predict the ID of the face
            id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
            print(f"Detected ID: {id}, Confidence: {confidence}")
            # Check if confidence is less than 100 ==> "0" is perfect match
            if id == aspirant.reg_id and confidence < 80:
                label = f"Face Verified: Reg ID {id}"
                cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.imshow("Face Recognition", img)
                cam.release()
                cv2.destroyAllWindows()
                return redirect('aspirant_dashboard', aspirant_id=aspirant.id)
            else:
                label = "Unrecognized Face!"
                cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                return redirect(aspirant_registration)
        # Display the frame
        cv2.imshow('Face Recognition', img)

        # Allow quitting the recognition process
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup and redirect if face is not recognized
    cam.release()
    cv2.destroyAllWindows()


def aspirant_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        print(email)
        if User.objects.filter(username=email).exists():
            def generate_otp():
                return random.randint(1000, 9999)

            otp = generate_otp()
            send_mail("OTP for Password Reset", f"Your OTP for forgot password verification is {otp}",
                      settings.EMAIL_HOST_USER, [email])
            request.session['otp'] = otp
            request.session['email'] = email
            request.session['time'] = str(datetime.now())
            return redirect(aspirant_password_reset)
        else:
            messages.warning(request, "Account not Found")
    return render(request, "aspirant_otp.html")


def aspirant_password_reset(request):
    otp = request.session.get('otp')
    print(otp)
    email = request.session.get('email')
    send_time = request.session.get('time')
    send_time = datetime.strptime(send_time, "%Y-%m-%d %H:%M:%S.%f")
    send_time_str = send_time.isoformat()
    current_time = datetime.now()
    duration = current_time - send_time
    print(duration)
    if request.method == "POST":
        otp1 = int(request.POST.get("otp"))
        print(otp1)
        new_password = request.POST.get("password")
        re_password = request.POST.get("re_password")

        try:
            validate_password_strength(new_password)
        except ValidationError as e:
            messages.warning(request, str(e))
            return render(request, "aspirant_password_reset.html")

        if new_password == re_password:
            if otp == otp1 and duration <= timedelta(minutes=5):
                aspirant = User.objects.get(username=email)

                aspirant.password = make_password(new_password)
                aspirant.save()
                return redirect(aspirant_login)
            elif otp == otp1 and duration > timedelta(minutes=5):
                messages.warning(request, "Time exceeded !!")
            else:
                messages.warning(request, "Invalid otp")
        else:
            messages.warning(request, "Password Mismatch")
    return render(request, "aspirant_password_reset.html", {'send_time': send_time_str})

@login_required
def aspirant_dashboard(request, aspirant_id):
    aspirant = AspirantReg.objects.filter(id=aspirant_id).first()
    print(aspirant_id, "HI")
    if not aspirant:
        messages.error(request, "Aspirant not found.")
        return redirect(aspirant_login)
    return render(request, 'aspirant_dashboard.html', {'is_authenticated': True, "aspirant_name": aspirant.user.first_name, "reg_id": aspirant.reg_id})


def aspirant_dashboard1(request):
    return render(request, 'aspirant_dashboard1.html')


def aspirant_logout(request):
    logout(request)
    return redirect(aspirant_dashboard1)

'''-------------------listen_correct_start----------------'''

def l_correct_summary_test(request):
    if 'mcq_listen' not in request.session:
        request.session['mcq_listen'] = 0

    if request.session['mcq_listen'] >= 3:
        messages.warning(request, "You have reached the maximum attempts.")
        return redirect('aspirant_test')

    if 'listen_summary_current_attempt' not in request.session or \
            'question_ids' not in request.session['listen_summary_current_attempt']:
        request.session['listen_summary_current_attempt'] = {
            'current_question': 0,
            'question_ids': [],
        }

    listen_summary_current_attempt = request.session['listen_summary_current_attempt']

    # Start fresh if no questions selected yet
    if not listen_summary_current_attempt['question_ids'] and listen_summary_current_attempt['current_question'] == 0:
        attempted_questions = ListeningCorrectSummarySubmit.objects.filter(student=request.user).values_list(
            'Listening_quetion_id', flat=True)

        available_questions = ListeningCorrectSummary.objects.exclude(id__in=attempted_questions)

        if available_questions.count() < 2:
            messages.warning(request, "No more new questions available. Please try another test.")
            return redirect('aspirant_test')

        selected_questions = random.sample(list(available_questions.values_list('id', flat=True)), 2)
        listen_summary_current_attempt['question_ids'] = selected_questions
        request.session.modified = True

    # Get current question
    try:
        current_q_index = listen_summary_current_attempt['current_question']
        question_id = listen_summary_current_attempt['question_ids'][current_q_index]
        question = ListeningCorrectSummary.objects.get(id=question_id)
    except (IndexError, ListeningCorrectSummary.DoesNotExist, KeyError):
        messages.error(request, "Invalid question sequence. Please restart the test.")
        del request.session['listen_summary_current_attempt']  # Clear corrupted session data
        return redirect('aspirant_test')

    context = {
        "question": question,
        "current_q_number": current_q_index + 1,
        "total_questions": 2
    }
    return render(request, "l_correct_summary_test.html", context)


def mcq_l_submit(request):
    if request.method == "POST":
        session_data = request.session.get('listen_summary_current_attempt', {})

        if not session_data.get('question_ids'):
            messages.error(request, "Invalid test session.")
            return redirect('aspirant_test')

        current_q_index = session_data['current_question']
        question_id = request.POST.get('question_id')
        user_answer = request.POST.get('answer')

        try:
            question = ListeningCorrectSummary.objects.get(id=question_id)

            if question.id != session_data['question_ids'][current_q_index]:
                raise ValueError("Question mismatch")
        except (ListeningCorrectSummary.DoesNotExist, ValueError):
            messages.error(request, "Invalid question submission.")
            return redirect('aspirant_test')



        print(user_answer)
        print(question.answer)

        score = 1 if user_answer == question.answer else 0

        # Save response
        ListeningCorrectSummarySubmit.objects.create(
            student=request.user,
            Listening_quetion=question,
            mark=score
        )

        # Move to next question
        request.session['listen_summary_current_attempt']['current_question'] += 1

        # Check if the test is completed
        if request.session['listen_summary_current_attempt']['current_question'] >= 2:
            request.session['mcq_listen'] += 1  # Update attempt count correctly
            del request.session['listen_summary_current_attempt']
            messages.success(request, "Test completed successfully!")
            request.session.modified = True
            return redirect('aspirant_test')

        request.session.modified = True
        return redirect('l_correct_summary_test')

    return redirect('aspirant_test')


'''----------------listen_end---------------------'''


def l_fill_blanks_test(request):
    if 'fill_blanks' not in request.session:
        request.session['fill_blanks'] = 0

    if request.session['fill_blanks'] >= 3:
        messages.warning(request, "You have reached the maximum attempts.")
        return redirect('aspirant_test')

    if 'fill_blanks_current_attempt' not in request.session or \
            'question_ids' not in request.session['fill_blanks_current_attempt']:
        request.session['fill_blanks_current_attempt'] = {
            'current_question': 0,
            'question_ids': [],
        }

    fill_blanks_current_attempt = request.session['fill_blanks_current_attempt']

    # Start fresh if no questions selected yet
    if not fill_blanks_current_attempt['question_ids'] and fill_blanks_current_attempt['current_question'] == 0:
        attempted_questions = ListeningFillBlanksSubmit.objects.filter(student=request.user).values_list('question_blank_id', flat=True)

        available_questions = ListeningFillBlanks.objects.exclude(id__in=attempted_questions)

        if available_questions.count() < 3:
            messages.warning(request, "No more new questions available. Please try another test.")
            return redirect('aspirant_test')

        selected_questions = random.sample(list(available_questions.values_list('id', flat=True)), 3)
        fill_blanks_current_attempt['question_ids'] = selected_questions
        request.session.modified = True

    # Get current question
    try:
        current_q_index = fill_blanks_current_attempt['current_question']
        question_id = fill_blanks_current_attempt['question_ids'][current_q_index]
        question = ListeningFillBlanks.objects.get(id=question_id)
    except (IndexError, ListeningFillBlanks.DoesNotExist, KeyError):
        messages.error(request, "Invalid question sequence. Please restart the test.")
        del request.session['fill_blanks_current_attempt']  # Clear corrupted session data
        return redirect('aspirant_test')

    context = {
        "question": question,
        "current_q_number": current_q_index + 1,
        "total_questions": 3
    }

    return render(request, "l_fill_blanks_test.html", context)


def evaluate_answers(user_answers, correct_answers):
    score = 0
    for key in correct_answers:
        if user_answers.get(key, "").strip().lower() == correct_answers[key].strip().lower():
            score += 1
    return score

def fill_in_blank_submit(request):
    if request.method == "POST":
        session_data = request.session.get('fill_blanks_current_attempt', {})

        if not session_data.get('question_ids'):
            messages.error(request, "Invalid test session.")
            return redirect('aspirant_test')

        current_q_index = session_data['current_question']
        question_id = request.POST.get('question_id')


        try:
            question = ListeningFillBlanks.objects.get(id=question_id)

            if question.id != session_data['question_ids'][current_q_index]:
                raise ValueError("Question mismatch")
        except (ListeningFillBlanks.DoesNotExist, ValueError):
            messages.error(request, "Invalid question submission.")
            return redirect('aspirant_test')

        user_answers = {
            "blank1": request.POST.get("blank1", "").strip(),
            "blank2": request.POST.get("blank2", "").strip(),
            "blank3": request.POST.get("blank3", "").strip(),
            "blank4": request.POST.get("blank4", "").strip(),
            "blank5": request.POST.get("blank5", "").strip(),
        }
        correct_answers = question.answers
        result = evaluate_answers(user_answers, correct_answers)

        ListeningFillBlanksSubmit.objects.get_or_create(
            student=request.user,
            question_blank=question,
            mark=result
        )
        request.session['fill_blanks_current_attempt']['current_question'] += 1

        # Check if the test is completed
        if request.session['fill_blanks_current_attempt']['current_question'] >= 3:
            request.session['fill_blanks'] += 1  # Update attempt count correctly
            del request.session['fill_blanks_current_attempt']
            messages.success(request, "Test completed successfully!")
            request.session.modified = True
            return redirect('aspirant_test')

        request.session.modified = True
        return redirect('l_fill_blanks_test')

    return redirect('aspirant_test')

#---------------l_mcq_single_start---------------

def l_mcq_single_test(request):
    if 'l_mcq_single' not in request.session:
        request.session['l_mcq_single'] = 0

    # Check if maximum attempts reached
    if request.session['l_mcq_single'] >= 3:
        messages.warning(request, "You have reached the maximum attempts.")
        return redirect('aspirant_test')

    # Initialize test session if not present
    if 'listen_l_mcq_single' not in request.session or 'question_ids' not in request.session['listen_l_mcq_single']:
        request.session['listen_l_mcq_single'] = {
            'current_question': 0,
            'question_ids': [],
        }

    listen_l_mcq_single = request.session['listen_l_mcq_single']

    # Select new questions if starting fresh
    if not listen_l_mcq_single['question_ids'] and listen_l_mcq_single['current_question'] == 0:
        attempted_questions = ListeningMCQSingleSubmit.objects.filter(student=request.user).values_list('Single_listen_id', flat=True)
        available_questions = ListeningMCQSingle.objects.exclude(id__in=attempted_questions)

        if available_questions.count() < 3:
            messages.warning(request, "No more new questions available. Please try another test.")
            return redirect('aspirant_test')

        selected_questions = random.sample(list(available_questions.values_list('id', flat=True)), 3)
        listen_l_mcq_single['question_ids'] = selected_questions
        request.session.modified = True

    # Retrieve current question
    try:
        current_q_index = listen_l_mcq_single['current_question']
        question_id = listen_l_mcq_single['question_ids'][current_q_index]
        question = ListeningMCQSingle.objects.get(id=question_id)
    except (IndexError, ListeningMCQSingle.DoesNotExist, KeyError):
        messages.error(request, "Invalid question sequence. Please restart the test.")
        del request.session['listen_l_mcq_single']
        request.session.modified = True
        return redirect('aspirant_test')

    context = {
        "question": question,
        "current_q_number": current_q_index + 1,
        "total_questions": 3
    }
    return render(request, "l_mcq_single_test.html", context)


def l_mcq_single_test_submit(request):
    if request.method == 'POST':
        # Retrieve session data safely
        session_data = request.session.get('listen_l_mcq_single', {})

        # Ensure session contains required keys
        if not session_data or 'question_ids' not in session_data or 'current_question' not in session_data:
            messages.error(request, "Invalid test session.")
            return redirect('aspirant_test')

        choice_user = request.POST.get('selected_option')
        current_q_index = session_data['current_question']
        question_id = request.POST.get('q_id')

        if not question_id or not choice_user:
            messages.error(request, "Invalid submission.")
            return redirect('aspirant_test')

        try:
            question = ListeningMCQSingle.objects.get(id=question_id)
            # Verify question is in the current sequence
            if question.id != session_data['question_ids'][current_q_index]:
                raise ValueError("Question mismatch")
        except (ListeningMCQSingle.DoesNotExist, ValueError):
            messages.error(request, "Invalid question submission.")
            return redirect('aspirant_test')

        mark = 1 if choice_user == question.answer else 0

        ListeningMCQSingleSubmit.objects.get_or_create(
            student=request.user,
            Single_listen=question,
            mark=mark
        )

        # Move to the next question
        request.session['listen_l_mcq_single']['current_question'] += 1
        request.session.modified = True

        # Check if the user has completed all questions
        if request.session['listen_l_mcq_single']['current_question'] >= 3:
            # Maintain a separate attempt count
            request.session['listen_l_mcq_single_attempts'] = request.session.get('listen_l_mcq_single_attempts', 0) + 1

            # Clear current session data
            del request.session['listen_l_mcq_single']

            messages.success(request, "Test completed successfully!")
            request.session.modified = True
            return redirect('aspirant_test')

        return redirect('l_mcq_single_test')

    return redirect('aspirant_test')



#---------------------l_mcq_single_end--------------------


def r_mcq_single_test(request):
    if 'attempts' not in request.session:
        request.session['attempts'] = 0

    if request.session['attempts'] >= 3:
        messages.warning(request, "You have reached the maximum attempts for MCQ Single.")
        return redirect(aspirant_test)

        # Select a random passage
    questions = list(ReadMCQSingle.objects.all())
    if not questions:
        messages.error(request, "No questions available.")
        return redirect(aspirant_test)

    last_question_id = request.session.get('last_question_id')

    available_questions = [q for q in questions if q.id != last_question_id]

    if not available_questions:  # If only one question is available, use it
        random_question = questions[0]
    else:
        random_question = random.choice(available_questions)

    request.session['last_question_id'] = random_question.id
    
    context = {
        "passage": random_question.passage,
        "question": random_question.question,
        "choices": [random_question.choice1, random_question.choice2, random_question.choice3, random_question.choice4,
                    random_question.choice5],
        "question_id": random_question.id,
    }
    return render(request, "r_mcq_single_test.html", context)


def submit_mcq_single(request):
    if request.method == "POST":
        question_id = request.POST.get("question_id")
        selected_answer = request.POST.get("answer")
        user = request.user
        aspirant = AspirantReg.objects.get(user=user)

        question = ReadMCQSingle.objects.get(id=question_id)

        # Save the response
        ReadingMCQSingleTest.objects.create(
            student=user.first_name,
            reg_id=aspirant.reg_id,
            question=question,
            answer=selected_answer
        )

        # Check correctness
        if selected_answer == question.answer:
            result, created = ReadingTestResult.objects.get_or_create(student=user.first_name, reg_id=aspirant.reg_id)
            result.mark += 1
            result.save()

        # Increase attempt count
        request.session['attempts'] += 1

        if request.session['attempts'] >= 3:
            return redirect(aspirant_test)

        return redirect(r_mcq_single_test)

    return redirect(aspirant_test)



def r_mcq_multiple_test(request):
    if 'MCQ_multiple' not in request.session:
        request.session['MCQ_multiple'] = 0

    if request.session['MCQ_multiple'] >= 3:
        messages.warning(request, "You have reached the maximum attempts.")
        return redirect('aspirant_test')

    # Get all available questions
    questions = list(ReadMCQMultiple.objects.all())
    if not questions:
        messages.error(request, "No questions available.")
        return redirect('aspirant_test')

    # Get IDs of questions already attempted by the user
    attempted_questions = MCQMultipleSubmit.objects.filter(student=request.user).values_list('Summarize_question_id', flat=True)

    # Filter questions that haven't been attempted
    available_questions = [q for q in questions if q.id not in attempted_questions]

    if not available_questions:
        messages.error(request, "New questions not available.")
        return redirect('aspirant_test')

    # Select a random question
    random_question = random.choice(available_questions)

    context = {
        "passage_id":random_question.id,
        "passage": random_question.passage,
        "question": random_question.question,
        "choices": [
            random_question.choice1,
            random_question.choice2,
            random_question.choice3,
            random_question.choice4,
            random_question.choice5
        ]
    }

    return render(request, "r_mcq_multiple_test.html", context)


def submit_mcq(request):
    if request.method == "POST":
        passage_id = request.POST.get("passage_id")
        selected_choices = request.POST.getlist("selected_choices")  # User-selected answers

        try:
            mcq = ReadMCQMultiple.objects.get(id=passage_id)  # Fetch correct answers

            # Store correct answers as a set (ignoring empty answers)
            correct_answers = {mcq.answer1, mcq.answer2, mcq.answer3} - {None, ""}

            # Convert user-selected choices to a set
            selected_set = set(selected_choices)

            # Calculate score based on correct selections
            score = len(selected_set & correct_answers)  # Count matching answers

            print("Correct Answers:", correct_answers)
            print("User Selected:", selected_set)
            print("Score:", score)

        except ReadMCQMultiple.DoesNotExist:
            score = 0  # If passage not found, return 0

        MCQMultipleSubmit.objects.get_or_create(
            student=request.user,
            Summarize_question=mcq,
            mark=score
        )
        request.session['MCQ_multiple'] += 1
        messages.error(request, "Text Submitted Successfully.")
        return redirect('aspirant_test')  # Redirect after submission

    return redirect('aspirant_test')


'''---------Read_Aloud  Start---------'''

def s_read_aloud_test(request):
    # Check maximum attempts first
    if request.session.get('read_aloud_attempts', 0) >= 3:
        messages.warning(request, "You have reached the maximum attempts for Read Aloud.")
        return redirect('aspirant_test')

    # Initialize session if not exists or fix structure
    current_attempt = request.session.get('current_attempt', {})
    if not current_attempt or 'question_ids' not in current_attempt:
        request.session['current_attempt'] = {
            'current_question': 0,
            'question_ids': [],
        }
        current_attempt = request.session['current_attempt']

    # If starting fresh (current_question 0 and empty question_ids)
    if not current_attempt['question_ids'] and current_attempt['current_question'] == 0:
        # Get available questions
        attempted_questions = Read_aloud_submit.objects.filter(
            student=request.user
        ).values_list('questions', flat=True)

        available_questions = ReadAloud.objects.exclude(id__in=attempted_questions)

        if available_questions.count() < 5:
            messages.warning(request, "No more new questions available. Please try another test.")
            return redirect('aspirant_test')

        # Select and store 5 random questions
        selected_questions = random.sample(list(available_questions.values_list('id', flat=True)), 5)
        current_attempt['question_ids'] = selected_questions
        request.session.modified = True

    # Get current question
    try:
        current_q_index = current_attempt['current_question']
        question_id = current_attempt['question_ids'][current_q_index]
        question = ReadAloud.objects.get(id=question_id)
    except (IndexError, ReadAloud.DoesNotExist, KeyError) as e:
        messages.error(request, "Invalid question sequence. Please restart the test.")
        # Clear corrupted session data
        if 'current_attempt' in request.session:
            del request.session['current_attempt']
        return redirect('aspirant_test')

    context = {
        "question": question,
        "current_q_number": current_q_index + 1,
        "total_questions": 5
    }
    return render(request, 's_read_aloud_test.html', context)






def count_mistakes(original, user_input):
    """Compares the original sentence with user input and determines the score based on 55% accuracy."""
    original_words = original.lower().split()
    user_words = user_input.lower().split()

    total_words = max(len(original_words), len(user_words))
    correct_words = 0

    for i in range(min(len(original_words), len(user_words))):
        if original_words[i] == user_words[i]:
            correct_words += 1  # Exact match
        else:
            similarity = SequenceMatcher(None, original_words[i], user_words[i]).ratio()
            if similarity >= 0.55:  # If similarity is at least 55%, consider it correct
                correct_words += 1

    accuracy = (correct_words / total_words) * 100

    return 3 if accuracy >= 55 else 0  # Accept if accuracy is 55% or more




def submit_text(request):
    if request.method == "POST":
        # Validate session data
        session_data = request.session.get('current_attempt', {})
        if not session_data.get('question_ids'):
            messages.error(request, "Invalid test session.")
            return redirect('aspirant_test')

        current_q_index = session_data['current_question']
        question_id = request.POST.get('q_id')
        user_text = request.POST.get('user_text', '').strip()

        # Validation
        if not question_id or not user_text:
            messages.error(request, "Invalid submission.")
            return redirect('aspirant_test')

        try:
            question = ReadAloud.objects.get(id=question_id)
            # Verify question is in the current sequence
            if question.id != session_data['question_ids'][current_q_index]:
                raise ValueError("Question mismatch")
        except (ReadAloud.DoesNotExist, ValueError):
            messages.error(request, "Invalid question submission.")
            return redirect('aspirant_test')

        # Calculate score
        score = count_mistakes(question.sentence, user_text)

        # Save submission
        Read_aloud_submit.objects.get_or_create(
            student=request.user,
            questions=question,
            defaults={"mark": score}
        )

        # Move to next question
        request.session['current_attempt']['current_question'] += 1

        # Check if completed all questions
        if request.session['current_attempt']['current_question'] >= 5:
            # Update attempt count using the main session key
            request.session['read_aloud_attempts'] = request.session.get('read_aloud_attempts', 0) + 1
            # Clear current attempt
            del request.session['current_attempt']
            messages.success(request, "Test completed successfully!")
            request.session.modified = True
            return redirect('aspirant_test')

        request.session.modified = True
        return redirect('s_read_aloud_test')

    return redirect('aspirant_test')



'''---------Read_Aloud  End---------'''


'''-----------Short_Answer_Start------------'''


def s_short_answer_test(request):
    if request.session.get('short_answer_attempts', 0) >= 3:
        messages.warning(request, "You have reached the maximum attempts for Short Answer.")
        return redirect('aspirant_test')

    # Initialize session if it doesn't exist or structure is broken
    if 'short_answer_current_attempt' not in request.session or \
            'question_ids' not in request.session['short_answer_current_attempt']:
        request.session['short_answer_current_attempt'] = {
            'current_question': 0,
            'question_ids': [],
        }

    short_answer_current_attempt = request.session['short_answer_current_attempt']

    # If starting fresh (current_question is 0 and no question_ids)
    if not short_answer_current_attempt['question_ids'] and short_answer_current_attempt['current_question'] == 0:
        # Get available questions
        attempted_questions = Short_answer_submit.objects.filter(
            student=request.user
        ).values_list('questions', flat=True)

        available_questions = ShortAnswer.objects.exclude(id__in=attempted_questions)

        if available_questions.count() < 5:
            messages.warning(request, "No more new questions available. Please try another test.")
            return redirect('aspirant_test')

        # Select and store 5 random questions
        selected_questions = random.sample(list(available_questions.values_list('id', flat=True)), 5)
        short_answer_current_attempt['question_ids'] = selected_questions
        request.session.modified = True

    # Get current question
    try:
        current_q_index = short_answer_current_attempt['current_question']
        question_id = short_answer_current_attempt['question_ids'][current_q_index]
        question = ShortAnswer.objects.get(id=question_id)
    except (IndexError, ShortAnswer.DoesNotExist, KeyError):
        messages.error(request, "Invalid question sequence. Please restart the test.")
        del request.session['short_answer_current_attempt']  # Clear corrupted session data
        return redirect('aspirant_test')

    context = {
        "question": question,
        "current_q_number": current_q_index + 1,
        "total_questions": 5
    }
    return render(request, 's_short_answer_test.html', context)


def Short_answer_check(question_id, user_text):
    """Compares the original answer with user input and determines the score based on 85% accuracy."""
    user_words = user_text.lower().strip()
    get_answer = ShortAnswer.objects.get(id=question_id)
    correct_mark = 0

    if get_answer.answer.lower().strip() == user_words:
        correct_mark = 1  # Exact match
    else:
        similarity = SequenceMatcher(None, get_answer.answer.lower().strip(), user_words).ratio()
        if similarity >= 0.85:  # If similarity is at least 85%, consider it correct
            correct_mark = 1
    return correct_mark


def short_answer_submit(request):
    if request.method == "POST":
        # Validate session data
        session_data = request.session.get('short_answer_current_attempt', {})
        if not session_data.get('question_ids'):
            messages.error(request, "Invalid test session.")
            return redirect('aspirant_test')

        current_q_index = session_data['current_question']
        question_id = request.POST.get('q_id')
        user_text = request.POST.get('user_text', '').strip()

        # Validation
        if not question_id :
            messages.error(request, "Invalid submission.")
            return redirect('aspirant_test')

        try:
            question = ShortAnswer.objects.get(id=question_id)
            # Verify question is in the current sequence
            if question.id != session_data['question_ids'][current_q_index]:
                raise ValueError("Question mismatch")
        except (ShortAnswer.DoesNotExist, ValueError):
            messages.error(request, "Invalid question submission.")
            return redirect('aspirant_test')

        # Calculate score
        score = Short_answer_check(question_id, user_text)

        # Save submission
        Short_answer_submit.objects.get_or_create(
            student=request.user,
            questions=question,
            defaults={"mark": score}
        )

        # Move to next question
        request.session['short_answer_current_attempt']['current_question'] += 1

        # Check if completed all questions
        if request.session['short_answer_current_attempt']['current_question'] >= 5:
            # Update attempt count using the main session key
            request.session['short_answer_attempts'] = request.session.get('short_answer_attempts', 0) + 1
            # Clear current attempt
            del request.session['short_answer_current_attempt']
            messages.success(request, "Test completed successfully!")
            request.session.modified = True
            return redirect('aspirant_test')

        request.session.modified = True
        return redirect('s_short_answer_test')

    return redirect('aspirant_test')


'''-----------Short_Answer_End------------'''


'''-----------Summarize_passage_start------------'''
def w_summarize_passage_test(request):
    if 'summarize_passage' not in request.session:
        request.session['summarize_passage'] = 0

    if request.session['summarize_passage'] >= 3:
        messages.warning(request, "You have reached the maximum attempts for Summarize.")
        return redirect('aspirant_test')

    # Get all available questions
    questions = list(SummarizePassage.objects.all())
    if not questions:
        messages.error(request, "No questions available.")
        return redirect('aspirant_test')

    # Get IDs of questions already attempted by the user
    attempted_questions = SummarizePassageSubmit.objects.filter(student=request.user).values_list('Summarize_question_id', flat=True)

    # Filter questions that haven't been attempted
    available_questions = [q for q in questions if q.id not in attempted_questions]

    if not available_questions:
        messages.error(request, "New questions not available.")
        return redirect('aspirant_test')

    # Select a random question
    random_question = random.choice(available_questions)

    context = {
        "passage": random_question.passage,
        "question_id": random_question.id,
    }

    return render(request, "w_summarize_passage_test.html", context)





def summarize_submit(request):
    if request.method != "POST":
        return HttpResponse("Invalid request method.", status=405)  # Handle non-POST requests

    question_id = request.POST.get('passage_id')
    user_text = request.POST.get('User_text', '').lower()

    # Validate word count
    words = user_text.split()
    if len(words) < 5 or len(words) > 75:
        messages.error(request, "Your summary must be between 5 and 75 words.")
        return redirect('aspirant_test')

    try:
        summarize_keyword = SummarizePassage.objects.get(id=question_id)
    except SummarizePassage.DoesNotExist:
        messages.error(request, "Invalid question ID.")
        return redirect('aspirant_test')

    # TODO: Add your processing logic here (e.g., evaluation, scoring, saving)

    messages.success(request, "Your summary has been submitted successfully!")
    return redirect('aspirant_test')
# Function to clean and split words
def clean_and_split(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)  # Remove special characters
    return text.lower().split()  # Convert to lowercase & split into words

def process_summary(request, summarize_keyword, user_text):
    keywords = clean_and_split(summarize_keyword.keywords)
    user_words = clean_and_split(user_text)

    # Calculate keyword match percentage
    matched_keywords = [k for k in keywords if k in user_words]
    match_percentage = (len(matched_keywords) / len(keywords)) * 100 if keywords else 0

    # Debugging: Print cleaned data
    print("Cleaned Keywords:", keywords)
    print("User Input Words:", user_words)
    print("Match Percentage:", match_percentage)

    # Determine mark based on match percentage
    mark = 10 if match_percentage >= 70 else 0

    # Save to database
    SummarizePassageSubmit.objects.create(
        Summarize_question=summarize_keyword,
        student=request.user,
        mark=mark
    )

    # Increment session count
    request.session['summarize_passage'] += 1

    messages.success(request, "Summary submitted successfully!")
    return redirect('aspirant_test')

'''-----------Summarize_passage_end------------'''





def aspirant_result(request):
    user = request.user # Calculate latest marks (same as before)
    listening_fill_marks = sum(listening.mark for listening in ListeningFillBlanksSubmit.objects.filter(student=user))
    listening_mcq_marks = sum(listening.mark for listening in ListeningMCQSingleSubmit.objects.filter(student=user))
    listening_summary_marks = sum(listening.mark for listening in ListeningCorrectSummarySubmit.objects.filter(student=user))
    total_listening_marks = listening_fill_marks + listening_mcq_marks + listening_summary_marks
    #print("Listening Marks:", total_listening_marks)

    speaking_loud = sum(read.mark for read in Read_aloud_submit.objects.filter(student=user))
    speaking_short = sum(read.mark for read in Short_answer_submit.objects.filter(student=user))
    total_speaking = speaking_short + speaking_loud

    total_writing = sum(write.mark for write in SummarizePassageSubmit.objects.filter(student=user))

    reading_single = ReadingTestResult.objects.get(student=user.first_name).mark
    reading_multiple = sum(read.mark for read in MCQMultipleSubmit.objects.filter(student=user))
    total_reading = reading_single + reading_multiple
    print(reading_single)
    grand_total = total_writing + total_reading + total_speaking + total_listening_marks

    existing_final = Final_Result.objects.filter(student=user).first()
    marks_changed = False
    # Only create history if marks change
    if existing_final:
        marks_changed = (existing_final.writing != total_writing or existing_final.reading != total_reading or existing_final.speaking != total_speaking or existing_final.listening != total_listening_marks )
    if marks_changed:
        ResultHistory.objects.create(student=user, writing=existing_final.writing,
                                                   reading=existing_final.reading, speaking=existing_final.speaking,
                                                   listening=existing_final.listening,
                                                   total=grand_total,  # Use existing total, not new one
                                                   attempted_on=now() )

    # Update Final_Result (always keep latest marks)
    final, created = Final_Result.objects.update_or_create(
        student=user,
        defaults={
            "writing": total_writing,
            "reading": total_reading,
            "speaking": total_speaking,
            "listening": total_listening_marks,
            "total": grand_total, } )
    # Show only the last attempt in history
    previous_results = ResultHistory.objects.filter(student=user).order_by('-attempted_on')[:1]
    return render(request, "aspirant_result.html", {
        "aspirant_mark": final,
        "previous_results": previous_results})


def aspirant_test(request):

    return render(request,"aspirant_test.html" )

def grammar_checker(request):
    return render(request, 'grammar_checker.html')




