/**
 * Queen Sheba - Client Authentication & Authorization Service
 */

const AUTH_KEY = 'queen_sheba_token';
const USER_KEY = 'queen_sheba_user';

const Auth = {
  getToken() {
    return localStorage.getItem(AUTH_KEY);
  },

  getUser() {
    try {
      const data = localStorage.getItem(USER_KEY);
      return data ? JSON.parse(data) : null;
    } catch (e) {
      return null;
    }
  },

  setUser(user, token) {
    if (token) {
      localStorage.setItem(AUTH_KEY, token);
    }
    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
    this.updateNavState();
  },

  isAuthenticated() {
    return !!this.getToken();
  },

  isAdmin() {
    const user = this.getUser();
    return user && user.role === 'admin';
  },

  async logout() {
    const token = this.getToken();
    if (token) {
      try {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
      } catch (e) {
        // Continue clearing local state
      }
    }
    localStorage.removeItem(AUTH_KEY);
    localStorage.removeItem(USER_KEY);
    window.location.href = '/login';
  },

  async authFetch(url, options = {}) {
    const token = this.getToken();
    const headers = options.headers ? { ...options.headers } : {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    if (!headers['Content-Type'] && options.body && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(url, {
      ...options,
      headers
    });

    if (response.status === 401) {
      // Session expired or invalid
      localStorage.removeItem(AUTH_KEY);
      localStorage.removeItem(USER_KEY);
      window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
      throw new Error('Unauthorized');
    }

    return response;
  },

  requireAuth(redirectAdmin = false) {
    const token = this.getToken();
    const user = this.getUser();
    if (!token || !user) {
      window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
      return false;
    }
    if (redirectAdmin && user.role !== 'admin') {
      alert('Access Denied: Administrator privileges required.');
      window.location.href = '/';
      return false;
    }
    return true;
  },

  requireAdmin() {
    return this.requireAuth(true);
  },

  updateNavState() {
    const user = this.getUser();
    const profileBtn = document.querySelector('.profile-icon-btn');
    if (!profileBtn) return;

    if (user) {
      profileBtn.setAttribute('title', `${user.name} (${user.role === 'admin' ? 'Administrator' : 'Customer'})`);
      profileBtn.onclick = () => {
        if (user.role === 'admin') {
          window.location.href = '/admin';
        } else {
          window.location.href = '/account';
        }
      };
    } else {
      profileBtn.setAttribute('title', 'Sign In / Register');
      profileBtn.onclick = () => {
        window.location.href = '/login';
      };
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  Auth.updateNavState();
});
