from django.shortcuts import render,redirect
from django.urls import reverse
from urllib.parse import urlencode
from .models import Reward,RegAmount,OtpCode,AdoptionRequest,OrphnHltSts,OrphanageInfo,DonationInfo,CharityInfo,Homevstngstatus,SurityInfo,Requeststatus,UserLogin,ParentReg,Upload_Court_Docs,UserRegistration,BabyInfo,ParentsInfo
from django.core.mail import send_mail
from django.shortcuts import render
from django.contrib import messages

from django.core.files.storage import FileSystemStorage
import os
from adoption_db.settings import BASE_DIR
import random
import datetime
import smtplib
from django.contrib import messages

def index(request):
    return render(request,'index.html')


def about(request):
    return render(request,'about.html')

def parent_home(request):
    username=request.session['username']
    return render(request,'parent_home.html')

def admin_home(request):
    data = RegAmount.objects.all().order_by('-id')[:5]
    return render(request,'admin_home.html',{'data':data})

def manager_home(request):
    return render(request,'manager_home.html')


from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def make_volunteer(request):
    """
    POST handler to mark a CharityInfo record as volunteer and save the role.
    Expects 'volunteer_id' and 'role' in POST.
    """
    if request.method == "POST":
        volunteer_id = request.POST.get("volunteer_id")
        role = request.POST.get("role", "").strip()
        charity = get_object_or_404(CharityInfo, id=volunteer_id)

        charity.is_volunteer = True
        charity.volunteer_role = role or "Volunteer"
        charity.save()

        messages.success(request, f"{charity.Name} is now a volunteer ({charity.volunteer_role}).")
        return redirect(reverse("CharityInfo_view"))

    return redirect(reverse("CharityInfo_view"))


def give_reward(request):
    """
    POST handler to save reward. Expects 'reward_id', 'reward_title', 'reward_points', 'reward_description'
    """
    if request.method == "POST":
        charity_id = request.POST.get("reward_id")
        title = request.POST.get("reward_title", "").strip()
        points = request.POST.get("reward_points") or 0
        description = request.POST.get("reward_description", "").strip()

        charity = get_object_or_404(CharityInfo, id=charity_id)
        # save reward; optional: record who gave it
        Reward.objects.create(
            charity=charity,
            title=title,
            points=int(points),
            description=description,
            given_by=request.user if request.user.is_authenticated else None
        )

        messages.success(request, f"Reward '{title}' given to {charity.Name}.")
        return redirect(reverse("CharityInfo_view"))

    return redirect(reverse("CharityInfo_view"))


def view_rewards(request, charity_id):
    """
    Show reward history for a charity/donor
    """
    charity = get_object_or_404(CharityInfo, id=charity_id)
    rewards = charity.rewards.all().order_by('-created_at')
    return render(request, "view_user_rewards.html", {"charity": charity, "rewards": rewards})


def reward_certificate(request, reward_id):
    reward = Reward.objects.get(id=reward_id)
    return render(request, "reward_certificate.html", {"reward": reward})


def parent_child_view(request):
    child = BabyInfo.objects.all()

    gender = request.GET.get("gender")
    min_age = request.GET.get("min_age")
    max_age = request.GET.get("max_age")

    if gender:
        child = child.filter(gender__iexact=gender)

    if min_age:
        child = child.filter(year__gte=min_age)

    if max_age:
        child = child.filter(year__lte=max_age)

    return render(request, "parent_child_list.html", {"userdict": child})


from django.db.models import Sum
def donor_home(request):
    username = request.session['username']   # logged-in donor email/username

    # fetch all donations made by logged-in donor
    donations = DonationInfo.objects.filter(Charity_id=username)

    # total number of donations
    total_donations = donations.count()

    # sum of donated amount
    donated_amount = donations.aggregate(total=Sum('Donation_Amt'))['total'] or 0

    # number of different orphanages supported
    orphanages_supported = donations.values('Charity_id').distinct().count()

    return render(request, "donor_home.html", {
        "total_donations": total_donations,
        "donated_amount": donated_amount,
        "orphanages_supported": orphanages_supported
    })


def login(request):
    if request.method =="POST":
        username = request.POST.get('t1')
        request.session['username']=username
        password = request.POST.get('t2')
        utype = request.POST.get('t3')
        ucheck=UserLogin.objects.filter(username=username).count()
        if ucheck>=1:
            udata=UserLogin.objects.get(username=username)
            upass=udata.password
            utype=udata.utype
            if upass==password:
                if utype=='admin':
                    return render(request,'admin_home.html')
                if utype=='parent':
                  return render(request,'parent_home.html')
                if utype=='donor':
                  return render(request,'donor_home.html')

                if utype=='manager':
                  return render(request,'manager_home.html')
            else:
                return render(request,'UserLogin.html',{'msg':'invalid password'})
        else:
            return render(request,'UserLogin.html',{'msg':'invalid username'})
    return render(request,'UserLogin.html')

def parentsLogin(request):
    if request.method == "POST":
        username = request.POST.get('t1')
        password = request.POST.get('t2')

        request.session['username'] = username

        ucheck = UserLogin.objects.filter(username=username, utype='parent').count()

        if ucheck >= 1:
            udata = UserLogin.objects.get(username=username, utype='parent')
            if udata.password == password:
                return render(request, 'parent_home.html')
            else:
                return render(request, 'parents_login.html', {'msg': 'Invalid password'})
        else:
            return render(request, 'parents_login.html', {'msg': 'Invalid parent username'})

    return render(request, 'parents_login.html')

def reg(request):
    if request.method=="POST" :
        fullname = request.POST.get('t1')
        city = request.POST.get('t2')
        address = request.POST.get('t3')
        pincode = request.POST.get('t4')
        contact = request.POST.get('t5')
        email = request.POST.get('t6')
        request.session['email']=email
        password = request.POST.get('t7')
        ucheck=ParentReg.objects.filter(email=email).count()
        if ucheck>=1:
            return render(request, 'parent_reg.html',{'msg':'This user has already exist'})
        else:
            ParentReg.objects.create(fullname=fullname,city=city,address=address,pincode=pincode,contact=contact,email=email)
            UserLogin.objects.create(username=email, password=password, utype='parent')
            #base_url=reverse('login')
            base_url=reverse('reg_amount')
            return redirect(base_url)
    return render(request, 'parent_reg.html')


def reg_amount(request):
    email = request.session.get('email')  # safer access
    if not email:
        return redirect('login')  # redirect if session email not found

    now = datetime.datetime.now()
    reg_date = now.strftime("%Y-%m-%d")

    if request.method == "POST":
        amount = request.POST.get('t1') or 1000  # default to 1000 if not provided
        request.session['amount'] = amount

        # Save registration amount record
        RegAmount.objects.create(email=email, amount=amount, date=reg_date)

        # Redirect to payment page
        return render(request, 'reg_payment.html', {'amount': amount})

    return render(request, 'reg_amount.html')

def reg_amount_view(request):
    data=RegAmount.objects.all()
    return render(request,'reg_amount_view.html',{'data':data})


from django.shortcuts import render, get_object_or_404
from .models import UserRegistration

def reg_view_user(request, email):
    user = ParentReg.objects.filter(email=email).values()
    return render(request, 'reg_view_user.html', {'data': user})





def payment_success(request):
    return render(request, 'payment_success.html')


'''def reg_payment(request):
    amount=request.session['amount']
    return render(request,'reg_payment.html',{'amount':amount})'''

def adoption_request(request,pk):
    username=request.session['username']
    now=datetime.datetime.now()
    request_date=now.strftime("%Y-%m-%d")
    request_id=str(random.randint(1,9000))
    #request.session['request_id']=request_id
    udata=BabyInfo.objects.get(id=pk)
    photo=udata.Photo
    ucheck=AdoptionRequest.objects.filter(baby_id=pk).filter(status="Accepted").count()
    if ucheck>=1:
        userdict=BabyInfo.objects.all()
        return render(request,'Babyinfo_view_p.html',{'userdict':userdict,'msg':'Sorry! This Baby has Booked'})
    else:
        if request.method=="POST":
            request_id = request.POST.get('t1')
            request_by = request.POST.get('t2')
            request_date = request.POST.get('t3')
            adoption_reason = request.POST.get('t5')
            occupation = request.POST.get('t6')
            family_members = request.POST.get('t7')
            annual_income = request.POST.get('t8')
            assets = request.POST.get('t9')
            AdoptionRequest.objects.create(request_id=request_id,request_by=request_by,request_date=request_date,adoption_reason=adoption_reason,occupation=occupation,family_members=family_members,annual_income=annual_income,assets=assets,status='pending',baby_id=pk,photo=photo)
            Requeststatus.objects.create(requeststatus='pending',requestdate=request_date,appln_no=request_id,adoptionstatus='pending')
            #ndata = AdoptionRequest.objects.get(baby_id=pk)[0]
            req_id=request_id
            request.session['request_id']=req_id
            base_url=reverse('parentsinfo')

            query_string = urlencode({'req_id': req_id,'username':username,'occupation':occupation})
            return redirect(base_url,query_string)
        return render(request,'adoption_request.html',{'username':username,'request_date':request_date,'request_id':request_id})


def adoption_status_view_p(request):
    username = request.session.get('username')  # safe way, avoids KeyError
    context = {}

    if request.method == "POST":
        applno = request.POST.get('t1')

        # First check if application exists
        if AdoptionRequest.objects.filter(request_id=applno).exists():
            userdict = Requeststatus.objects.filter(appln_no=applno).values()

            if userdict.exists():
                context['userdict'] = userdict
                return render(request, 'adoption_request_status_view_p.html', context)
            else:
                context['msg'] = "No status records found for this application."
                return render(request, 'check_adoption_status.html', context)
        else:
            context['msg'] = "Invalid Application No"
            return render(request, 'check_adoption_status.html', context)

    return render(request, 'check_adoption_status.html')


def babyinfo(request):
    if request.method=="POST" and request.FILES['myfile']:
        myfile=request.FILES['myfile']
        year = request.POST.get('t1')
        childname = request.POST.get('t2')
        bloodgroup = request.POST.get('t3')
        dob = request.POST.get('t4')
        doj = request.POST.get('t5')
        gender = request.POST.get('r1')

        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        pat = os.path.join(BASE_DIR, '/media/' + filename)
        BabyInfo.objects.create(year=year,childname=childname,bloodgroup=bloodgroup,Photo=myfile,dob=dob,doj=doj,gender=gender,adoption_status='pending')

        return render(request, 'admin_home.html')
    return render(request, 'babyinfo.html')

def parentsinfo(request):
    username=request.session['username']
    request_id=request.session['request_id']
    if request.method == "POST" and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        myfile1 = request.FILES['myfile1']
        myfile2 = request.FILES['myfile2']
        Applicant_name = request.POST.get('t1')
        Husband_name= request.POST.get('t2')
        spouse_name = request.POST.get('t22')
        education = request.POST.get('t3')
        #occupation = request.POST.get('t4')
        Email = request.POST.get('t5')
        #Phone_No = request.POST.get('t8')
        Application_No = request.POST.get('t9')
        parent_type=request.POST.get('type')

        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        pat = os.path.join(BASE_DIR, '/media/' + filename)

        filename1 = fs.save(myfile1.name, myfile1)
        uploaded_file_url1 = fs.url(filename1)
        pat1 = os.path.join(BASE_DIR, '/media/' + filename1)

        filename2 = fs.save(myfile2.name, myfile2)
        uploaded_file_url2 = fs.url(filename2)
        pat2 = os.path.join(BASE_DIR, '/media/', filename2)


        ParentsInfo.objects.create(Applicant_name=Applicant_name,education=education ,Email=username,Photo=myfile,Marriage_certificate=myfile1,Application_No=Application_No,Husband_name=Husband_name,parent_type=parent_type,spouse_name=spouse_name,aadhar_copy=myfile2)
        base_url=reverse('parent_home')
        return redirect(base_url)
    return render(request, 'Parents_info.html',{'request_id':request_id})

def reqstatus(request):
    if request.method == "POST":
        appln_no = request.POST.get('t1')
        requeststatus = request.POST.get('t2')
        requestdate = request.POST.get('t3')
        Requeststatus.objects.create(appln_no=appln_no,requeststatus=requeststatus,requestdate=requestdate)
        return render(request, 'index.html')
    return render(request, 'request_status.html')


def homevststatus(request,pk):
    udata=AdoptionRequest.objects.get(id=pk)
    applno=udata.request_id
    request.session['applno']=applno
    if request.method == "POST":
        ApplnNo = request.POST.get('t1')
        visited_date = request.POST.get('t2')
        doc_verification = request.POST.get('t3')
        visiting_status = request.POST.get('t4')
        ucheck=Homevstngstatus.objects.filter(ApplnNo=ApplnNo).count()
        if ucheck>=1:
            Homevstngstatus.objects.filter(ApplnNo=ApplnNo).update(visited_date=visited_date, doc_verification=doc_verification,visiting_status=visiting_status)
            if visiting_status=="Approved":
                return redirect('surityinfo')
            else:
                base_url=reverse('manager_home')
                return redirect(base_url)
        else:
            Homevstngstatus.objects.create(ApplnNo=ApplnNo,visited_date=visited_date,doc_verification=doc_verification,visiting_status=visiting_status)
            userdict=AdoptionRequest.objects.all()
            if visiting_status=="Approved":
                return redirect('surityinfo')
            else:
                base_url=reverse('manager_home')
                return redirect(base_url)
    return render(request, 'hmvststatus.html',{'applno':applno})


def surityinfo(request):
    username=request.session['username']
    applno=request.session['applno']
    #udata=AdoptionRequest.objects.get(request_by=username)
    #applno=udata.request_id
    if request.method == "POST":
        ApplnNo = request.POST.get('t1')
        Surity_amount = request.POST.get('t2')
        Surity_duration = request.POST.get('t3')
        terms_conditions = request.POST.get('t4')
        ucheck=SurityInfo.objects.filter(ApplnNo=ApplnNo).count()
        if ucheck>=1:
            SurityInfo.objects.filter(ApplnNo=ApplnNo).update(Surity_amount=Surity_amount, Surity_duration=Surity_duration,terms_conditions=terms_conditions)
            base_url = reverse('manager_home')
            return redirect(base_url)
        else:
            SurityInfo.objects.create(ApplnNo=ApplnNo,Surity_amount=Surity_amount,Surity_duration=Surity_duration,terms_conditions=terms_conditions)
            base_url=reverse('manager_home')
            return redirect(base_url)
    return render(request, 'surityinfo.html',{'applno':applno})

def charityinfo(request):
    if request.method == "POST":
        Name = request.POST.get('t1')
        Address = request.POST.get('t2')
        Contact_No = request.POST.get('t3')
        Email = request.POST.get('t4')
        Occupation = request.POST.get('t5')
        ucheck=CharityInfo.objects.filter(Email=Email).count()
        if ucheck>=1:
            return render(request, 'charityinfo.html',{'msg':'This user has already exist'})
        else:
            CharityInfo.objects.create(Name=Name,Address=Address,Contact_No=Contact_No,Email=Email,Occupation=Occupation)
            UserLogin.objects.create(username=Email,password=Contact_No,utype='donor')

            '''CharityInfo.objects.create(Name=Name,Address=Address,Contact_No=Contact_No,Email=Email,Occupation=Occupation)
            UserLogin.objects.create(username=Email,password=Contact_No,utype='donor')
            content = "UserName is " + str(Email) + " " + "and Password Is +" + str(Contact_No)
            mail = smtplib.SMTP('smtp.gmail.com', 587)
            mail.ehlo()
            mail.starttls()
            mail.login('@gmail.com', '')
            mail.sendmail('@gmail.com', Email, content)
            mail.close()'''
            return redirect('login')
    return render(request, 'charityinfo.html')

from django.contrib import messages
import razorpay

def donationinfo(request):
    username = request.session.get('username')

    if request.method == "POST":
        Charity_id = request.POST.get('t1')
        Donation_Amt = request.POST.get('t2')
        Donation_things = request.POST.get('t3')
        Donation_date = request.POST.get('t4')
        purpose = request.POST.get('t5')

        client = razorpay.Client(auth=("rzp_test_aRwvKMa3LOdILg", "bceCS0Mx0iWwM9OafcFtFvu3"))

        # Create Razorpay Order
        order = client.order.create({
            "amount": int(Donation_Amt) * 100,
            "currency": "INR",
            "payment_capture": 1
        })

        # Save donation temporarily (Pending status)
        donation = DonationInfo.objects.create(
            Charity_id=Charity_id,
            Donation_Amt=Donation_Amt,
            Donation_things=Donation_things,
            Donation_date=Donation_date,
            purpes=purpose,
            razorpay_order_id=order["id"],
            payment_status="Pending"
        )

        return render(request, "payment2.html", {
            "amount": Donation_Amt,
            "razorpay_order_id": order["id"],
            "donation_id": donation.id
        })

    return render(request, 'donationinfo.html', {'username': username})


import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id")
        order_id = request.POST.get("razorpay_order_id")
        signature = request.POST.get("razorpay_signature")

        client = razorpay.Client(auth=("rzp_test_Z1qzBJgJYDcceP", "YOUR_SECRET_KEY"))

        try:
            # Verify signature
            client.utility.verify_payment_signature({
                "razorpay_signature": signature,
                "razorpay_payment_id": payment_id,
                "razorpay_order_id": order_id
            })
        except:
            messages.error(request, "❌ Payment verification failed!")
            return redirect("donor_home")

        # Update donation status
        donation = DonationInfo.objects.filter(razorpay_order_id=order_id).first()
        if donation:
            donation.payment_status = "Paid"
            donation.razorpay_payment_id = payment_id
            donation.save()

        messages.success(request, "🎉 Payment Successful! Your donation has been recorded.")
        return redirect("donation_history")

    return redirect("donor_home")


def orphanageinfo(request):
    if request.method == "POST":
        Member_Name = request.POST.get('t1')
        Age = request.POST.get('t2')
        JoiningYear = request.POST.get('t3')
        blood_group = request.POST.get('t4')
        guardian_name = request.POST.get('t5')
        OrphanageInfo.objects.create(Member_Name=Member_Name,Age=Age,JoiningYear=JoiningYear,blood_group=blood_group,guardian_name=guardian_name)
        return render(request, 'admin_home.html')
    return render(request, 'orphanageinfo.html')


def donation_history(request):
    username = request.session['username']
    donations = DonationInfo.objects.filter(Charity_id=username).order_by('-Donation_date')

    return render(request, "donation_history.html", {
        "donations": donations
    })


def orphnhltsts(request):
    if request.method == "POST":
        Member_id = request.POST.get('t1')
        Health_problems = request.POST.get('t2')
        last_checkup_date = request.POST.get('t3')
        Previous_checkupdate = request.POST.get('t4')
        OrphnHltSts.objects.create(Member_id=Member_id,Health_problems=Health_problems,last_checkup_date=last_checkup_date,Previous_checkupdate=Previous_checkupdate,)
        return render(request, 'index.html')
    return render(request, 'orphnhltsts.html')

def UserRegistration_view(request):
    userdict=UserRegistration.objects.all()
    return render(request,'reg_view.html',{'userdict' : userdict})


def BabyInfo_view(request):
    userdict=BabyInfo.objects.all()
    return render(request,'BabyInfo_view.html',{'userdict' : userdict})


def BabyInfo_view_p(request):
    child = BabyInfo.objects.all()

    gender = request.GET.get("gender")
    min_age = request.GET.get("min_age")
    max_age = request.GET.get("max_age")

    if gender:
        child = child.filter(gender__iexact=gender)

    if min_age:
        child = child.filter(year__gte=min_age)

    if max_age:
        child = child.filter(year__lte=max_age)

    return render(request, "BabyInfo_view_p.html", {"userdict": child})



def adoption_request_view_m(request):
    userdict=AdoptionRequest.objects.all()
    bdata=AdoptionRequest.objects.all()

    return render(request,'adoption_request_view_m.html',{'userdict':userdict})

def adoption_request_update(request):

    return render(request,'adoption_request_view_m.html')

def BabyInfo_view_m(request):
    userdict=BabyInfo.objects.all()
    return render(request,'BabyInfo_view_m.html',{'userdict' : userdict})

def ParentsInfo_view(request,pk):
    udata=AdoptionRequest.objects.get(id=pk)
    request_id=udata.request_id
    userdict=ParentsInfo.objects.filter(Application_No=request_id)
    return render(request,'ParentsInfo_view.html',{'userdict' : userdict})


def Requeststatus_view(request):
    userdict=Requeststatus.objects.all()
    return render(request,'Requeststatus_view.html',{'userdict' : userdict})


def Homevstngstatus_view(request):
    userdict=Homevstngstatus.objects.all()
    return render(request,'Homevstngstatus_view.html',{'userdict' : userdict})

def Homevstngstatus_view_p(request):
    username=request.session['username']

    if request.method=="POST":
        applno=request.POST.get('t1')
        ucheck = AdoptionRequest.objects.filter(request_id=applno).count()
        if ucheck >=1:
            userdict = Homevstngstatus.objects.filter(ApplnNo=applno).values()
            return render(request, 'Homevstngstatus_view_p.html', {'userdict': userdict})
        else:
            return render(request,'check_visiting_status.html',{'msg':'Invalid Application No'})

    return render(request,'check_visiting_status.html')

def SurityInfo_view(request):
    userdict=SurityInfo.objects.all()
    return render(request,'SurityInfo_view.html',{'userdict' : userdict})

def SurityInfo_view_s(request,id):
    username=request.session['username']
    userdict=SurityInfo.objects.filter(ApplnNo=id).values()
    return render(request,'SurityInfo_view_s.html',{'userdict' : userdict})



def CharityInfo_view(request):
    userdict=CharityInfo.objects.all()
    return render(request,'CharityInfo_view.html',{'userdict' : userdict})

def CharityInfo_view_m(request):
    userdict=CharityInfo.objects.all()
    return render(request,'CharityInfo_view_m.html',{'userdict' : userdict})

def DonationInfo_view(request):
    userdict=DonationInfo.objects.all()
    return render(request,'DonationInfo_view.html',{'userdict' : userdict})

def DonationInfo_view_m(request):
    userdict = DonationInfo.objects.all()

    # Calculate total donation amount
    total_amount = DonationInfo.objects.aggregate(total=Sum('Donation_Amt'))['total'] or 0

    return render(request, 'DonationInfo_view_m.html', {
        'userdict': userdict,
        'total_amount': total_amount
    })


def OrphanageInfo_view(request):
    userdict=OrphanageInfo.objects.all()
    return render(request,'OrphanageInfo_view.html',{'userdict' : userdict})

def OrphanageInfo_view_d(request):
    userdict=OrphanageInfo.objects.all()
    return render(request,'OrphanageInfo_view_d.html',{'userdict' : userdict})


def OrphnHltSts_view(request):
    userdict=OrphnHltSts.objects.all()
    return render(request,'OrphnHltSts_view.html',{'userdict' : userdict})

def parents_update(request,pk):
    userdict=ParentsInfo.objects.filter(id=pk).values()
    return render(request,'parentsinfo_edit.html',{'userdict':userdict})

def parentsinfo_db(request):
    if request.method == "POST":
        id=request.POST.get('id')
        Applicant_name = request.POST.get('t1')
        Husband_wife_name = request.POST.get('t2')
        education = request.POST.get('t3')
        occupation = request.POST.get('t4')
        Email = request.POST.get('t5')
        Marriage_certificate = request.POST.get('t7')
        Phone_No = request.POST.get('t8')
        ParentsInfo.objects.filter(id=id).update(Applicant_name=Applicant_name, Husband_wife_name=Husband_wife_name,education=education ,occupation=occupation,Email=Email,Marriage_certificate=Marriage_certificate,Phone_No=Phone_No)
        userdict = ParentsInfo.objects.all()
        return render(request, 'ParentsInfo_view.html',{'userdict':userdict})

def parents_del(request,pk):
    rid=ParentsInfo.objects.get(id=pk)
    rid.delete()
    userdict=ParentsInfo.objects.all()
    return render(request, 'ParentsInfo_view.html',{'userdict':userdict})

def BabyInfo_update(request,pk):
    userdict=BabyInfo.objects.filter(id=pk).values()
    return render(request,'BabyInfo_update.html',{'userdict':userdict})

def babyinfo_db(request):
    if request.method == "POST":

        year = request.POST.get('t1')
        childname = request.POST.get('t2')
        bloodgroup = request.POST.get('t3')
        dob = request.POST.get('t4')
        doj = request.POST.get('t5')
        #gender = request.POST.get('r1')
        id=request.POST.get('id')

        '''fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        pat = os.path.join(BASE_DIR, '/media/' + filename)'''
        BabyInfo.objects.filter(id=id).update(year=year,childname=childname,bloodgroup=bloodgroup,dob=dob,doj=doj)
        userdict = BabyInfo.objects.all()
        return render(request, 'BabyInfo_view.html', {'userdict': userdict})

def babyinfo_del(request, pk):
    rid = BabyInfo.objects.get(id=pk)
    rid.delete()
    userdict = BabyInfo.objects.all()
    return render(request, 'BabyInfo_view.html', {'userdict': userdict})

def req_status_update(request,pk):
    userdict=AdoptionRequest.objects.filter(id=pk).values()
    bdata=AdoptionRequest.objects.get(id=pk)
    bid=bdata.baby_id
    if request.method=="POST":
        appln_no = request.POST.get('t1')
        request_date = request.POST.get('t2')
        request_status = request.POST.get('t3')
        adoption_status = request.POST.get('t4')
        ndata=AdoptionRequest.objects.get(request_id=appln_no)
        email=ndata.request_by
        if request_status=="Rejected":
            AdoptionRequest.objects.filter(request_id=appln_no).update(status='Rejected')
            Requeststatus.objects.filter(appln_no=appln_no).update(requeststatus='Pending',adoptionstatus='pending')
            content = "Your Request Status is " + request_status + " and Adoption Status is " + adoption_status
            mail = smtplib.SMTP('smtp.gmail.com', 587)
            mail.ehlo()
            mail.starttls()
            mail.login('gurusirsi25@gmail.com', 'oemkfoxpxpvtyzou')
            mail.sendmail('gurusirsi25@gmail.com', email, content)
            mail.close()
            msg = "Email has sent successfully"
            messages.add_message(request, messages.INFO, msg)
            base_url = reverse('adoption_request_view_m')
            return redirect(base_url, userdict='userdict')
        else:
            ucheck=Requeststatus.objects.filter(appln_no=appln_no).count()
            if ucheck>=1:
                Requeststatus.objects.filter(appln_no=appln_no).update(requeststatus=request_status,adoptionstatus=adoption_status)
                AdoptionRequest.objects.filter(request_id=appln_no).update(status=request_status)
                BabyInfo.objects.filter(id=bid).update(adoption_status=request_status)
                userdict = AdoptionRequest.objects.all()
                content = "Your Request Status is " + request_status+" and Adoption Status is "+adoption_status
                mail = smtplib.SMTP('smtp.gmail.com', 587)
                mail.ehlo()
                mail.starttls()
                mail.login('gurusirsi25@gmail.com', 'oemkfoxpxpvtyzou')
                mail.sendmail('gurusirsi25@gmail.com', email, content)
                mail.close()
                msg="Email has sent successfully"
                messages.add_message(request, messages.INFO, msg)
                base_url=reverse('adoption_request_view_m')
                return redirect(base_url,userdict='userdict')
            else:
                Requeststatus.objects.create(requeststatus=request_status,requestdate=request_date,appln_no=appln_no,adoptionstatus=adoption_status)
                AdoptionRequest.objects.filter(request_id=appln_no).update(status='Accepted')
                BabyInfo.objects.filter(id=bid).update(adoption_status=request_status)
                userdict = AdoptionRequest.objects.all()
                content = "Your Request Status is " + request_status + " and Adoption Status is " + adoption_status
                mail = smtplib.SMTP('smtp.gmail.com', 587)
                mail.ehlo()
                mail.starttls()
                mail.login('gurusirsi25@gmail.com', 'oemkfoxpxpvtyzou')
                mail.sendmail('gurusirsi25@gmail.com', email, content)
                mail.close()
                msg = "Email has sent successfully"
                messages.add_message(request, messages.INFO, msg)
                base_url = reverse('adoption_request_view_m')
                return redirect(base_url, userdict='userdict')
    return render(request,'req_status_update.html',{'userdict':userdict})

def req_status_db(request):
    if request.method=="POST":
        appln_no = request.POST.get('t1')
        request_date = request.POST.get('t2')
        request_status = request.POST.get('t3')
        adoption_status = request.POST.get('t4')
        ucheck=Requeststatus.objects.filter(appln_no=appln_no).count()
        if ucheck>=1:
            Requeststatus.objects.filter(appln_no=appln_no).update(requeststatus=request_status,adoptionstatus=adoption_status)
        else:
            Requeststatus.objects.create(requeststatus=request_status,requestdate=request_date,appln_no=appln_no,adoptionstatus=adoption_status)
            AdoptionRequest.objects.filter(request_id=appln_no).update(status='Accepted')
            userdict = AdoptionRequest.objects.all()
            return render(request, 'adoption_request_view_m.html', {'userdict': userdict})

def req_status_del(request, pk):
    id = Requeststatus.objects.get(id=pk)
    id.delete()
    userdict = Requeststatus.objects.all()
    return render(request, 'Requeststatus_view.html', {'userdict': userdict})

def homevstngstatus_update(request,pk):
    userdict=Homevstngstatus.objects.filter(id=pk).values()
    return render(request,'homevstngstatus_update.html',{'userdict':userdict})

def homevstngstatus_db(request):
    if request.method=="POST":
        id = request.POST.get('id')
        doc_verification = request.POST.get('t3')
        visiting_status = request.POST.get('t4')

        Homevstngstatus.objects.filter(id=id).update(doc_verification=doc_verification,visiting_status=visiting_status)
        userdict = Homevstngstatus.objects.all()
        return render(request, 'Homevstngstatus_view.html', {'userdict': userdict})

def homevstngstatus_del(request, pk):
    rid = Homevstngstatus.objects.get(id=pk)
    rid.delete()
    userdict = Homevstngstatus.objects.all()
    return render(request, 'Homevstngstatus_view.html', {'userdict': userdict})

def surityInfo_update(request,pk):
    userdict=SurityInfo.objects.filter(id=pk).values()
    return render(request,'SurityInfo_update.html',{'userdict':userdict})

def surityInfo_db(request):
    if request.method=="POST":
        id = request.POST.get('id')
        Surity_amount = request.POST.get('t2')
        Surity_duration = request.POST.get('t3')
        terms_conditions = request.POST.get('t4')

        SurityInfo.objects.filter(id=id).update(Surity_amount=Surity_amount,Surity_duration=Surity_duration,terms_conditions=terms_conditions)
        userdict = SurityInfo.objects.all()
        return render(request, 'SurityInfo_view.html', {'userdict': userdict})

def surityInfo_del(request, pk):
    rid = SurityInfo.objects.get(id=pk)
    rid.delete()
    userdict = SurityInfo.objects.all()
    return render(request, 'SurityInfo_view.html', {'userdict': userdict})

def charityInfo_update(request,pk):
    userdict=CharityInfo.objects.filter(id=pk).values()
    return render(request,'CharityInfo_update.html',{'userdict':userdict})

def CharityInfo_db(request):
    if request.method=="POST":
        id = request.POST.get('id')
        Address = request.POST.get('t2')
        Contact_No = request.POST.get('t3')
        Email = request.POST.get('t4')
        Occupation = request.POST.get('t5')
        CharityInfo.objects.filter(id=id).update(Address=Address,Contact_No=Contact_No,Email=Email,Occupation=Occupation)
        userdict = CharityInfo.objects.all()
        return render(request, 'CharityInfo_view.html', {'userdict': userdict})

def CharityInfo_del(request, pk):
    rid = CharityInfo.objects.get(id=pk)
    rid.delete()
    userdict = CharityInfo.objects.all()
    return render(request, 'CharityInfo_view.html', {'userdict': userdict})

def donationInfo_update(request,pk):
    userdict=DonationInfo.objects.filter(id=pk).values()
    return render(request,'DonationInfo_update.html',{'userdict':userdict})

def donationInfo_db(request):
    if request.method=="POST":
        id = request.POST.get('id')

        Donation_Amt = request.POST.get('t2')
        Donation_things = request.POST.get('t3')
        purpes = request.POST.get('t5')
        DonationInfo.objects.filter(id=id).update(Donation_Amt=Donation_Amt,Donation_things=Donation_things,purpes=purpes)
        userdict = DonationInfo.objects.all()
        return render(request, 'DonationInfo_view.html', {'userdict': userdict})

def donationInfo_del(request, pk):
    rid = DonationInfo.objects.get(id=pk)
    rid.delete()
    userdict = DonationInfo.objects.all()
    return render(request, 'DonationInfo_view.html', {'userdict': userdict})

def OrphanageInfo_update(request,pk):
    userdict=OrphanageInfo.objects.filter(id=pk).values()
    return render(request,'OrphanageInfo_update.html',{'userdict':userdict})

def OrphanageInfo_db(request):
    if request.method=="POST":
        id = request.POST.get('id')

        Age = request.POST.get('t2')
        OrphanageInfo.objects.filter(id=id).update(Age=Age)
        userdict = OrphanageInfo.objects.all()
        return render(request, 'OrphanageInfo_view.html', {'userdict': userdict})

def OrphanageInfo_del(request, pk):
    rid = OrphanageInfo.objects.get(id=pk)
    rid.delete()
    userdict = OrphanageInfo.objects.all()
    return render(request, 'OrphanageInfo_view.html', {'userdict': userdict})


def OrphnHltSts_update(request,pk):
    userdict=OrphnHltSts.objects.filter(id=pk).values()
    return render(request,'OrphnHltSts_update.html',{'userdict':userdict})

def OrphnHltSts_db(request):
    if request.method=="POST":
        id = request.POST.get('id')
        Health_problems = request.POST.get('t2')
        last_checkup_date = request.POST.get('t3')
        Previous_checkupdate = request.POST.get('t4')
        OrphnHltSts.objects.filter(id=id).update(Health_problems=Health_problems,last_checkup_date=last_checkup_date,Previous_checkupdate=Previous_checkupdate)
        userdict = OrphnHltSts.objects.all()
        return render(request, 'OrphnHltSts_view.html', {'userdict': userdict})

def OrphnHltSts_del(request, pk):
    rid = OrphnHltSts.objects.get(id=pk)
    rid.delete()
    userdict = OrphnHltSts.objects.all()
    return render(request, 'OrphnHltSts_view.html', {'userdict': userdict})


def forgetpass(request):
    if request.method=="POST":
        username=request.POST.get('t1')
        request.session['username']=username
        chcek=UserLogin.objects.filter(username=username).count()
        if chcek>=1:
            udata=UserLogin.objects.get(username=username)
            password=udata.password
            otp=random.randint(1,5000)
            OtpCode.objects.create(otp_code=otp,status='active')
            content=str(otp)
            mail=smtplib.SMTP('smtp.gmail.com',587)
            mail.ehlo()
            mail.starttls()
            mail.login('satishmm9508@gmail.com','Abcd@123')
            mail.sendmail('satishmm9508@gmail.com',username,content)
            mail.close()
            base_url=reverse('otp')
            return redirect(base_url)
            #return render(request,'otp.html',{'password':password})
        else:
            return render(request,'forgetpass.html',{'msg':'invalid username'})
    return render(request,'forgetpass.html')


def otp(request):
    username=request.session['username']
    if request.method=="POST":
        otp=request.POST.get('t1')
        ucheck=OtpCode.objects.filter(otp_code=otp).count()
        if ucheck >=1:
            base_url=reverse('pass_db')
            return redirect(base_url)
        else:
            url=reverse('otp')
            msg='invalid otp'
            return redirect(url,msg='msg')

        #newpass=request.POST.get('t1')
        #cpass=request.POST.get('t2')
        #UserLogin.objects.filter(username=username).update(password=newpass)
        #return render(request,'print.html')
    return render(request,'otp.html')

def pass_db(request):
    username = request.session['username']
    if request.method == "POST":
        newpass = request.POST.get('t1')
        cpass = request.POST.get('t2')
        if newpass==cpass:

            UserLogin.objects.filter(username=username).update(password=newpass)
            log_url=reverse('login')
            return redirect(log_url)
        else:
            return render(request, 'print.html',{'msg':'newpass and confirm pass must be same'})

    return render(request, 'print.html')


def changepass(request):
    uname=request.session['username']
    if request.method == 'POST':
        currentpass = request.POST.get('t2', '')
        newpass = request.POST.get('t3', '')
        confirmpass = request.POST.get('t4', '')

        ucheck = UserLogin.objects.filter(username=uname).values()
        for a in ucheck:
            u = a['username']
            p = a['password']
            if u == uname and currentpass == p:
                if newpass == confirmpass:
                    UserLogin.objects.filter(username=uname).update(password=newpass)
                    base_url=reverse('login')
                    msg='password has been changed successfully'
                    return redirect(base_url,msg=msg)
                else:
                    return render(request, 'changepass.html',{'msg': 'both the usename and password are incorrect'})
            else:
                return render(request, 'changepass.html',{'msg': 'invalid username'})
    return render(request, 'changepass.html')


def upload_court_docs(request,pk):
    if request.method=="POST" and request.FILES['myfile']:
        
        myfile=request.FILES['myfile']
        myfile1 = request.FILES['myfile1']
        myfile2 = request.FILES['myfile2']
        myfile3 = request.FILES['myfile3']

        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        pat = os.path.join(BASE_DIR, '/media/' + filename)

        filename1 = fs.save(myfile1.name, myfile1)
        uploaded_file_url1 = fs.url(filename1)
        pat1 = os.path.join(BASE_DIR, '/media/' + filename1)

        filename2 = fs.save(myfile2.name, myfile2)
        uploaded_file_url2 = fs.url(filename2)
        pat2 = os.path.join(BASE_DIR, '/media/' + filename2)

        filename3 = fs.save(myfile3.name, myfile3)
        uploaded_file_url3 = fs.url(filename3)
        pat3 = os.path.join(BASE_DIR, '/media/' + filename3)

        Upload_Court_Docs.objects.create(user_id=pk,court_certi=myfile,caste=myfile1,aadhar=myfile2,address_proof=myfile3)
        base_url=reverse('parent_home')
        return redirect(base_url)
    return render(request,'upload_court_docs.html')


def court_doc_view(request):
    userdict=Upload_Court_Docs.objects.all()
    return render(request,'court_doc_view.html',{'userdict':userdict})



def chat(request):
	return render(request, 'chatindex.html')

    
def room(request, room_name):
	return render(request, 'room.html', {'room_name': room_name})
	#return render(request, 'chatindex.html')


def location_view(request,email):
    data=ParentReg.objects.filter(email=email).all()
    return render(request,'location_view.html',{'data':data})


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # Email subject & message
        admin_subject = f"New Contact Form Message: {subject}"
        admin_message = (
            f"New message received from the Contact Page.\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Subject: {subject}\n\n"
            f"Message:\n{message}"
        )

        # Send email to admin
        send_mail(
            admin_subject,
            admin_message,
            email,  # safer than user email
            ['gurusirsi25@gmail.com'],  # must be a LIST
            fail_silently=False,
        )

        messages.success(request, "Your message has been sent successfully!")

    return render(request, "contact.html")