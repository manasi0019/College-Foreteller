from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from numpy import dtype
from CollegeForteller import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from django.core.mail import EmailMessage, send_mail
from application.models import UserInformation
import os
import pickle
import warnings
warnings.filterwarnings("ignore")
import pandas as pd

# Create your views here.
def home(request):
    return render(request, 'application/mainPage.html')


def getCasteList ( cat , gender,collegedata ):
  temp = "G"+cat
  if gender.lower() == "female":
    temp = "L"+cat
  castelist = collegedata[collegedata['Caste'].str.startswith(temp.upper())]
  cst = castelist['Caste'].tolist()
  #st = set(cst)
  return cst


def getlistofcolleges ( region , gender , category , coursename, cettotal , cetphysics , cetchemistry , cetmaths , hsctotal , hscphysics , hscchemistry , hscmaths ):
  collegelist = []
  #collegedata = pd.read_csv(region.lower()+'collegedata.csv')
  basepath = "/DYE/DYE/REPO/"
  collegedata = pd.read_csv(basepath +  region.lower()+'collegedata.csv')  
  collegedata = collegedata [ collegedata['CourseName'].str.lower()==coursename.lower().strip() ]
  ids = collegedata['ID'].tolist()
  basepath = "/DYE/DYE/"
  path = region.upper()
  files = os.listdir(basepath+path)
  
  castes = getCasteList ( category , gender , collegedata)  
  for f in files:
    #   print(f);
    id = int(f)
    # print(id)
    
    
    if id in ids :
      courseinfo = collegedata[ collegedata['ID']==id]  
      collegename = courseinfo['CollegeName'].iloc[0]
      castename = courseinfo['Caste'].iloc[0]
      if castename in castes:
        filepath = basepath+path + '/' + f
        lg = pickle.load(open(filepath,'rb'))
        print('cettotal ', cettotal, type(cettotal) )
        print('cetphysics ', cetphysics, type(cetphysics) )
        print('cetchemistry ', cetchemistry, type(cetchemistry) )
        print('cetmaths ', cetmaths, type(cetmaths) )
        print('hsctotal ', hsctotal, type(hsctotal) )
        print('hscphysics ', hscphysics, type(hscphysics) )
        print('hscchemistry ', hscchemistry, type(hscchemistry) )
        print('hscmaths ', hscmaths, type(hscmaths) )
        
        r = lg.predict([[float(cettotal),float(cetphysics),float(cetchemistry),float(cetmaths),float(hsctotal),float(hscphysics),float(hscchemistry),float(hscmaths)]])
        # r = lg.predict([[50.0,	50.0,	59.949508,	59.989902,	58.33,	50.0,	88.0,	88.00]])
        if int(r[0])==1:
          collegelist.append(collegename)
          #print ( collegename)
        #break
  return collegelist

def list(request):
    
    if request.method == 'POST':
        cetphysics = request.POST['cetphysics']
        cetchemistry = request.POST['cetchemistry']
        cetmaths = request.POST['cetmaths']
        cettotal = request.POST['cettotal']
        hscphysics = request.POST['hscphysics']
        hscchemistry = request.POST['hscchemistry']
        hscmaths = request.POST['hscmaths']
        hsctotal = request.POST['hsctotal']
        gender = request.POST['gender']
        category = request.POST['category']
        region = request.POST['state']

        if gender=='F':
            gender="female"
        else:
            gender="Male"

        if category=="GEN":
            category="OPEN"

        if category=="GEN":
            category="SC"

        if category=="GEN":
            category="ST"

        if category=="GEN":
            category="EWS"

        if category=="GEN":
            category="OBC"
        clglist = getlistofcolleges(region,gender,category,'Mechanical Engineering',cettotal,	cetmaths,	cetphysics,	cetchemistry,	hscchemistry,	hscmaths,	hscphysics,	hsctotal)

    return render(request,'application/collegelist.html',{'collegelist':clglist})

def signup(request):
    if request.method == 'POST':
        fname = request.POST['fname']
        username = request.POST['username']
        mobile = request.POST['mobile']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username Already Exist !! Please Try Some other Username")
            return redirect('signup')

        if len(mobile)>10:
            messages.error(request, "Contact number must be under 10 integers")
            return redirect('signup')
            
        if User.objects.filter(email=email):
            messages.error(request, "Email Already Exist !! Please Enter New Email")
            return redirect('signup')

        if len(username)>20:
            messages.error(request, "Username must be under 20 characters")
            return redirect('signup')

        if not username.isalnum():
            messages.error(request, "Username must be alphanumeric...")
            return redirect('signup')

        # password validators :
        l , u, p, d = 0, 0, 0, 0
        capitalalphabets="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        smallalphabets="abcdefghijklmnopqrstuvwxyz"
        specialchar="$@_"
        digits="0123456789"
        if (len(pass1) >= 8):
            for i in pass1:
                if (i in smallalphabets):# counting lowercase alphabets
                    l+=1           
                if (i in capitalalphabets):# counting uppercase alphabets
                    u+=1           
        
                if (i in digits):# counting digits
                    d+=1           
                if(i in specialchar):# counting the mentioned special characters
                    p+=1  
        if (l>=1 and u>=1 and p>=1 and d>=1 and l+p+u+d==len(pass1)):
            if pass1 != pass2:
                messages.error(request, "Password didn't match !!!")
                return redirect('signup')  
        else:
            return redirect('signup')          
        # end of pass validators
        

        usr = User.objects.create_user(username, email, pass1)
        usr.first_name = fname
        usr.is_active = False    

        ins = UserInformation(fname=fname, username=username, mobile=mobile, email=email)
        ins.save()
        usr.save()
        messages.success(request,"Your account has been successfully created !!!")

        # CODE TO SEND CONFIRMATION MAIL :
        subject = "Welcome to CollegeForeteller - Login"
        message = "Hello " + usr.first_name + " !!\n" + "Welcome to CollegeForeteller. \nThank You For visiting our Website. \nWe have also sent you a confirmation mail, please confirm your mail in order to activate your account. \n\nThank You....." 
        from_email = settings.EMAIL_HOST_USER
        to_list = [usr.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        #Confirmation Email :
        current_site = get_current_site(request)
        email_subject = "Confirm your email at CollegeForeteller.com"
        message2 = render_to_string('confirmation.html', {'name':usr.first_name, 'domain':current_site.domain, 'uid':urlsafe_base64_encode(force_bytes(usr.pk)), 'token':generate_token.make_token(usr)})
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [usr.email],
        )
        email.fail_silently = True
        email.send()


        return redirect('login')
    return render(request, 'application/login.html')


def loginfunc(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)
        if user is not None:
            login(request, user)
            fname = user.first_name
            uname = user.username
            if uname == 'admin':
                d = UserInformation.objects.all()
                return render(request,'application/userlist.html',{'users': d})
            return render(request, "application/mainPage.html", {'fname':fname, 'uname':uname})
        else:
           messages.error(request, "Bad request")
           return redirect('signup')
    return render(request, 'application/login.html')



def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully !!!")
    return redirect('signup')

def mainPage(request):
    return render(request, 'application/mainPage.html')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usr = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        usr = None
    
    if usr is not None and generate_token.check_token(usr, token):
        usr.is_active = True
        usr.save()
        login(request, usr)
        return redirect('signup')
    else:
        return render(request, 'activationFail.html')



def userProfile(request):
    return render(request, 'application/profile.html')


def getuserslist(request):
    d = UserInformation.objects.all()
    return render(request,'application/userlist.html',{'users': d})



