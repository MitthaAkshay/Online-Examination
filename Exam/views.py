from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from . import forms,models
from django.http import HttpResponseRedirect
from Exam import models as TMODEL
from teacher import models as SMODEL
from django.core.mail import send_mail
from django.conf.global_settings import EMAIL_HOST_USER
from datetime import date, datetime
# Create your views here.
def Home_View(request):
    return render(request,'Exam/Home.html')

def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()


def afterlogin_view(request):
    if is_student(request.user):      
        return redirect('student/student-dashboard')
                
    elif is_teacher(request.user):
            return redirect('teacher/teacher-dashboard')
        
    else:
        return redirect('admin-dashboard')

@login_required(login_url='login')
def admin_dashboard_view(request):
    notice=SMODEL.CirculateNotice.objects.all()
    Teacherinfo=TMODEL.Teacher.objects.filter(user_id=request.user.id)
    notice=SMODEL.CirculateNotice.objects.all()
    TodaytotalExams=SMODEL.ExamTimeTable.objects.filter(Date=date.today())
    datewiseExamScheduledTotal=SMODEL.ExamTimeTable.objects.filter(Date=date.today(),Status='Scheduled')
    datewiseExamcompleted=SMODEL.ExamTimeTable.objects.filter(Date=date.today(),Status='End')
    datewiseExamActivated=SMODEL.ExamTimeTable.objects.filter(Date=date.today(),Status='Start')
    ActivatedExam=datewiseExamActivated.count()
    completedexam=datewiseExamcompleted.count()
    totalexam=datewiseExamScheduledTotal.count()
    todaytotalexam=TodaytotalExams.count()
    todayexamrunninglist=SMODEL.ExamTimeTable.objects.filter(Date=date.today(),Status='Start')
    #For Student
    srt=[]
    getcoursesemtoday=SMODEL.ExamTimeTable.objects.filter(Date=date.today()).distinct()
    for dt in getcoursesemtoday:
        srt.append(dt.course_name) 
        srt.append(dt.semester) 
    temp=1
    temp1=0
    totalst=0
    stcount=[]
    for st in range(0,len(srt)):
           local=len(srt)+1
           if temp!=local:
                if temp1!=temp:
                    TotalStudentAllocated=SMODEL.Student.objects.filter(course=srt[temp1],semester=srt[temp])
                    stcount.append(TotalStudentAllocated.count())
                    temp=temp+2
                    temp1=temp1+2
    add=list(dict.fromkeys(stcount))# removing Duplicate Elements
    for ele in range(0,len(add)):
        totalst=totalst+add[ele]
    print(totalst)
    context={'todaytotalexam':todaytotalexam,'teacher':Teacherinfo,'notice':notice,'totalex':totalexam,'datewiseExam':datewiseExamScheduledTotal,'completed':completedexam,'examcomlist':datewiseExamcompleted,'activat':ActivatedExam,'examlist':todayexamrunninglist,'tstexam':totalst}
    return render(request,'Exam/AdminDashboard.html',context)

@login_required(login_url='login')
def admin_add_faculty_view(request):
    userForm=forms.TeacherUserForm()
    teacherForm=forms.TeacherForm()
    teachers= TMODEL.Teacher.objects.all().filter(status=True)
    mydict={'userForm':userForm,'teacherForm':teacherForm,'teachers':teachers}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST)
        teacherForm=forms.TeacherForm(request.POST,request.FILES)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacher=teacherForm.save(commit=False)
            teacher.user=user
            teacher.save()
            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
            email=userForm.cleaned_data['email']
            username=userForm.cleaned_data['username']
            passw=userForm.cleaned_data['password']
            send_mail(
            'Punyashlok Ahilyadevi Holkar Solapur University, Solapur',
            'This Faculty Name:'+username+'  And Password:'+passw+' Authentication For Your Staff ...! And Welcome To Our University',
            EMAIL_HOST_USER,
            [email],
            fail_silently=False,
                    )
    return render(request,'Exam/AddFaculty.html',context=mydict)
#Student Details
@login_required(login_url='login')
def admin_manage_student(request):
    studentdetails=SMODEL.Student.objects.all()
    return render(request,'Exam/StudentDetails.html',{'studentdetails':studentdetails})
#Student Details
@login_required(login_url='login')
def admin_view_examtimetable(request):
    TimeTable=SMODEL.ExamTimeTable.objects.order_by('semester','course_name')
    return render(request,'Exam/ExamTimeTable.html',{'TimeTable':TimeTable})
