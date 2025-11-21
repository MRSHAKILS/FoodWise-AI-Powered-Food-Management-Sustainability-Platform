"""
Test authentication status
Run with: python manage.py shell < test_auth.py
"""
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.utils import timezone

User = get_user_model()

print("=" * 50)
print("AUTHENTICATION DEBUG")
print("=" * 50)

# Check users
users = User.objects.all()
print(f"\nTotal Users: {users.count()}")
for user in users:
    print(f"  - {user.username} ({user.email}) - Active: {user.is_active}")

# Check active sessions
sessions = Session.objects.filter(expire_date__gte=timezone.now())
print(f"\nActive Sessions: {sessions.count()}")
for session in sessions:
    data = session.get_decoded()
    user_id = data.get('_auth_user_id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            print(f"  - Session for: {user.username}")
        except User.DoesNotExist:
            print(f"  - Session for deleted user (ID: {user_id})")

print("\n" + "=" * 50)
