from rest_framework import permissions

class IsAgrovetCreatingFarmer(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        print("PERMISSION DEBUG: user_type=", getattr(user, 'user_type', None), "is_authenticated=", user.is_authenticated)
        if view.action == 'create' and request.method == 'POST':
            user_type = request.data.get('user_type')
            if user_type == 'Farmer':
                return user.is_authenticated and getattr(user, 'user_type', None) == 'Agrovet'
            else:
                return True  
        if view.action == 'my_farmers' and request.method == 'GET':
            return user.is_authenticated and getattr(user, 'user_type', None) == 'Agrovet'
        return True
