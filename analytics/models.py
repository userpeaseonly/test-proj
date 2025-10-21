# Analytics app models for monitoring existing Task and User data
# This app focuses on providing read-only analytics views for admins
# using PostgreSQL aggregation on existing models rather than storing separate analytics data

from django.db import models

# No models needed - we use direct PostgreSQL aggregation 
# on existing Task and User models for real-time analytics
