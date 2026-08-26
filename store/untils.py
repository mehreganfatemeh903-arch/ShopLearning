STATUS_CHOICE = {
    -1: 'Cancel',
    0: 'Pending Py',
    1: 'processing',
    2: 'shipped',
    3: 'delivered',
}


def get_tuple_status():
    return [(k, v) for k, v in STATUS_CHOICE.items()]


def display_status(status):
    return STATUS_CHOICE.get(int(status), 'UnKnown Status')

def get_user_or_session(request):
    if request.user.is_authenticated:
        user=request.user
        session_key=None
    else:
        user=None
        session_key=request.session.session_key
        if not session_key:
            request.session.cart()
            session_key=request.session.session_key
    return user,session_key
