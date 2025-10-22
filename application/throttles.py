from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Throttle for login attempts.
    Limits login attempts to prevent brute force attacks.
    """
    scope = 'login'


class RegisterRateThrottle(AnonRateThrottle):
    """
    Throttle for user registration.
    Prevents spam user registration.
    """
    scope = 'register'


class PasswordResetRateThrottle(AnonRateThrottle):
    """
    Throttle for password reset requests.
    Prevents abuse of password reset functionality.
    """
    scope = 'password_reset'


class TaskCreateRateThrottle(UserRateThrottle):
    """
    Throttle for task creation.
    Limits how many tasks a user can create per hour.
    """
    scope = 'task_create'


class TaskUpdateRateThrottle(UserRateThrottle):
    """
    Throttle for task updates.
    Limits how many task updates a user can make per hour.
    """
    scope = 'task_update'


class BurstRateThrottle(UserRateThrottle):
    """
    Burst protection throttle.
    Prevents rapid-fire requests from users.
    """
    scope = 'burst'


class SustainedRateThrottle(UserRateThrottle):
    """
    Daily usage throttle.
    Limits total daily API usage per user.
    """
    scope = 'sustained'


class AdminActionRateThrottle(UserRateThrottle):
    """
    Special throttle for admin actions.
    Higher limits for admin users.
    """
    def allow_request(self, request, view):
        # If user is admin, apply higher limits
        if hasattr(request.user, 'role') and request.user.role == 'admin':
            # Admin users get 5x the normal rate
            self.rate = '5000/hour'
        return super().allow_request(request, view)


class AnonymousStrictThrottle(AnonRateThrottle):
    """
    Strict throttle for anonymous users on sensitive endpoints.
    """
    scope = 'anon_strict'


# Throttle classes for different levels of security
class LowSecurityThrottle(UserRateThrottle):
    """For low-risk endpoints like reading public data"""
    scope = 'low_security'


class MediumSecurityThrottle(UserRateThrottle):
    """For medium-risk endpoints like user data operations"""
    scope = 'medium_security'


class HighSecurityThrottle(UserRateThrottle):
    """For high-risk endpoints like authentication or admin operations"""
    scope = 'high_security'