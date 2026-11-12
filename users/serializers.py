from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Contact

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True, validators=[validate_password])
	password_confirmation = serializers.CharField(write_only=True)

	class Meta:
		model = User
		fields = (
			'email',
			'password',
			'password_confirmation',
			'first_name',
			'last_name',
			'user_type',
			'company'
		)

	def validate(self, attrs):
		if attrs['password'] != attrs['password_confirmation']:
			raise serializers.ValidationError('Passwords must match')
		if attrs.get('user_type') == User.UserType.SHOP and not attrs.get('company'):
			raise serializers.ValidationError('Company must be provided')
		return attrs

	def create(self, validated_data):
		validated_data.pop('password_confirmation')
		password = validated_data.pop('password')
		user = User(**validated_data)
		user.set_password(password) #хешируем пароль
		user.is_active = False #по умолчании до подтверждения email
		user.save()
		return user

class LoginSerializer(serializers.Serializer):
	email = serializers.EmailField()
	password = serializers.CharField(write_only=True)

	def validate(self, attrs):
		user = authenticate(
			request=self.context.get('request'),
			username=attrs['email'], #для валидации по email а не username
			password=attrs['password'],
		)

		if not user:
			raise serializers.ValidationError('Invalid credentials')
		if not user.is_active:
			raise serializers.ValidationError('User must be activated')
		attrs['user'] = user
		return attrs


class UserSerializer(serializers.ModelSerializer):

	class Meta:
		model = User
		fields = ('id', 'email', 'first_name', 'last_name',
		          'user_type', 'company', 'is_active'
		          )
		read_only_fields = ('id', 'email', 'user_type', 'is_active',)


class PasswordResetRequestSerializer(serializers.Serializer):
	email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
	token = serializers.CharField()
	password = serializers.CharField(write_only=True, validators=[validate_password])
	password_confirmation = serializers.CharField(write_only=True)

	def validate(self, attrs):
		if attrs.get('password') != attrs.get('password_confirmation'):
			raise serializers.ValidationError('Passwords must match')
		return attrs


class ContactSerializer(serializers.ModelSerializer):
	class Meta:
		model = Contact
		fields = (
			'id', 'city', 'street', 'house', 'is_private_house',
			'building', 'apartment', 'phone', 'is_default_adress',
		)
		read_only_fields = ('id',)

	def validate(self, attrs):
		#адрес по умолчании может быть только один, если в запросе is_default=True
		#старый адрес перестанет быть адресом по умолчании
		if attrs.get('is_default_adress'):
			request = self.context.get('request')
			if request and request.user:
				Contact.objects.filter(
					user=request.user, is_default_adress=True,
				).exclude(pk=self.instance.pk if self.instance else None).update(is_default_adress=False)
		return attrs
