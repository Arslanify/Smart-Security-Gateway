from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.db.models import Count
from django.utils import timezone
from django.core.signing import dumps, loads, BadSignature
from django.conf import settings
import threading
import datetime
import os
import uuid
import qrcode
from io import BytesIO

# 🛑 TWILIO WHATSAPP IMPORT
from twilio.rest import Client

# 🛑 DRF & SWAGGER IMPORTS
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# 🚩 DATABASE MODELS (BusLocation lazmi add kiya hai)
from .models import Entity, AttendanceLog, BusLocation

# ==========================================
# 🧠 AI MODEL PRE-LOADING
# ==========================================
try:
    from deepface import DeepFace
    print("🚀 Enterprise AI Models Loading... System starting.")
    # DeepFace.build_model("Facenet512") 
    print("✅ System Ready: Face, QR & Biometric Modules Activated.")
except Exception as e:
    print(f"❌ AI Initialization Error: {e}")

# ==========================================
# 📱 WHATSAPP & SMART TERMINAL LOGIC
# ==========================================

def send_whatsapp_bg(student, action_type, lat=None, lng=None, terminal_mode='gate'):
    if not student.guardian_phone:
        return
    
    # 🔐 Aapke Twilio Account ki Asli Details
    TWILIO_ACCOUNT_SID = 'AC73270579de9affcf8b4d1a25ad35ec4e'
    TWILIO_AUTH_TOKEN = '85729cd2d0366891c061457ccd5c9430'
    TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886' 
    
    # 🔗 NGROK LINK (Presentation walay din lazmi update karein!)
    NGROK_URL = "https://hillocked-celine-unattempting.ngrok-free.dev" 
    
    phone = student.guardian_phone.strip()
    if phone.startswith('0'):
        phone = '+92' + phone[1:]
    elif not phone.startswith('+'):
        phone = '+' + phone
    guardian_whatsapp = f'whatsapp:{phone}'
    
    # 🚩 SMART TERMINAL MESSAGE LOGIC
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    location_text = ""
    
    if action_type == "In":
        status_text = "*ENTERED CAMPUS* 🟢" if terminal_mode == "gate" else "*BOARDED BUS* 🚌"
    else:
        # Jab Exit ho rahi ho
        if terminal_mode == "bus":
            status_text = "*BOARDED BUS (DEPARTING)* 🚌🔴"
            location_text = f"\n\n📍 *Track Bus Live:* \n{NGROK_URL}/track-bus/"
        else:
            status_text = "*EXITED CAMPUS* 🔴"
            location_text = "" # Main gate se nikalne par map nahi jayega
    
    msg_body = f"🛡️ *HCSC SECURITY ALERT* 🛡️\n\nDear {student.guardian_name},\nYour child *{student.name}* has {status_text} at {current_time}.{location_text}\n\n_System: AI Smart Gateway_"
    
    def send():
        try:
            print("\n" + "="*55)
            print(f"📱 [SENDING REAL WHATSAPP TO {guardian_whatsapp}]")
            print("="*55 + "\n")
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER, 
                body=msg_body, 
                to=guardian_whatsapp
            )
            print(f"✅ WhatsApp Sent Successfully! SID: {message.sid}")
        except Exception as e:
            print(f"❌ WhatsApp Failed: {e}")
            
    threading.Thread(target=send).start()

def log_attendance(person, attendance_date=None, lat=None, lng=None, terminal_mode='gate'):
    """Smart Exit Pole Logic with Cooldown Timer"""
    if not attendance_date:
        today = timezone.now().date()
    else:
        try: today = timezone.datetime.strptime(attendance_date, '%Y-%m-%d').date()
        except ValueError: today = timezone.now().date()
            
    now = timezone.now()
    last_log = AttendanceLog.objects.filter(person=person, date=today).order_by('-entry_time').first()
    COOLDOWN_MINUTES = 5 

    if not last_log or (last_log.entry_time and last_log.exit_time):
        if last_log and last_log.exit_time:
            time_diff = (now - last_log.exit_time).total_seconds() / 60
            if time_diff < COOLDOWN_MINUTES: return "Out" 
                
        AttendanceLog.objects.create(person=person, date=today, entry_time=now)
        if person.user_type == 'student': 
            send_whatsapp_bg(person, "In", lat, lng, terminal_mode)
        return "In"
    
    elif last_log.entry_time and not last_log.exit_time:
        time_diff = (now - last_log.entry_time).total_seconds() / 60
        if time_diff < COOLDOWN_MINUTES: return "In" 
            
        last_log.exit_time = now
        last_log.save()
        if person.user_type == 'student': 
            send_whatsapp_bg(person, "Out", lat, lng, terminal_mode)
        return "Out"
    
    return "In"

def get_entity_details(person, action_status="Success"):
    return {
        "status": "success",
        "action": action_status, 
        "name": person.name,
        "type": person.get_user_type_display(),
        "id": person.id_number,
        "photo_url": person.reference_photo.url if person.reference_photo else "",
        "extra": person.extra_html
    }

# ==========================================
# 🌐 HTML PAGES (Non-API Views)
# ==========================================

def home(request): return render(request, 'index.html')

def admin_dashboard(request):
    if not request.session.get('is_admin'): return render(request, 'index.html', {"error": "Strictly Unauthorized!"})
    pending = Entity.objects.filter(is_verified=False)
    today = timezone.now().date()
    logs_today = AttendanceLog.objects.filter(date=today)
    
    type_counts = logs_today.values('person__user_type').annotate(count=Count('person__user_type'))
    labels_type = [item['person__user_type'].title() for item in type_counts]
    data_type = [item['count'] for item in type_counts]
    if not labels_type: labels_type = ['No Data Yet']; data_type = [1] 

    last_7_days = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
    labels_week = [d.strftime('%a') for d in last_7_days] 
    data_week = [AttendanceLog.objects.filter(date=d).count() for d in last_7_days]

    return render(request, 'admin_panel.html', {
        'entities': pending, 'labels_type': labels_type, 'data_type': data_type,
        'labels_week': labels_week, 'data_week': data_week, 'total_today': logs_today.count()
    })

def approve_entity(request, entity_id):
    if not request.session.get('is_admin'): return redirect('/')
    try:
        person = Entity.objects.get(id=entity_id)
        person.is_verified = True
        person.save()
    except: pass
    return redirect('admin_dashboard')

def reject_entity(request, entity_id):
    if not request.session.get('is_admin'): return redirect('/')
    try:
        person = Entity.objects.get(id=entity_id)
        if person.reference_photo and os.path.exists(person.reference_photo.path): os.remove(person.reference_photo.path)
        if person.qr_code and os.path.exists(person.qr_code.path): os.remove(person.qr_code.path)
        person.delete()
    except: pass
    return redirect('admin_dashboard')

def attendance_report(request):
    if not (request.session.get('is_admin') or request.session.get('is_terminal_user')): return redirect('/')
    date_str = request.GET.get('date')
    search_id = request.GET.get('search_id', '').strip() 
    selected_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else timezone.now().date()
    
    logs_list = AttendanceLog.objects.filter(date=selected_date).order_by('-entry_time')
    if search_id: logs_list = logs_list.filter(person__id_number__icontains=search_id)
        
    paginator = Paginator(logs_list, 20) 
    page_number = request.GET.get('page')
    try: logs = paginator.get_page(page_number)
    except PageNotAnInteger: logs = paginator.get_page(1)
    except EmptyPage: logs = paginator.get_page(paginator.num_pages)

    return render(request, 'attendance_report.html', {'logs': logs, 'selected_date': selected_date.strftime('%Y-%m-%d'), 'search_id': search_id})


# ==========================================
# 🚀 DRF API ENDPOINTS (Scanner & Verification)
# ==========================================

@swagger_auto_schema(method='post', manual_parameters=[])
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def register_student(request):
    name = request.data.get('name')
    id_num = request.data.get('roll')
    u_type = request.data.get('user_type', 'student')
    photo = request.data.get('photo')
    finger_id = request.data.get('fingerprint_id')

    if Entity.objects.filter(id_number=id_num).exists(): return Response({"status": "error", "message": "ID already exists!"})

    if name and id_num and photo:
        try:
            ext = photo.name.split('.')[-1]
            photo.name = f"{id_num}.{ext}"
            person = Entity(
                name=name, id_number=id_num, user_type=u_type, reference_photo=photo, fingerprint_id=finger_id, is_verified=False,
                department=request.data.get('department', ''), session=request.data.get('session', ''),
                guardian_name=request.data.get('guardian_name', ''), guardian_phone=request.data.get('guardian_phone', ''),
                designation=request.data.get('designation', ''), purpose_of_visit=request.data.get('purpose', ''),
                reference_type=request.data.get('reference_type', ''), reference_details=request.data.get('reference_details', ''),
                vehicle_category=request.data.get('vehicle_category', ''), driver_cnic=request.data.get('driver_cnic', ''),
                driver_contact=request.data.get('driver_contact', ''), owner_type=request.data.get('owner_type', ''),
                ownership=request.data.get('ownership', ''), number_plate=request.data.get('number_plate', '')
            )
            secure_qr_data = dumps(id_num) 
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(secure_qr_data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            person.qr_code.save(f'qr_{id_num}.png', File(buffer), save=False)
            person.save()
            return Response({"status": "success", "message": "Enrollment Request Sent!"})
        except Exception as e: return Response({"status": "error", "message": f"Server Error: {str(e)}"})
    return Response({"status": "error", "message": "Invalid Data"})

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def verify_face(request):
    captured_img = request.data.get('image')
    target_id = request.data.get('roll_number')
    selected_date = request.data.get('attendance_date')
    
    # 🚩 Location & Mode Extractions
    lat = request.data.get('lat')
    lng = request.data.get('lng')
    terminal_mode = request.data.get('terminal_mode', 'gate')

    full_temp_path = None
    try:
        person = Entity.objects.get(id_number=target_id)
        if not person.is_verified: return Response({"status": "fail", "message": "Account pending admin approval!"})
        
        temp_path = default_storage.save(f'temp_{uuid.uuid4()}.jpg', captured_img)
        full_temp_path = os.path.join(default_storage.location, temp_path)
        ref_path = person.reference_photo.path

        result = DeepFace.verify(full_temp_path, ref_path, model_name="Facenet512", enforce_detection=False)

        if result.get('verified', False) or result.get('distance', 1.0) < 0.35:
            action = log_attendance(person, selected_date, lat, lng, terminal_mode)
            return Response(get_entity_details(person, action))
        else: return Response({"status": "fail", "message": "Face did not match!"})
    except Entity.DoesNotExist: return Response({"status": "fail", "message": "ID not found!"})
    except Exception as e: return Response({"status": "fail", "message": "Face API Error"})
    finally:
        if full_temp_path and os.path.exists(full_temp_path): os.remove(full_temp_path)

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def verify_qr(request):
    scanned_text = request.data.get('roll_from_scanner')
    selected_date = request.data.get('attendance_date')
    
    # 🚩 Location & Mode Extractions
    lat = request.data.get('lat')
    lng = request.data.get('lng')
    terminal_mode = request.data.get('terminal_mode', 'gate')
    
    try: actual_id = loads(scanned_text) 
    except BadSignature: return Response({"status": "fail", "message": "⚠️ FAKE QR DETECTED!"})

    try:
        person = Entity.objects.get(id_number=actual_id)
        if not person.is_verified: return Response({"status": "fail", "message": "Account pending approval!"})
        action = log_attendance(person, selected_date, lat, lng, terminal_mode)
        return Response(get_entity_details(person, action))
    except Entity.DoesNotExist: return Response({"status": "fail", "message": "ID not found!"})

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def verify_fingerprint(request):
    scanned_id = request.data.get('cred_id', '').strip() 
    selected_date = request.data.get('attendance_date')
    
    # 🚩 Location & Mode Extractions
    lat = request.data.get('lat')
    lng = request.data.get('lng')
    terminal_mode = request.data.get('terminal_mode', 'gate')
    
    try:
        person = Entity.objects.get(fingerprint_id=scanned_id)
        if not person.is_verified: return Response({"status": "fail", "message": "Account pending approval!"})
        action = log_attendance(person, selected_date, lat, lng, terminal_mode)
        return Response(get_entity_details(person, action))
    except Entity.DoesNotExist: return Response({"status": "fail", "message": "ID Mismatch!"})

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def login_student(request):
    name = request.data.get('name')
    id_val = request.data.get('roll')
    if name == getattr(settings, 'MASTER_ADMIN_USER', 'admin') and id_val == getattr(settings, 'MASTER_ADMIN_PASS', 'admin123'):
        request.session['is_admin'] = True; request.session['is_terminal_user'] = True 
        return Response({"status": "success", "message": "Master Admin Access Granted!"})
    try:
        person = Entity.objects.get(name__iexact=name, id_number=id_val)
        if not person.is_verified: return Response({"status": "error", "message": "Pending Admin Approval."})
        if person.user_type not in ['staff', 'guard']: return Response({"status": "error", "message": "Access Denied!"})
        request.session['is_terminal_user'] = True; request.session['is_admin'] = False 
        return Response({"status": "success", "message": person.name})
    except Entity.DoesNotExist: return Response({"status": "error", "message": "Invalid Credentials!"})

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def verify_id(request):
    roll_text = request.data.get('roll_from_scanner') 
    selected_date = request.data.get('attendance_date')
    
    # 🚩 Location & Mode Extractions
    lat = request.data.get('lat')
    lng = request.data.get('lng')
    terminal_mode = request.data.get('terminal_mode', 'gate')
    
    try:
        person = Entity.objects.get(id_number=roll_text)
        if not person.is_verified: return Response({"status": "fail", "message": "Account pending approval!"})
        action = log_attendance(person, selected_date, lat, lng, terminal_mode)
        return Response(get_entity_details(person, action))
    except Entity.DoesNotExist: return Response({"status": "fail", "message": "ID not found!"})

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def fast_live_attendance(request):
    roll_num = request.data.get('roll_number')
    selected_date = request.data.get('attendance_date')
    
    # 🚩 Location & Mode Extractions
    lat = request.data.get('lat')
    lng = request.data.get('lng')
    terminal_mode = request.data.get('terminal_mode', 'gate')
    
    if not roll_num or roll_num == "Unknown": return Response({"status": "ignore"})
    try:
        person = Entity.objects.get(id_number=str(roll_num).strip())
        action = log_attendance(person, selected_date, lat, lng, terminal_mode) 
        return Response(get_entity_details(person, action))
    except Entity.DoesNotExist: return Response({"status": "fail", "message": "ID not found!"})
    except Exception as e: return Response({"status": "fail", "message": str(e)})


# ==========================================
# 📍 LIVE BUS TRACKING APIs (Uber Style)
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def update_location(request):
    """Driver ke mobile se har 5 second baad location aayegi"""
    lat = request.data.get('lat')
    lng = request.data.get('lng')
    if lat and lng:
        loc, created = BusLocation.objects.get_or_create(bus_id="UOG-BUS-01")
        loc.latitude = float(lat)
        loc.longitude = float(lng)
        loc.save()
        return Response({"status": "success"})
    return Response({"status": "fail"})

@api_view(['GET'])
@permission_classes([AllowAny])
def get_location(request):
    """Guardian ka Map page har 3 second baad yahan se data mangega"""
    loc = BusLocation.objects.filter(bus_id="UOG-BUS-01").first()
    if loc and loc.latitude and loc.longitude:
        return Response({"status": "success", "lat": loc.latitude, "lng": loc.longitude})
    return Response({"status": "fail"})

def track_bus_page(request):
    """Yeh HTML page WhatsApp link par click karne se khulega"""
    return render(request, 'tracking.html')


# ==========================================
# ⚙️ UTILITIES
# ==========================================

@api_view(['GET'])
@permission_classes([AllowAny])
def regenerate_all_qrs(request):
    if not request.session.get('is_admin'): return Response({"status": "error", "message": "Admin Only!"})
    try:
        count = 0
        for person in Entity.objects.all():
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(dumps(person.id_number))
            qr.make(fit=True); qr_img = qr.make_image(fill='black', back_color='white')
            buffer = BytesIO(); qr_img.save(buffer, format='PNG')
            person.qr_code.save(f'qr_{person.id_number}.png', File(buffer), save=False)
            person.save()
            count += 1
        return Response({"status": "success", "message": f"{count} QRs generated."})
    except Exception as e: return Response({"status": "error", "message": str(e)})

@api_view(['GET'])
@permission_classes([AllowAny])
def rename_old_photos(request):
    if not request.session.get('is_admin'): return Response({"status": "error", "message": "Admin Only!"})
    try:
        count = 0
        for person in Entity.objects.all():
            if person.reference_photo:
                old_path = person.reference_photo.path
                new_filename = f"{person.id_number}.{old_path.split('.')[-1]}"
                new_path = os.path.join(os.path.dirname(old_path), new_filename)
                if old_path != new_path and os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    person.reference_photo.name = os.path.join(os.path.dirname(person.reference_photo.name), new_filename)
                    person.save(); count += 1
        return Response({"status": "success", "message": f"{count} photos renamed."})
    except Exception as e: return Response({"status": "error", "message": str(e)})