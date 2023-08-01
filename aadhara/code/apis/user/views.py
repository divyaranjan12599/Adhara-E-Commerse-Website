from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions,authentication
from rest_framework import status
from communication.com_service import ComService,send_registration_success
from shop.shipment.shiprocket import ShipRocketService
from users.models import User,Address
from .serializers import ReferralSerializer,ReferralTreeSerializer
from django.db.models import Q
from core import choices
from core.models import Pincode,CityState
from django.contrib.auth import authenticate, login
from shop.models import Cart
import json
from ecommerce.jinja_env import img_tag
from django.conf import settings
from shop.mails import registration_success_communication
from shop.shipment.nimbuspost import Nimbuspost 
class SendOTP(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user = request.data.get('user',False)
        otp_type = request.data.get('type',False)
        is_new = request.data.get('is_new',False)

        data={}
        data['status']=True
        data['message'] = "All Fields Required"

        if user and otp_type:
            if is_new == "yes" and User.objects.filter(Q(mobile=user if user.isdigit() else '-1') | Q(email=user) ).exists():
                data['status']=False
                data['message'] = "User Already exists"
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            #do not send to blocked users
            if not User.objects.filter(is_active=False).filter(Q(mobile=user if user.isdigit() else '-1') | Q(email=user) ).exists():
                cs=ComService()
                cs.send_otp(user,int(otp_type))
                return Response(data, status=status.HTTP_200_OK)
            else:
                data['message'] = "Your account is blocked, please contact admin."
        data['status']=False
        return Response(data, status=status.HTTP_400_BAD_REQUEST)



class VerifyOTP(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user = request.data.get('user',False)
        otp = request.data.get('otp',False)
        otp_type = request.data.get('type',False)
        if user and otp and otp_type:
            cs=ComService()
            if cs.verify_otp(user,otp,int(otp_type)):
                #verfied data will be used while creating user
                request.session['verified_{}'.format(otp_type)] = user
                return Response("ok", status=status.HTTP_200_OK)
            return Response("Invalid OTP", status=status.HTTP_400_BAD_REQUEST)
        return Response("All Fields Required", status=status.HTTP_400_BAD_REQUEST)

class ReferralDID(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        did = request.data.get('did',False)
        if did and len(did) == 9 and did[-1] in ['L','R']:
            user = User.objects.get(did=did[:-1])

            request.session['referral_did'] = did
            data = ReferralSerializer(user).data
            data['position'] = "Right" if did[-1] == "R" else "Left"
            return Response(data, status=status.HTTP_200_OK)
        return Response("error", status=status.HTTP_400_BAD_REQUEST)


class UserDetails(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        did = request.data.get('did',False)
        if did:
            user = User.get_user(did)
            if user:
                data = ReferralSerializer(user).data
                return Response(data, status=status.HTTP_200_OK)
        return Response("error", status=status.HTTP_400_BAD_REQUEST)



class CreateUser(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        gender = request.data.get('gender',False)
        name = request.data.get('name',False)
        dob = request.data.get('dob',False)
        password = request.data.get('password',False)
        profile_picture = request.data.get('profile_picture', False)

        #from session
        placement = request.session.get('referral_did')[-1]
        placement = choices.PlacementChoices.get_by_string(placement)
        sponsor_id = request.session.get('referral_did')[:-1]
        
        email = request.session.get('verified_{}'.format(choices.CommunicationTypeChooices.EMAIL))
        mobile = request.session.get('verified_{}'.format(choices.CommunicationTypeChooices.SMS))
        #session data ends

        data={}
        data['status']= False
        data['message'] = "All Fields Required"

        if gender and name and dob and password:
            # user = User.objects.get(did=did[:-1])
            user_dict={}

            #gender=gender,name=name,email=email,date_of_birth=dob,sponsor=sponsor,placement=placement,parent=parent
            user_dict['gender'] = gender
            user_dict['name'] = name
            user_dict['password'] = password
            user_dict['date_of_birth'] = dob
            user_dict['placement'] = placement
            user_dict['sponsor_id'] = sponsor_id
            user_dict['email'] = email
            user_dict['mobile'] = mobile

            user = User.create_user(**user_dict)
            if profile_picture:
                user.profile_picture = profile_picture
                user.save()

            send_registration_success.delay(user.id)
            data['status'] = True
            data['message'] = "Account Created. Your DID is {}".format(user.id) 
            del request.session['referral_did']
            del request.session['verified_1']
            del request.session['verified_2']
            return Response(data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email',False)
        password = request.data.get('password',False)
        
        data={}
        data['status']= False
        data['message'] = "All Fields Required"

        if email and password:
            user = authenticate(email=email,password=password)
            if user:
                data['status']=True
                data['message'] = "Logged In"
                login(request,user)
                return Response(data, status=status.HTTP_200_OK)

            else:
                data['message']="Login failed. Invalid username and/or password/otp."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class UserForgotPassword(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        mobile = request.data.get('username', False)
        otp = request.data.get('otp', False)
        newpassword = request.data.get('newpassword', False)

        data = {}
        data['status'] = False
        data['message'] = "All Fields Required"

        if mobile and otp and newpassword:
            user = authenticate(username=mobile, password=None, otp=otp)
            if user:
                user.set_password(newpassword)
                user.save()
                return Response(data, status=status.HTTP_200_OK)
            else:
                data['message'] = "Action failed. Invalid mobile and/or otp."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)



class EditProfile(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]

    def post(self, request):
        profile_picture = request.data.get('profile_picture',False)
        password = request.data.get('password',False)
        newpassword = request.data.get('newpassword',False)

        transactionpassword = request.data.get('transactionpassword', False)
        newtransactionpassword = request.data.get('newtransactionpassword', False)



        data={}
        data['status']= False
        data['message'] = "All Fields Required"
        
        if profile_picture or (password and newpassword) or (transactionpassword and newtransactionpassword):

            user = request.user
            
            if profile_picture:
                user.profile_picture = profile_picture
                user.save()

            if password and newpassword:
                if user.check_password(password):
                    user.set_password(newpassword)
                    user.save()
                else:
                    data={}
                    data['status']= False
                    data['message'] = "password do not match"
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if transactionpassword and newtransactionpassword:
                bank_details = BankDetailsModel.objects.filter(user=user).first()
                if bank_details and bank_details.check_transaction_password(transactionpassword):
                    bank_details.transation_password = newtransactionpassword
                    bank_details.save()
                else:
                    data={}
                    data['status']= False
                    data['message'] = "current transaction password do not match"
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)


            data['status']= True
            data['message'] = "Saved successfully!"

            return Response(data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class EditMobile(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]

    def post(self, request):
        mobile = request.data.get('mobile',False)
        otp = request.data.get('otp',False)
        user = request.user    
        data={}
        data['status']= False
        data['message'] = "All Fields Required"
        
        if user and otp and mobile:
            cs=ComService()
            if cs.verify_otp(mobile,otp,choices.CommunicationTypeChooices.SMS):
                user.mobile = mobile
                user.save()
                data['status']= True
                data['message'] = "Saved successfully!"
                return Response("ok", status=status.HTTP_200_OK)
            
            data['message'] = "Invalid OTP"
            return Response(data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class EditEmail(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]

    def post(self, request):
        email = request.data.get('email',False)
        otp = request.data.get('otp',False)
        user = request.user    
        data={}
        data['status']= False
        data['message'] = "All Fields Required"
        
        if user and otp and email:
            cs=ComService()
            if cs.verify_otp(email,otp,choices.CommunicationTypeChooices.EMAIL):
                user.email = email
                user.save()
                data['status']= True
                data['message'] = "Saved successfully!"
                return Response("ok", status=status.HTTP_200_OK)
            
            data['message'] = "Invalid OTP"
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)



class ChangePassword(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]

    def post(self, request):
        existing_password = request.data.get('existing_password',False)
        new_password = request.data.get('new_password',False)
        user = request.user    
        data={}
        data['status']= False
        data['message'] = "All Fields Required"
        
        if user and existing_password and new_password:
            if user.check_password(existing_password):
                user.set_password(new_password)
                user.save()
                data['status']= True
                data['message'] = "Saved successfully!"
                return Response("ok", status=status.HTTP_200_OK)
            
            data['message'] = "Invalid existing password"
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)




class AddressAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]

    def post(self, request):
        name = request.data.get('name',False)
        email = request.data.get('email',False)
        mobile = request.data.get('mobile', False)
        street = request.data.get('street',False)
        pincode = request.data.get('pincode',False)                        
        city = request.data.get('city',False)                        
        state = request.data.get('state',False)                        

        data={}
        data['status']= False
        data['message'] = "All Fields Required"
        
        if name and email and mobile and street and pincode and city and state:

            user = request.user
            
            address = user.get_address()
            address.name = name
            address.email = email
            address.mobile = mobile
            address.street = street
            address.city = CityState.objects.filter(pk=city).first()
            address.state = CityState.objects.filter(pk=state).first()
            address.pincode = Pincode.objects.filter(pincode=pincode).first()

            address.save()

            data['status']= True
            data['message'] = "Address Saved successfully!"

            return Response(data, status=status.HTTP_200_OK)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)




class CartAddressAPI(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get_or_create_user(self,request):
        """This method user is authenticated return otherwise create user
        """
        name=request.POST.get('name',False)
        email=request.POST.get('email',False)
        mobile=request.POST.get('mobile',False)
        if request.user.is_authenticated:
            return request.user
        if User.objects.filter(Q(email=email)|Q(mobile=mobile)).exists():
            return None
        user=User(name=name,email=email,mobile=mobile)
        user.set_password("Ajdshj133334jk")
        user.save()
        registration_success_communication(user)
                
        return user
    
    def post(self, request):
        name=request.POST.get('name',False)
        email=request.POST.get('email',False)
        mobile=request.POST.get('mobile',False)
        address=request.POST.get('address',False)
        city=request.POST.get('city',False)
        state=request.POST.get('state',False)
        company=request.POST.get('company','')
        pincode=request.POST.get('pincode',False)
        
        data={}
        data['status']= False
        data['message'] = "All Fields Required"
        if name and email and mobile and address and city and state and pincode:
            user=self.get_or_create_user(request)
            if user:
                nmb=Nimbuspost()
                result=nmb.check_pincode_delivery(pincode)
                if result is False:
                    data['message']="This pincode no available"
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                pincode =Pincode.objects.get(pincode=pincode)
                # address = Address.objects.create(name=name,email=email,mobile=mobile,address=address,city=pincode.city_state,state=pincode.city_state.parent,pincode=pincode,company_name=company)
                if request.user.is_authenticated:
                    addr = Address.objects.filter(user=user,name=name,email=email,mobile=mobile,address=address,city=pincode.city_state,state=pincode.city_state.parent,pincode=pincode,company_name=company).first()
                    if  not addr:
                        addr = Address.objects.create(name=name,email=email,mobile=mobile,address=address,city=pincode.city_state,state=pincode.city_state.parent,pincode=pincode,company_name=company)
                        addr.user = user
                        addr.save()
                else:
                    addr = Address.objects.create(name=name,email=email,mobile=mobile,address=address,city=pincode.city_state,state=pincode.city_state.parent,pincode=pincode,company_name=company)
                    addr.user = user
                    addr.save()
                cart = Cart.get_cart(request)
                cart.shipping_address=addr
                cart.billing_address=addr
                cart.save()
                data['status']= True
                data['message'] = "Address Saved successfully!"
                return Response(data, status=status.HTTP_200_OK)
            else:
                data['message']="User with this email or mobile no. already exists, Please login"
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)



