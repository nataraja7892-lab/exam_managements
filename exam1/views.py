from django.shortcuts import render, get_object_or_404, redirect
from .forms import ExamForm
from .models import Exam
from django.shortcuts import render, redirect
from .forms import ResultForm
from exam1.models import Exam
from register.models import Student

def exam_list(request):
    exams = Exam.objects.all()
    return render(request, 'exam1/exam_list.html', {'exams': exams})

# views.py
from django.shortcuts import render, redirect
from .forms import ExamForm

def create_exam(request):
    if request.method == 'POST':
      
        num_subjects = int(request.POST.get('num_subjects', 0))
        form = ExamForm(request.POST, num_subjects=num_subjects)
        
        if form.is_valid():
            exam = form.save()
            return redirect('exam1:exam_list')  # Redirect to success page
    else:
        form = ExamForm()
    
    return render(request, 'exam1/create_exam.html', {'form': form})
def update_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    num_subjects = exam.num_subjects
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam, num_subjects=num_subjects)
        if form.is_valid():
            form.save()
            return redirect('exam1:exam_list')
    else:
        form = ExamForm(instance=exam, num_subjects=num_subjects)
        # Pre-fill subject/date fields
        for i, subject in enumerate(exam.subject_names):
            form.fields[f'subject_{i+1}'].initial = subject["name"]
            form.fields[f'date_{i+1}'].initial = subject["date"]

    return render(request, 'exam1/update_exam.html', {'form': form, 'exam': exam})

def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    if request.method == 'POST':
        exam.delete()
        return redirect('exam1:exam_list')
    return render(request, 'exam1/confirm_delete_exam.html', {'exam': exam})


# exam1/views.py
from django.shortcuts import render, redirect
from register.models import Student
from .models import Exam, Result

from django.shortcuts import render, redirect
from .models import Exam, Result
from register.models import Student
from django.http import HttpResponse

from django.shortcuts import render, redirect
from register.models import Student
from .models import Exam, Result

from django.shortcuts import render, redirect
from .models import Exam, Result
from register.models import Student
from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Exam, Result
from register.models import Student


def enter_results(request):
    exams = Exam.objects.all()
    courses = Student.objects.values_list('course', flat=True).distinct()

    selected_exam_id = request.POST.get("exam")
    selected_course = request.POST.get("course")
    selected_year = request.POST.get("year")

    students = []
    selected_exam = None
    subject_list = []
    results_map = {}  # stores already entered results

    # Save or update marks
    if request.method == "POST" and "save_results" in request.POST:
        exam = Exam.objects.get(pk=request.POST.get("exam"))
        students = Student.objects.filter(course=request.POST.get("course"), year=request.POST.get("year"))

        for student in students:
            marks_dict = {}
            for subject in exam.subject_max_marks:
                sub_name = subject["name"]
                mark = request.POST.get(f"marks_{student.id}_{sub_name}")
                if mark:
                    marks_dict[sub_name] = int(mark)

            # Check if result already exists
            result, created = Result.objects.get_or_create(student=student, exam=exam)
            result.subject_marks = marks_dict
            result.save()

        messages.success(request, "Marks saved/updated successfully ✅")
        return redirect("exam1:enter_results")

    # Fetch students and results
    if selected_exam_id and selected_course and selected_year:
        selected_exam = Exam.objects.get(pk=selected_exam_id)
        subject_list = selected_exam.subject_max_marks
        students = Student.objects.filter(course=selected_course, year=selected_year)

        for student in students:
            try:
                result = Result.objects.get(student=student, exam=selected_exam)
                results_map[student.id] = result.subject_marks
            except Result.DoesNotExist:
                results_map[student.id] = {}

    context = {
        "exams": exams,
        "courses": courses,
        "students": students,
        "selected_exam": selected_exam,
        "selected_exam_id": selected_exam_id,
        "selected_course": selected_course,
        "selected_year": selected_year,
        "subject_list": subject_list,
        "results_map": results_map,
    }
    return render(request, "exam1/enter_results.html", context)


def delete_result(request, student_id, exam_id):
    try:
        result = Result.objects.get(student_id=student_id, exam_id=exam_id)
        result.delete()
        messages.success(request, "Result deleted successfully ❌")
    except Result.DoesNotExist:
        messages.error(request, "No result found to delete.")
    return redirect("exam1:enter_results")


from django.shortcuts import render
from register.models import Student
from .models import Exam, Result

from django.shortcuts import render
from .models import Exam, Student, Result

def view_results(request):
    exams = Exam.objects.all()  # Get all exams
    courses = Student.objects.values_list('course', flat=True).distinct()  # Get distinct courses

    selected_exam_id = request.POST.get("exam")  # Get selected exam ID from POST
    selected_course = request.POST.get("course")  # Get selected course from POST
    selected_year = request.POST.get("year")  # Get selected year from POST

    students = []
    results_data = []
    selected_exam = None
    subject_headers = []
    subject_max_marks = {}  # Added

    if request.method == "POST" and "fetch_results" in request.POST:
        # Ensure the selected exam, course, and year are provided
        if selected_exam_id and selected_course and selected_year:
            try:
                # Try to fetch the selected exam
                selected_exam = Exam.objects.get(pk=selected_exam_id)
                subject_headers = [subj["name"] for subj in selected_exam.subject_names]

                # Optional: Extract subject-wise max marks if stored in DB
                # For now assuming 100 marks per subject
                subject_max_marks = {subject: 100 for subject in subject_headers}  # Added

                # Get students matching the selected course and year
                students = Student.objects.filter(course=selected_course, year=selected_year)

                for student in students:
                    # Get the result for the student and the selected exam, excluding empty marks
                    result = Result.objects.filter(student=student, exam=selected_exam).exclude(subject_marks={}).first()

                    if result:
                        subject_marks = result.subject_marks or {}
                        marks_dict = {}
                        total = 0

                        # Process subject marks and calculate total and percentage
                        for subject in subject_headers:
                            mark = subject_marks.get(subject)
                            if mark is not None:
                                marks_dict[subject] = mark
                                total += mark
                            else:
                                marks_dict[subject] = "-"

                        # Calculate percentage
                        percentage = round((total / (len(subject_headers) * 100)) * 100, 2) if subject_headers else 0.0

                        results_data.append({
                            'student': student,
                            'marks': marks_dict,
                            'total': total,
                            'percentage': percentage,
                            'exam': selected_exam, 
                        })
                    else:
                        # No result or empty marks, so return default values
                        marks_dict = {subject: "-" for subject in subject_headers}
                        results_data.append({
                            'student': student,
                            'marks': marks_dict,
                            'total': 0,
                            'percentage': 0.0,
                            'exam': selected_exam, 

                        })
            except Exam.DoesNotExist:
                # Handle case where selected_exam doesn't exist in the database
                return HttpResponse("Exam not found", status=404)

    # Ensure selected_exam is not None before passing total_max_marks
    if selected_exam:
        total_max_marks = sum(subj["max_marks"] for subj in selected_exam.subject_max_marks)

    else:
        total_max_marks = 0 # Default value if no exam is selected

    # Prepare the context for rendering the template
    context = {
        'exams': exams,
        'courses': courses,
        'students': students,
        'selected_exam': selected_exam,
        'results_data': results_data,
        'subject_headers': subject_headers,
        'selected_exam_id': selected_exam_id,
        'selected_course': selected_course,
        'selected_year': selected_year,
        'total_max_marks': total_max_marks,  # Safely pass the total_max_marks
        'subject_max_marks': subject_max_marks,
        # New line for subject-wise max
    }

    return render(request, 'exam1/view_results.html', context)



from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from .models import Result, Exam
from register.models import Student

def download_student_result_pdf(request, student_id, exam_id):
    student = Student.objects.get(id=student_id)
    exam = Exam.objects.get(exam_id=exam_id)
    result = Result.objects.get(student=student, exam=exam)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student.name}_result.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    # Title
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, y, "MARKS CARD")
    y -= 50

    # Student Info
    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Name: {student.name}")
    y -= 20
    p.drawString(50, y, f"Register Number: {student.register_number}")
    y -= 20
    p.drawString(50, y, f"Course: {student.course}")
    y -= 20
    p.drawString(50, y, f"Year: {student.get_year_display()}")
    y -= 20
    p.drawString(50, y, f"Exam Title: {exam.exam_title}")
    y -= 40

    # Table Header
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Subject")
    p.drawString(250, y, "Max Marks")
    p.drawString(370, y, "Marks Obtained")
    p.drawString(500, y, "Result")
    y -= 20

    # Subject Marks
    p.setFont("Helvetica", 12)
    total = 0
    all_passed = True  # track if student passed all subjects

    for subject in exam.subject_max_marks:  # [{"name": "Math", "max_marks": 100}, ...]
        subject_name = subject['name']
        max_marks = subject['max_marks']
        mark = result.subject_marks.get(subject_name, 0)
        total += mark

        # Subject pass/fail check
        pass_mark = max_marks * 0.35
        subject_result = "Pass" if mark >= pass_mark else "Fail"
        if subject_result == "Fail":
            all_passed = False

        # Print subject row
        p.setFillColor(colors.black)
        p.drawString(50, y, subject_name)
        p.drawString(250, y, str(max_marks))
        p.drawString(370, y, str(mark))

        # Highlight Fail in RED
        if subject_result == "Fail":
            p.setFillColor(colors.red)
        else:
            p.setFillColor(colors.black)
        p.drawString(500, y, subject_result)

        y -= 20

    # Totals
    total_max_marks = exam.total_max_marks
    percentage = round((total / total_max_marks) * 100, 2) if total_max_marks > 0 else 0

    # Grade calculation
    if not all_passed:
        grade = "Fail"
    elif percentage >= 75:
        grade = "Distinction"
    elif percentage >= 60:
        grade = "First Class"
    elif percentage >= 50:
        grade = "Second Class"
    elif percentage >= 35:
        grade = "Pass"
    else:
        grade = "Fail"

    y -= 20
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total Marks Obtained: {total}")
    y -= 20
    p.drawString(50, y, f"Total Maximum Marks: {total_max_marks}")
    y -= 20
    p.drawString(50, y, f"Percentage: {percentage}%")

    # Grade in Blue if Pass, Red if Fail
    y -= 20
    if grade == "Fail":
        p.setFillColor(colors.red)
    else:
        p.setFillColor(colors.blue)
    p.drawString(50, y, f"Overall Grade: {grade}")

    # Footer
    y -= 50
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Oblique", 10)
    p.drawCentredString(width / 2, y, "This is a system generated marks card.")

    p.showPage()
    p.save()
    return response
# exam1/views.py
from django.shortcuts import render
from .models import Exam, Result
from register.models import Student

from django.shortcuts import render
from .models import Exam, Result
from register.models import Student

def dashboard(request):
    # Total students & exams
    total_students = Student.objects.count()
    total_exams = Exam.objects.count()

    # Get all results
    results = Result.objects.select_related("exam", "student")

    # Counters
    passed = 0
    failed = 0
    distinctions = 0
    first_class = 0
    second_class = 0

    # Subject totals for averages
    subject_totals = {}
    subject_counts = {}

    for r in results:
        # Calculate total and max marks dynamically
        total_max = sum(sub['max_marks'] for sub in r.exam.subject_max_marks)
        total_obtained = sum(r.subject_marks.get(sub['name'], 0) for sub in r.exam.subject_max_marks)

        percentage = (total_obtained / total_max) * 100 if total_max > 0 else 0

        # ✅ Pass/Fail condition (overall >= 35% and each subject >= 35%)
        all_passed = True
        for sub in r.exam.subject_max_marks:
            sub_name = sub['name']
            sub_max = sub['max_marks']
            mark = r.subject_marks.get(sub_name, 0)
            if mark < sub_max * 0.35:  # failed in one subject
                all_passed = False
                break

        if all_passed and percentage >= 35:
            passed += 1
        else:
            failed += 1

        # ✅ Classifications (only for passed students)
        if all_passed:
            if percentage >= 75:
                distinctions += 1
            elif 60 <= percentage < 75:
                first_class += 1
            elif 35 <= percentage < 60:
                second_class += 1

        # ✅ Subject-wise totals for averages
        for sub in r.exam.subject_max_marks:
            sub_name = sub['name']
            mark = r.subject_marks.get(sub_name, 0)
            subject_totals[sub_name] = subject_totals.get(sub_name, 0) + mark
            subject_counts[sub_name] = subject_counts.get(sub_name, 0) + 1

    # ✅ Calculate averages
    subject_avg = {
        sub: round(subject_totals[sub] / subject_counts[sub], 2)
        for sub in subject_totals
    }

    context = {
        "total_students": total_students,
        "total_exams": total_exams,
        "passed": passed,
        "failed": failed,
        "distinctions": distinctions,
        "first_class": first_class,
        "second_class": second_class,
        "subject_avg": subject_avg,
        "exams": Exam.objects.all(),
    }

    return render(request, "exam1/dashboard.html", context)

from django.shortcuts import render
from django.shortcuts import render
from register.models import Student

def total_students(request):
    course = request.GET.get("course")
    year = request.GET.get("year")

    context = {}

    # 🔹 Step 1: Show all courses with total student count
    if not course:
        courses = {}
        for student in Student.objects.all():
            courses[student.course] = courses.get(student.course, 0) + 1
        context["courses"] = courses
        context["total_students"] = Student.objects.count()
        return render(request, "exam1/all.html", context)

    # 🔹 Step 2: Show years inside the selected course
    if course and not year:
        years = {}
        for student in Student.objects.filter(course=course):
            years[student.year] = years.get(student.year, 0) + 1
        context["course"] = course
        context["years"] = years
        return render(request, "exam1/all.html", context)

    # 🔹 Step 3: Show students of selected course + year
    if course and year:
        students = Student.objects.filter(course=course, year=year)
        context["course"] = course
        context["year"] = year
        context["students"] = students
        return render(request, "exam1/all.html", context)

from django.shortcuts import render
from exam1.models import Exam, Result
from register.models import Student

from django.shortcuts import render, get_object_or_404
from .models import Exam, Result
from register.models import Student

from django.shortcuts import render, get_object_or_404
from collections import defaultdict
from .models import Result, Exam

def passed_students_by_course(request):
    course = request.GET.get("course")
    year = request.GET.get("year")
    exam_id = request.GET.get("exam_id")

    context = {}

    # Step 1: Show courses with passed students
    if not course:
        courses = defaultdict(int)
        results = Result.objects.select_related("student", "exam")

        for result in results:
            student = result.student
            # check if student has passed this exam
            passed = True
            for subject in result.exam.subject_max_marks:
                name = subject["name"]
                max_marks = subject["max_marks"]
                mark = result.subject_marks.get(name, 0)
                if mark < max_marks * 0.35:
                    passed = False
                    break
            if passed:
                courses[student.course] += 1

        context["courses"] = dict(courses)
        return render(request, "exam1/pass.html", context)

    # Step 2: Show years for selected course
    if course and not year:
        years = defaultdict(int)
        results = Result.objects.select_related("student", "exam").filter(student__course=course)

        for result in results:
            student = result.student
            # check if student passed this exam
            passed = True
            for subject in result.exam.subject_max_marks:
                name = subject["name"]
                max_marks = subject["max_marks"]
                mark = result.subject_marks.get(name, 0)
                if mark < max_marks * 0.35:
                    passed = False
                    break
            if passed:
                years[student.year] += 1

        context["course"] = course
        context["years"] = dict(years)
        return render(request, "exam1/pass.html", context)

    # Step 3: Show exams for selected course + year
    if course and year and not exam_id:
        exams = {}
        results = Result.objects.select_related("student", "exam").filter(
            student__course=course, student__year=year
        )

        for result in results:
            student = result.student
            passed = True
            for subject in result.exam.subject_max_marks:
                name = subject["name"]
                max_marks = subject["max_marks"]
                mark = result.subject_marks.get(name, 0)
                if mark < max_marks * 0.35:
                    passed = False
                    break
            if passed:
                exams[result.exam.exam_id] = result.exam

        context["course"] = course
        context["year"] = year
        context["exams"] = exams.values()
        return render(request, "exam1/pass.html", context)

    # Step 4: Show passed students for selected course + year + exam
    if course and year and exam_id:
        exam = get_object_or_404(Exam, exam_id=exam_id)
        results = Result.objects.select_related("student", "exam").filter(
            exam=exam, student__course=course, student__year=year
        )

        passed_students = []
        for result in results:
            passed = True
            for subject in exam.subject_max_marks:
                name = subject["name"]
                max_marks = subject["max_marks"]
                mark = result.subject_marks.get(name, 0)
                if mark < max_marks * 0.35:
                    passed = False
                    break
            if passed:
                total = sum(result.subject_marks.values())
                total_max = exam.total_max_marks
                percentage = round((total / total_max) * 100, 2) if total_max > 0 else 0

                passed_students.append({
                    "student": result.student,
                    "marks": result.subject_marks,
                    "total": total,
                    "percentage": percentage,
                    "total_max": total_max
                })

        context["course"] = course
        context["year"] = year
        context["exam"] = exam
        context["passed_students"] = passed_students
        return render(request, "exam1/pass.html", context)



from django.shortcuts import render, get_object_or_404
from collections import defaultdict
from .models import Result, Exam

# Step 1 → List of courses that have passed students
def passed_courses(request):
    courses = set()

    for result in Result.objects.select_related("student", "exam"):
        total = 0
        max_total = 0
        for subj in result.exam.subject_max_marks:
            subj_name = subj.get("name")
            subj_max = subj.get("max_marks", 0)
            max_total += subj_max
            if subj_name in result.subject_marks:
                total += result.subject_marks[subj_name]

        percentage = (total / max_total) * 100 if max_total > 0 else 0
        if percentage >= 35:
            courses.add(result.student.course)

    return render(request, "exam1/passc.html", {"courses": courses})


# Step 2 → List of exams for a selected course
def passed_exams_by_course(request, course_name):
    exams = set()

    for result in Result.objects.select_related("student", "exam"):
        if result.student.course == course_name:
            total = 0
            max_total = 0
            for subj in result.exam.subject_max_marks:
                subj_name = subj.get("name")
                subj_max = subj.get("max_marks", 0)
                max_total += subj_max
                if subj_name in result.subject_marks:
                    total += result.subject_marks[subj_name]

            percentage = (total / max_total) * 100 if max_total > 0 else 0
            if percentage >= 40:
                exams.add(result.exam)

    return render(request, "exam1/passec.html", {
        "course": course_name,
        "exams": exams
    })


# Step 3 → Passed students for a selected course + exam
def passed_students_by_course_exam(request, course_name, exam_id):
    exam = get_object_or_404(Exam, exam_id=exam_id)
    passed_students = []

    for result in Result.objects.select_related("student", "exam"):
        if result.student.course == course_name and result.exam == exam:
            total = 0
            max_total = 0
            for subj in result.exam.subject_max_marks:
                subj_name = subj.get("name")
                subj_max = subj.get("max_marks", 0)
                max_total += subj_max
                if subj_name in result.subject_marks:
                    total += result.subject_marks[subj_name]

            percentage = (total / max_total) * 100 if max_total > 0 else 0
            if percentage >= 40:
                passed_students.append({
                    "student": result.student,
                    "total": total,
                    "max_total": max_total,
                    "percentage": round(percentage, 2),
                })

    return render(request, "exam1/passstu.html", {
        "course": course_name,
        "exam": exam,
        "students": passed_students
    })
from django.shortcuts import render
from collections import defaultdict
from .models import Result

def all(request):
    failed_data = defaultdict(list)

    results = Result.objects.select_related("student", "exam")

    for result in results:
        is_failed = False

        # Check fail condition per subject (less than 40% of max)
        for subj in result.exam.subject_max_marks:
            subj_name = subj.get("name")
            subj_max = subj.get("max_marks", 0)

            if subj_name in result.subject_marks:
                mark = result.subject_marks[subj_name]
                if mark < (0.4 * subj_max):
                    is_failed = True

        if is_failed:
            failed_data[result.student.course].append({
                "student_name": result.student.name,
                "register_number": result.student.register_number,
                "exam_title": result.exam.exam_title,
            })

    return render(request, "exam1/fail.html", {
        "failed_data": dict(failed_data)
    })
#total exxx
from django.shortcuts import render
from .models import Exam

def total_exams_view(request):
    total_exams = Exam.objects.count()
    exams = Exam.objects.all()

    return render(request, "exam1/total_exams.html", {
        "total_exams": total_exams,
        "exams": exams,
    })
#this is u can remove man notification
from io import BytesIO
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMessage
from .models import Result, Exam
from register.models import Student
from django.shortcuts import get_object_or_404, redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# 🔹 PDF Generator
def generate_student_result_pdf(student, exam, result):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    # Title
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, y, "MARKS CARD")
    y -= 50

    # Student Info
    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Name: {student.name}")
    y -= 20
    p.drawString(50, y, f"Register Number: {student.register_number}")
    y -= 20
    p.drawString(50, y, f"Course: {student.course}")
    y -= 20
    p.drawString(50, y, f"Year: {student.get_year_display()}")
    y -= 20
    p.drawString(50, y, f"Exam Title: {exam.exam_title}")
    y -= 40

    # Table Header
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Subject")
    p.drawString(250, y, "Max Marks")
    p.drawString(370, y, "Marks Obtained")
    p.drawString(500, y, "Result")
    y -= 20

    # Subject Marks
    p.setFont("Helvetica", 12)
    total = 0
    all_passed = True

    for subject in exam.subject_max_marks:
        subject_name = subject['name']
        max_marks = subject['max_marks']
        mark = result.subject_marks.get(subject_name, 0)
        total += mark

        pass_mark = max_marks * 0.35
        subject_result = "Pass" if mark >= pass_mark else "Fail"
        if subject_result == "Fail":
            all_passed = False

        p.setFillColor(colors.black)
        p.drawString(50, y, subject_name)
        p.drawString(250, y, str(max_marks))
        p.drawString(370, y, str(mark))

        if subject_result == "Fail":
            p.setFillColor(colors.red)
        else:
            p.setFillColor(colors.black)
        p.drawString(500, y, subject_result)
        y -= 20

    total_max_marks = exam.total_max_marks
    percentage = round((total / total_max_marks) * 100, 2) if total_max_marks > 0 else 0

    # Grade
    if not all_passed:
        grade = "Fail"
    elif percentage >= 75:
        grade = "Distinction"
    elif percentage >= 60:
        grade = "First Class"
    elif percentage >= 50:
        grade = "Second Class"
    elif percentage >= 35:
        grade = "Pass"
    else:
        grade = "Fail"

    y -= 20
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total Marks Obtained: {total}")
    y -= 20
    p.drawString(50, y, f"Total Maximum Marks: {total_max_marks}")
    y -= 20
    p.drawString(50, y, f"Percentage: {percentage}%")

    y -= 20
    if grade == "Fail":
        p.setFillColor(colors.red)
    else:
        p.setFillColor(colors.blue)
    p.drawString(50, y, f"Overall Grade: {grade}")

    y -= 50
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Oblique", 10)
    p.drawCentredString(width / 2, y, "This is a system generated marks card.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


# 🔹 Send PDF to Individual
def send_result_email(request, student_id, exam_id):
    student = get_object_or_404(Student, id=student_id)
    exam = get_object_or_404(Exam, exam_id=exam_id)
    result = get_object_or_404(Result, student=student, exam=exam)

    pdf_buffer = generate_student_result_pdf(student, exam, result)

    email = EmailMessage(
        subject=f"Exam Result: {exam.exam_title}",
        body=f"Dear {student.name},\n\nPlease find attached your exam marks card.\n\nBest regards,\nExam Office",
        to=[student.email],
    )
    email.attach(f"{student.register_number}_{exam.exam_title}.pdf", pdf_buffer.read(), "application/pdf")
    email.send()

    return HttpResponse(f"Marks PDF sent to {student.email}")


# 🔹 Send PDF to ALL students of an exam
def send_all_results_email(request, exam_id):
    exam = get_object_or_404(Exam, exam_id=exam_id)
    results = Result.objects.filter(exam=exam)

    for result in results:
        student = result.student
        pdf_buffer = generate_student_result_pdf(student, exam, result)

        email = EmailMessage(
            subject=f"Exam Result: {exam.exam_title}",
            body=f"Dear {student.name},\n\nPlease find attached your exam marks card.\n\nBest regards,\nExam Office",
            to=[student.email],
        )
        email.attach(f"{student.register_number}_{exam.exam_title}.pdf", pdf_buffer.read(), "application/pdf")
        email.send()

    return HttpResponse(f"Marks PDFs sent to all {results.count()} students")

#student details 
from django.shortcuts import render, get_object_or_404, redirect
from register.models import Student

from django.shortcuts import render, redirect, get_object_or_404
from register.models import Student

from django.shortcuts import render, redirect, get_object_or_404
from register.models import Student

def manage_students(request):
    course = request.GET.get("course")
    year = request.GET.get("year")
    student_id = request.GET.get("student_id")
    action = request.GET.get("action")

    context = {}

    # Step 1 → Show all courses
    if not course:
        courses = Student.objects.values_list("course", flat=True).distinct()
        context["courses"] = courses
        return render(request, "exam1/manage_students.html", context)

    # Step 2 → Show years for course
    if course and not year:
        years = Student.objects.filter(course=course).values_list("year", flat=True).distinct()
        context["course"] = course
        context["years"] = years
        return render(request, "exam1/manage_students.html", context)

    # Step 3 → Show student list for course + year
    if course and year and not student_id:
        students = Student.objects.filter(course=course, year=year)
        context["course"] = course
        context["year"] = year
        context["students"] = students
        return render(request, "exam1/manage_students.html", context)

    # Step 4 → Add or Update student
    if student_id and action == "update":
        if student_id == "new":
            student = Student()  # empty instance for new student
        else:
            student = get_object_or_404(Student, id=student_id)

        if request.method == "POST":
            student.register_number = request.POST.get("register_number")
            student.name = request.POST.get("name")
            student.course = request.POST.get("course")
            student.gender = request.POST.get("gender")
            student.caste = request.POST.get("caste")
            student.dob = request.POST.get("dob")
            student.mobile_number = request.POST.get("mobile_number")
            student.email = request.POST.get("email")
            student.year = request.POST.get("year")
            student.save()
            return redirect(f"/exam1/details/?course={student.course}&year={student.year}")


        context["student"] = student
        context["course"] = course
        context["year"] = year
        return render(request, "exam1/manage_students.html", context)

    # Step 5 → Delete student
    if student_id and action == "delete":
        student = get_object_or_404(Student, id=student_id)
        course, year = student.course, student.year
        student.delete()
        return redirect(f"/exam1/details/?course={student.course}&year={student.year}")
    #ranking 
from django.shortcuts import render
from register.models import Student
from .models import Exam, Result

def ranking(request):
    exams = Exam.objects.all()
    courses = Student.objects.values_list('course', flat=True).distinct()
    years = [1, 2, 3, 4]

    selected_exam_id = request.GET.get("exam")
    selected_course = request.GET.get("course")
    selected_year = request.GET.get("year")

    rankings = []
    selected_exam = None

    # Start with all results
    results = Result.objects.all().select_related("student", "exam")

    # Filter based on selections
    if selected_exam_id:
        results = results.filter(exam__exam_id=selected_exam_id)
        selected_exam = Exam.objects.get(exam_id=selected_exam_id)

    if selected_course:
        results = results.filter(student__course=selected_course)

    if selected_year:
        results = results.filter(student__year=selected_year)

    # Build ranking list
    for result in results:
        student = result.student
        exam = result.exam
        subject_marks = result.subject_marks or {}
        total = sum(subject_marks.values())
        total_max_marks = exam.total_max_marks or (len(exam.subject_names) * 100)
        percentage = round((total / total_max_marks) * 100, 2) if total_max_marks else 0

        rankings.append({
            "student": student,
            "exam": exam,
            "total": total,
            "percentage": percentage,
        })

    # Sort by percentage (descending)
    rankings = sorted(rankings, key=lambda x: x["percentage"], reverse=True)[:10]

    context = {
        "exams": exams,
        "courses": courses,
        "years": years,
        "selected_exam_id": selected_exam_id,
        "selected_course": selected_course,
        "selected_year": selected_year,
        "rankings": rankings,
        "selected_exam": selected_exam,
    }
    return render(request, "exam1/ranking.html", context)
#admin
