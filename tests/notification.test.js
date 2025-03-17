import { showNotification } from '../static/js/convert_page';

describe('Notifications', () => {
  let notification;

  beforeEach(() => {
    document.body.innerHTML = `
      <div id="notification" class="hidden">
        <div id="notificationMessage"></div>
      </div>
    `;
    notification = document.getElementById('notification');
  });

  test('shows success notification', () => {
    showNotification('Success', 'success');
    expect(notification.className).toContain('bg-green-100');
  });

  test('shows error notification', () => {
    showNotification('Error', 'error');
    expect(notification.className).toContain('bg-red-100');
  });
});