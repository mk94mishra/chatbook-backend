import re 
import datetime
	
def media_validation(**media) -> (bool, str):
    if (not media['url']) & (not media['type']) (not media['thumbnail_url']):
        return True, None

    if media['url']:
        if not media['type']:
            return False, {"msg": "must be set media type!"}
    
    if (media['type'] == 'image') or (media['type'] == 'video') or (media['type'] == 'pdf'):
        # check length
        if media['type'] == 'image':
            if len(media['url']) > 5:
                return False, {"msg": "maximum 5 image you can upload!"}
            if media['thumbnail_url']:
                return False, {"msg": "image don't need thumbnail url!"}
        
        if media['type'] == 'video':
            if len(media['url']) > 1:
                return False, {"msg": "maximum 1 video you can upload!"}
            if len(media['url']) !=  len(media['thumbnail_url']):
                return False, {"msg": "video & thumbnail url length not match!"}
        
        if media['type'] == 'pdf':
            if len(media['url']) > 1:
                return False, {"msg": "maximum 1 pdf you can upload!"}
            if media['thumbnail_url']:
                return False, {"msg": "pdf don't need thumbnail url!"}

        # check url
        for m_url in media['url']:
            validation_url(m_url)
        for mt_url in media['thumbnail_url']:
            validation_url(mt_url)
                
        return True, None
    else:
        return False, {"msg": "wrong media type! media type options are 'image','video','pdf' "}

def form_validation(validation_name, validation_data):
    if validation_data == None:
        return validation_null(validation_data)

    if validation_name == "email":
        return validation_email(validation_data)
        
    if validation_name == "mobile":
        return validation_mobile(validation_data)

    if validation_name == "date":
        return validation_date(validation_data)

    if validation_name == "gender":
        return validation_gender(validation_data)

    if validation_name == "password":
        return validation_password_len(validation_data)

    if validation_name == "url":
        return validation_url(validation_data)

# null validate
def validation_null(data) -> (bool, str):
    return True, None

# for validating an Email 
def validation_email(email) -> (bool, str): 
    email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

    if re.search(email_regex, email): 
        return True, None
    else: 
        return False, {"msg":"wrong email"}

# 10 digit mobile validation 
def validation_mobile(mobile) -> (bool, str): 
    if len(str(mobile)) == 10:
        return True, None
    return False, {"msg":"wrong mobile"}


# dob validation
def validation_date(dob) -> (bool, str):
    try:
        datetime.datetime.strptime(dob, '%d/%m/%Y')
        return True, None
    except:
        return False, {"msg":"wrong date! date formate is (DD/MM/YYYY)"}

def validation_gender(gender) -> (bool, str):
    if (gender == 'male') or (gender == 'female') or (gender == 'other'):
        return True, None
    else:
        return False, {"msg": "wrong gender! gender options are 'male','female','other' "}

def validation_password_len(password) -> (bool, str):
    if (len(password) < 21) & (len(password) > 5):
        return True, None
    else:
        return False, {"msg":"password length, min 6 and max 20"}

def validation_url(url) -> (bool, str):
    url_regex = ("((http|https)://)(www.)?" +
             "[a-zA-Z0-9@:%._\\+~#?&//=]" +
             "{2,256}\\.[a-z]" +
             "{2,6}\\b([-a-zA-Z0-9@:%" +
             "._\\+~#?&//=]*)")

    # Compile the ReGex
    p = re.compile(url_regex)

    if (re.search(p, url)): 
        return True, None
    else: 
        return False, {"msg":"wrong url"}