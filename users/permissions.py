from rest_framework.permissions import IsAuthenticated

class IsShopOwner(IsAuthenticated):
	def has_permission(self, request, view):
		if not super().has_permission(request, view):
			return False
		if request.user.user_type != 'shop':
			return False
		try:
			request.user.shop
		except Exception:
			return False
		return True
