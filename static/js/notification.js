
let currentUser = null;
let notifications = [];

    document.addEventListener('DOMContentLoaded', function() {
        currentUser = JSON.parse(localStorage.getItem("loggedUser"));
        if (!currentUser) {
            window.location.href = "/";
        return;
                }
        loadNotifications();
        updateNotificationBadge();
        // Check for new notifications every 30 seconds
        setInterval(updateNotificationBadge, 30000);
        });

    async function loadNotifications() {
            try {
                const res = await fetch(`/notifications/${currentUser.email}`);
    const data = await res.json();

    document.getElementById('loadingState').style.display = 'none';
                
                if (data.notifications && data.notifications.length > 0) {
        notifications = data.notifications;
    displayNotifications(notifications);
                } else {
        document.getElementById('emptyState').style.display = 'block';
                }
            } catch (error) {
        console.error("Error loading notifications:", error);
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('emptyState').style.display = 'block';
    document.getElementById('emptyState').querySelector('h3').textContent = 'Error Loading Notifications';
            }
        }

    function displayNotifications(notifications) {
            const container = document.getElementById('notificationsContainer');
    container.style.display = 'block';
    container.innerHTML = '';

            notifications.forEach(notification => {
                const isUnread = !notification.read;
    const notificationClass = isUnread ? 'unread' : '';
    const typeClass = notification.type === 'new_draw' ? 'new-draw' :
    notification.type === 'payment_update' ? 'payment-update' :
    notification.type === 'draw_result' ? 'draw-result' : '';

    const timeAgo = getTimeAgo(notification.created_at);

    const notificationHtml = `
    <div class="notification-item ${notificationClass} ${typeClass}" id="notification-${notification.id}">
        <div class="d-flex justify-content-between align-items-start">
            <div>
                <h5 class="mb-2">${notification.title}</h5>
                <p class="mb-2">${notification.message}</p>
                <small class="notification-time">
                    <i class="far fa-clock me-1"></i>${timeAgo}
                </small>
            </div>
            ${isUnread ? '<span class="badge bg-primary">New</span>' : ''}
        </div>

        <div class="notification-actions d-flex justify-content-between align-items-center">
            <div>
                ${notification.action_url ? `
                                    <a href="${notification.action_url}" class="btn btn-sm btn-primary">
                                        <i class="fas fa-eye me-1"></i>${notification.action_text}
                                    </a>
                                ` : ''}
            </div>
            ${isUnread ? `
                                <button class="mark-read-btn" onclick="markAsRead('${notification.id}')">
                                    <i class="fas fa-check me-1"></i>Mark as Read
                                </button>
                            ` : ''}
        </div>
    </div>
    `;

    container.innerHTML += notificationHtml;
            });
        }

    async function markAsRead(notificationId) {
            try {
                const res = await fetch(`/notifications/mark-read/${notificationId}`, {
        method: "POST",
    headers: {"Content-Type": "application/json" },
    body: JSON.stringify({email: currentUser.email })
                });

    const data = await res.json();
    if (data.success) {
                    const notification = document.getElementById(`notification-${notificationId}`);
    notification.classList.remove('unread');
    notification.querySelector('.badge')?.remove();
    notification.querySelector('.mark-read-btn')?.remove();
    updateNotificationBadge();
                }
            } catch (error) {
        console.error("Error marking as read:", error);
            }
        }

    async function markAllAsRead() {
            try {
                const res = await fetch(`/notifications/mark-all-read/${currentUser.email}`, {
        method: "POST"
                });

    const data = await res.json();
    if (data.success) {
        document.querySelectorAll('.notification-item.unread').forEach(item => {
            item.classList.remove('unread');
            item.querySelector('.badge')?.remove();
            item.querySelector('.mark-read-btn')?.remove();
        });
    updateNotificationBadge();
                }
            } catch (error) {
        console.error("Error marking all as read:", error);
            }
        }

    async function updateNotificationBadge() {
            try {
                const res = await fetch(`/notifications/count/${currentUser.email}`);
    const data = await res.json();
    const badge = document.getElementById('notificationBadge');
                if (data.unread_count > 0) {
        badge.textContent = data.unread_count;
    badge.style.display = 'inline';
                } else {
        badge.style.display = 'none';
                }
            } catch (error) {
        console.error("Error updating badge:", error);
            }
        }

    function getTimeAgo(dateString) {
            try {
                const parts = dateString.match(/(\d+)\/(\d+)\/(\d+)T(\d+)h:(\d+)m:(\d+)s/);
    if (!parts) return dateString;

    const [_, day, month, year, hour, minute] = parts;
    const date = new Date(year, month-1, day, hour, minute);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
            } catch {
                return dateString;
            }
        }
 