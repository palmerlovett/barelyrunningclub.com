# club/context_processors.py

from club.models import Member, Notification


def latest_notification(request):

  member = Member.get_member_from_cookie(request)

  notification = (
    Notification.objects.filter(recipient=member, unread=True)
    .order_by("-timestamp")
    .first())

  if notification:
    notification.unread = False
    notification.save(update_fields=["unread"])

  return { "notification": notification }