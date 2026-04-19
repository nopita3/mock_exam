
from backend.utils import decode_access_token
from fastapi import Request , Response
from datetime import datetime


def log_control(auth_header:str ,
                request:Request
                ,response:Response,
                process_time,):

    # --- ส่วนที่เพิ่ม: พยายามแกะ User ID จาก Token
    
    try:
        user_id, sup_id, email = "annonymous", "annonymous" , None
        error_msg = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token) 
            user = payload.get("user")
            user_id = user.get("id") 
            sup_id = user.get("supervisor_id")

        if hasattr(request.state, "email") :
            email = request.state.email
        elif request.query_params.get("email"):
            email = request.query_params.get("email")
        else:
            email = None
        
        if hasattr(request.state, "user_id") :
            user_id = str(request.state.user_id)
            
        # ดึง handled exception จาก request.state
        if hasattr(request.state, "handled_exception"):
            exc_info = request.state.handled_exception
            error_msg = str(exc_info.get("type"))+": "+str(exc_info.get("detail"))
        
        
    except Exception as e:        
        user_id = "annonymous"
        sup_id = "annonymous"
        email = None
        error_msg = str(e)
    
    log_data = {
        "level": "INFO" if response.status_code < 400 else ("CLIENT_ERROR" if response.status_code < 500 else "SERVER_ERROR"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "method": request.method,
        "path": request.url.path,
        "query": str(request.query_params) if request.query_params else None,
        "status_code": response.status_code,
        "process_time": process_time,
        "user_id": user_id,
        "supervisor_id": sup_id,
        "email": email, 
    }
    if error_msg:
        log_data["error_message"] = error_msg   
    return log_data
        