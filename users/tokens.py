from django.contrib.auth.tokens import PasswordResetTokenGenerator

class EmailConfirmationTokenGenerator(PasswordResetTokenGenerator):

	def _make_hash(self, user, timestamp):
		return f'{user.pk}:{user.is_active}:{timestamp}'

email_confirmation_token = EmailConfirmationTokenGenerator()