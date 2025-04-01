from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
import random
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from .models import *
from aspirant.models import *
from django.http import HttpResponse


# Create your views here.


def admin_dashboard(request):

    is_authenticated = request.user.is_authenticated
    return render(request, 'admin_dashboard.html', {'is_authenticated': is_authenticated})


def admin_registration(request):
    # if User.objects.exists():
    #     messages.warning(request, "Registration is not allowed as a user already exists.")
    #     return redirect(admin_login)  # Redirect to home or another page of your choice

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        re_password = request.POST.get("re_password")
        print(name, email, password, re_password)
        if password == re_password:

            if User.objects.filter(username=email).exists():
                messages.warning(request, "Email exist")
            else:
                user = User.objects.create_user(first_name=name, username=email, password=password,
                                                is_superuser=1)
                user.save()
                print("Data Inserted")
                return redirect(admin_dashboard)
        else:
            messages.warning(request, "Password mismatch")
    return render(request, "admin_registration.html")


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            user = User.objects.get(username=user)
            if user.is_superuser is True:
                login(request, user)
                messages.warning(request, message="Logged Successfully")
                print("logged successfully")
                return redirect(admin_dashboard)
        else:
            messages.warning(request, "Account not found")

    return render(request, "admin_login.html", {'is_authenticated': request.user.is_authenticated})


def admin_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if User.objects.filter(username=email).exists():
            def generate_otp():
                return random.randint(1000, 9999)

            otp = generate_otp()
            send_mail("OTP for Password Reset", f"Your OTP for forgot password verification is {otp}",
                      settings.EMAIL_HOST_USER, [email])
            request.session['otp'] = otp
            request.session['email'] = email
            request.session['time'] = str(datetime.now())
            return redirect(admin_password_reset)
        else:
            messages.warning(request, "Account not Found")
    return render(request, "admin_otp.html")


def admin_password_reset(request):
    otp = request.session.get('otp')
    print(otp)
    email = request.session.get('email')
    send_time = request.session.get('time')
    send_time = datetime.strptime(send_time, "%Y-%m-%d %H:%M:%S.%f")
    current_time = datetime.now()
    duration = current_time - send_time
    print(duration)
    if request.method == "POST":
        otp1 = int(request.POST.get("otp"))
        # print(type(otp1))
        new_password = request.POST.get("password")
        re_password = request.POST.get("re_password")
        if new_password == re_password:
            if otp == otp1 and duration <= timedelta(minutes=5):
                user = User.objects.get(username=email)
                user.set_password(new_password)
                user.save()
                return redirect(admin_login)
            elif otp == otp1 and duration > timedelta(minutes=5):
                messages.warning(request, "Time exceeded !!")
            else:
                messages.warning(request, "Invalid otp")
        else:
            messages.warning(request, "Password Mismatch")
    return render(request, "admin_password_reset.html")


def admin_logout(request):
    logout(request)
    return redirect(admin_dashboard)


def l_correct_summary_add(request):
    if request.method == "POST":
        audio = request.FILES['audio']
        choice1 = request.POST['choice1']
        choice2 = request.POST['choice2']
        choice3 = request.POST['choice3']
        choice4 = request.POST['choice4']
        answer = request.POST['answer']

        answer_value = locals()[answer]  # This will get the actual choice text

        ListeningCorrectSummary.objects.create(
            audio=audio,
            choice1=choice1,
            choice2=choice2,
            choice3=choice3,
            choice4=choice4,
            answer=answer_value
        )
        return redirect(l_correct_summary_show)
    return render(request, "l_correct_summary_add.html")


def l_correct_summary_edit(request, lcs_id):
    question = get_object_or_404(ListeningCorrectSummary, id=lcs_id)

    if request.method == "POST":
        if 'audio' in request.FILES:
            question.audio = request.FILES['audio']
        question.choice1 = request.POST['choice1']
        question.choice2 = request.POST['choice2']
        question.choice3 = request.POST['choice3']
        question.choice4 = request.POST['choice4']
        answer = request.POST['answer']

        question.answer = request.POST[answer]  # Get the updated answer
        question.save()
        return redirect(l_correct_summary_show)
    return render(request, "l_correct_summary_edit.html", {'question': question})


def l_correct_summary_show(request):
    questions = ListeningCorrectSummary.objects.all()
    return render(request, "l_correct_summary_show.html", {'questions': questions})


def l_correct_summary_delete(request, lcs_id):
    question = get_object_or_404(ListeningCorrectSummary, id=lcs_id)
    question.delete()
    return redirect(l_correct_summary_show)


def l_fill_blanks_add(request):
    if request.method == 'POST':
        audio = request.FILES.get('audio')
        passage = request.POST.get('passage')

    # Map answers to specific blanks
        answers = {
            "blank1": request.POST.get('answer1'),
            "blank2": request.POST.get('answer2'),
            "blank3": request.POST.get('answer3'),
            "blank4": request.POST.get('answer4'),
            "blank5": request.POST.get('answer5'),
        }

        ListeningFillBlanks.objects.create(
            audio=audio,
            passage=passage,
            answers=answers
        )
        return redirect(l_fill_blanks_show)
    return render(request, "l_fill_blanks_add.html")


def l_fill_blanks_edit(request, lfb_id):
    question = get_object_or_404(ListeningFillBlanks, id=lfb_id)

    if request.method == 'POST':
        question.passage = request.POST.get('passage')
        if 'audio' in request.FILES:
            question.audio = request.FILES['audio']

        # Update answers
        question.answers = {
            "blank1": request.POST.get('answer1'),
            "blank2": request.POST.get('answer2'),
            "blank3": request.POST.get('answer3'),
            "blank4": request.POST.get('answer4'),
            "blank5": request.POST.get('answer5'),
        }

        question.save()
        return redirect(l_fill_blanks_show)
    return render(request, "l_fill_blanks_edit.html", {'question': question})


def l_fill_blanks_show(request):
    questions = ListeningFillBlanks.objects.all()
    return render(request, "l_fill_blanks_show.html", {"questions": questions})


def l_fill_blanks_delete(request, lfb_id):
    question = get_object_or_404(ListeningFillBlanks, id=lfb_id)
    question.delete()
    return redirect(l_fill_blanks_show)


def l_mcq_single_add(request):
    if request.method == "POST":
        audio = request.FILES['audio']
        question = request.POST['question']
        choice1 = request.POST['choice1']
        choice2 = request.POST['choice2']
        choice3 = request.POST['choice3']
        choice4 = request.POST['choice4']
        answer = request.POST['answer']

        answer_value = locals()[answer]  # This will get the actual choice text

        ListeningMCQSingle.objects.create(
            audio=audio,
            question=question,
            choice1=choice1,
            choice2=choice2,
            choice3=choice3,
            choice4=choice4,
            answer=answer_value
        )
        return redirect(l_mcq_single_show)
    return render(request, "l_mcq_single_add.html")


def l_mcq_single_edit(request, mcq_id):
    question = get_object_or_404(ListeningMCQSingle, id=mcq_id)

    if request.method == "POST":
        if 'audio' in request.FILES:
            question.audio = request.FILES['audio']
        question.question = request.POST['question']
        question.choice1 = request.POST['choice1']
        question.choice2 = request.POST['choice2']
        question.choice3 = request.POST['choice3']
        question.choice4 = request.POST['choice4']
        answer = request.POST['answer']

        question.answer = request.POST[answer]  # Get the updated answer
        question.save()
        return redirect(l_mcq_single_show)
    return render(request, "l_mcq_single_edit.html", {'question': question})


def l_mcq_single_show(request):
    questions = ListeningMCQSingle.objects.all()
    return render(request, "l_mcq_single_show.html", {'questions': questions})


def l_mcq_single_delete(request, mcq_id):
    question = get_object_or_404(ListeningMCQSingle, id=mcq_id)
    question.delete()
    return redirect(l_mcq_single_show)


def r_mcq_multiple_add(request):
    if request.method == 'POST':
        passage = request.POST.get('passage')
        question = request.POST.get('question')
        choice1 = request.POST.get('choice1')
        choice2 = request.POST.get('choice2')
        choice3 = request.POST.get('choice3')
        choice4 = request.POST.get('choice4')
        choice5 = request.POST.get('choice5')
        answer1 = request.POST.get('answer1')
        answer2 = request.POST.get('answer2')
        answer3 = request.POST.get('answer3', '')
        choices = {
            '1': choice1,
            '2': choice2,
            '3': choice3,
            '4': choice4,
            '5': choice5
        }
        answer1 = choices.get(answer1)
        answer2 = choices.get(answer2)
        answer3 = choices.get(answer3) if answer3 else None

        if not answer1 or not answer2:
            return render(request, "r_mcq_multiple_add.html", {
                "error": "Answer 1 and Answer 2 must be selected from the provided choices."
            })

        mcq = ReadMCQMultiple.objects.create(
            passage=passage,
            question=question,
            choice1=choice1,
            choice2=choice2,
            choice3=choice3,
            choice4=choice4,
            choice5=choice5,
            answer1=answer1,
            answer2=answer2,
            answer3=answer3
        )
        mcq.save()
        return redirect(r_mcq_multiple_show)
    return render(request, "r_mcq_multiple_add.html")


def r_mcq_multiple_edit(request, mcq_id):
    mcq = get_object_or_404(ReadMCQMultiple, id=mcq_id)

    if request.method == 'POST':
        mcq.passage = request.POST.get('passage')
        mcq.question = request.POST.get('question')
        mcq.choice1 = request.POST.get('choice1')
        mcq.choice2 = request.POST.get('choice2')
        mcq.choice3 = request.POST.get('choice3')
        mcq.choice4 = request.POST.get('choice4')
        mcq.choice5 = request.POST.get('choice5')

        choices = {
            '1': mcq.choice1,
            '2': mcq.choice2,
            '3': mcq.choice3,
            '4': mcq.choice4,
            '5': mcq.choice5
        }

        mcq.answer1 = choices.get(request.POST.get('answer1'))
        mcq.answer2 = choices.get(request.POST.get('answer2'))
        mcq.answer3 = choices.get(request.POST.get('answer3', ''))

        mcq.save()
        return redirect('r_mcq_multiple_show')
    return render(request, "r_mcq_multiple_edit.html", {'mcq': mcq})


def r_mcq_multiple_show(request):
    mcq = ReadMCQMultiple.objects.all()
    return render(request, "r_mcq_multiple_show.html", {'mcq': mcq})


def r_mcq_multiple_delete(request, mcq_id):
    mcq = get_object_or_404(ReadMCQMultiple, id=mcq_id)
    mcq.delete()
    return redirect(r_mcq_multiple_show)


def r_mcq_single_add(request):
    if request.method == 'POST':
        passage = request.POST['passage']
        question = request.POST['question']
        choice1 = request.POST['choice1']
        choice2 = request.POST['choice2']
        choice3 = request.POST['choice3']
        choice4 = request.POST['choice4']
        choice5 = request.POST['choice5']
        answer = request.POST['answer']

        # Ensure the answer matches one of the choices
        answer_value = locals()[answer]  # This will get the actual choice text

        ReadMCQSingle.objects.create(
            passage=passage,
            question=question,
            choice1=choice1,
            choice2=choice2,
            choice3=choice3,
            choice4=choice4,
            choice5=choice5,
            answer=answer_value
        )
        return redirect(r_mcq_single_show)
    return render(request, "r_mcq_single_add.html")


def r_mcq_single_edit(request, mcq_id):
    mcq = get_object_or_404(ReadMCQSingle, id=mcq_id)

    if request.method == 'POST':
        mcq.passage = request.POST['passage']
        mcq.question = request.POST['question']
        mcq.choice1 = request.POST['choice1']
        mcq.choice2 = request.POST['choice2']
        mcq.choice3 = request.POST['choice3']
        mcq.choice4 = request.POST['choice4']
        mcq.choice5 = request.POST['choice5']

        # Ensure the selected answer matches one of the updated choices
        answer_choice = request.POST['answer']
        mcq.answer = request.POST[answer_choice]

        mcq.save()
        return redirect(r_mcq_single_show)
    return render(request, "r_mcq_single_edit.html", {'mcq': mcq})


def r_mcq_single_show(request):
    mcq = ReadMCQSingle.objects.all()
    return render(request, "r_mcq_single_show.html", {'mcq': mcq})


def r_mcq_single_delete(request, mcq_id):
    mcq = get_object_or_404(ReadMCQSingle, id=mcq_id)
    mcq.delete()
    messages.success(request, "Read MCQ Single deleted successfully!")
    return redirect(r_mcq_single_show)


def s_read_aloud_add(request):
    if request.method == "POST":
        sentence = request.POST.get('sentence')
        if sentence:
            # Save the sentence to the database
            ReadAloud.objects.create(sentence=sentence)
            messages.success(request, "Sentence saved successfully!")
            return redirect(s_read_aloud_show)  # Redirect back to the same page
        else:
            messages.error(request, "Please enter a sentence.")
    return render(request, "s_read_aloud_add.html")


def s_read_aloud_edit(request, sentence_id):
    # Fetch the sentence from the database
    sentence = get_object_or_404(ReadAloud, id=sentence_id)

    if request.method == "POST":
        updated_sentence = request.POST.get('sentence')
        if updated_sentence:
            sentence.sentence = updated_sentence  # Update the sentence
            sentence.save()  # Save the changes to the database
            messages.success(request, "Sentence updated successfully!")
            return redirect(s_read_aloud_show)  # Redirect to a list or add page
        else:
            messages.error(request, "Please provide a valid sentence.")

    return render(request, 's_read_aloud_edit.html', {'sentence': sentence})


def s_read_aloud_show(request):
    # Fetch all read aloud sentences
    read_aloud = ReadAloud.objects.all()
    return render(request, 's_read_aloud_show.html', {'read_aloud': read_aloud})


def s_read_aloud_delete(request, sentence_id):
    sentence = get_object_or_404(ReadAloud, id=sentence_id)
    sentence.delete()  # Delete the sentence from the database
    messages.success(request, "Sentence deleted successfully!")
    return redirect(s_read_aloud_show)


def s_short_answer_add(request):
    if request.method == 'POST':
        answer = request.POST.get('answer')
        audio = request.FILES.get('audio')

        # Create and save the ShortAnswer object
        short_answer = ShortAnswer(answer=answer, audio=audio)
        short_answer.save()

        return redirect(s_short_answer_show)
    return render(request, "s_short_answer_add.html")


def s_short_answer_edit(request, short_answer_id):
    # Retrieve the specific short answer by ID
    short_answer = get_object_or_404(ShortAnswer, id=short_answer_id)

    if request.method == 'POST':
        # Get the updated answer and the new audio (if any)
        answer = request.POST.get('answer')
        audio = request.FILES.get('audio')

        # Update the short answer instance with new values
        short_answer.answer = answer
        if audio:
            short_answer.audio = audio  # Replace the old audio file with the new one

        short_answer.save()  # Save the updated object

        return redirect(s_short_answer_show)  # Redirect to the page that shows all short answers

    return render(request, 's_short_answer_edit.html', {'short_answer': short_answer})


def s_short_answer_show(request):
    short_answers = ShortAnswer.objects.all()  # Retrieve all short answers from the database
    print(short_answers)
    return render(request, 's_short_answer_show.html', {'short_answers': short_answers})


def s_short_answer_delete(request, short_answer_id):
    # Retrieve the specific short answer by its ID, or return a 404 error if not found
    short_answer = get_object_or_404(ShortAnswer, id=short_answer_id)

    # Delete the short answer object
    short_answer.delete()
    messages.success(request, "Sentence deleted successfully!")
    return redirect(s_short_answer_show)


def w_summarize_passage_add(request):
    if request.method == 'POST':
        passage = request.POST.get('passage')
        keywords = request.POST.get('keywords')
        SummarizePassage.objects.create(passage=passage, keywords=keywords)
        return redirect(w_summarize_passage_show)
    return render(request, "w_summarize_passage_add.html")


def w_summarize_passage_edit(request, summarize_id):
    summarize_passage = get_object_or_404(SummarizePassage, id=summarize_id)

    if request.method == 'POST':
        passage = request.POST.get('passage')
        keywords = request.POST.get('keywords')

        # Update the entry
        summarize_passage.passage = passage
        summarize_passage.keywords = keywords
        summarize_passage.save()

        return redirect(w_summarize_passage_show)  # Redirect after saving

    return render(request, 'w_summarize_passage_edit.html', {'summarize_passage': summarize_passage})


def w_summarize_passage_show(request):
    summarize_passages = SummarizePassage.objects.all()

    return render(request, "w_summarize_passage_show.html", {'summarize_passages': summarize_passages})


def w_summarize_passage_delete(request, summarize_id):
    # entry_id = request.GET.get('id')
    summarize_passage = get_object_or_404(SummarizePassage, id=summarize_id)
    summarize_passage.delete()
    return redirect(w_summarize_passage_show)


def aspirant_details(request):
    aspirants = AspirantReg.objects.all()
    return render(request, "aspirant_details.html", {"aspirants": aspirants})


from django.utils.timezone import now

def aspirant_details(request):
    aspirants = AspirantReg.objects.all()
    return render(request, "aspirant_details.html", {"aspirants": aspirants})

def aspirant_results(request, aspirant_id):
    aspirant = get_object_or_404(AspirantReg, id=aspirant_id)
    user = aspirant.user

    # Calculate Writing marks
    writing_marks = sum(write.mark for write in SummarizePassageSubmit.objects.filter(student=user))

    # Calculate Reading marks
    reading_single = ReadingTestResult.objects.filter(student=user.first_name).first()
    reading_single_marks = reading_single.mark if reading_single else 0
    reading_multiple_marks = sum(read.mark for read in MCQMultipleSubmit.objects.filter(student=user))
    reading_marks = reading_single_marks + reading_multiple_marks

    # Calculate Speaking marks
    speaking_loud_marks = sum(read.mark for read in Read_aloud_submit.objects.filter(student=user))
    speaking_short_marks = sum(read.mark for read in Short_answer_submit.objects.filter(student=user))
    speaking_marks = speaking_loud_marks + speaking_short_marks

    # Calculate Listening marks
    listening_fill_marks = sum(listening.mark for listening in ListeningFillBlanksSubmit.objects.filter(student=user))
    listening_mcq_marks = sum(listening.mark for listening in ListeningMCQSingleSubmit.objects.filter(student=user))
    listening_summary_marks = sum(listening.mark for listening in ListeningCorrectSummarySubmit.objects.filter(student=user))
    listening_marks = listening_fill_marks + listening_mcq_marks + listening_summary_marks

    # Calculate Total
    total_marks = writing_marks + reading_marks + speaking_marks + listening_marks

    # Get or create final result
    final_result, created = Final_Result.objects.get_or_create(
        student=user,
        defaults={
            "writing": writing_marks,
            "reading": reading_marks,
            "speaking": speaking_marks,
            "listening": listening_marks,
        }
    )

    context = {
        "aspirant": aspirant,
        "writing": writing_marks,
        "reading": reading_marks,
        "speaking": speaking_marks,
        "listening": listening_marks,
        "total": total_marks,
        "final_result": final_result
    }

    return render(request, "aspirant_results.html",context)

    # return render(request, "aspirant_results.html", {
    #     "aspirant_mark": final,
    #     "previous_results": previous_results
    # })

    # return render(request, "aspirant_results.html",{'results':results})




