import { renderHook, act, waitFor } from '@testing-library/react';
import { useAuth, AuthProvider } from '../auth';

// Mock fetch
global.fetch = jest.fn();

// Mock window.location
const mockLocation = { href: '' };
Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true,
});

describe('useAuth', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocation.href = '';
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <AuthProvider>{children}</AuthProvider>
  );

  describe('validateSession', () => {
    it('should set user when session is valid', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'resident',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ valid: true, user: mockUser }),
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => expect(result.current.loading).toBe(false));

      expect(result.current.user).toEqual(mockUser);
      expect(result.current.error).toBeNull();
      expect(global.fetch).toHaveBeenCalledWith(
        'https://aadharcha.in/api/auth/validate',
        expect.objectContaining({
          credentials: 'include',
        })
      );
    });

    it('should set user to null when session is invalid (401)', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => expect(result.current.loading).toBe(false));

      expect(result.current.user).toBeNull();
      expect(result.current.error).toBeNull();
    });

    it('should set error when validation fails with non-401 status', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => expect(result.current.loading).toBe(false));

      expect(result.current.user).toBeNull();
      expect(result.current.error).toContain('Session validation failed');
    });

    it('should set error when network request fails', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => expect(result.current.loading).toBe(false));

      expect(result.current.user).toBeNull();
      expect(result.current.error).toBe('Network error');
    });

    it('should return false when valid response has no user data', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ valid: false }),
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => expect(result.current.loading).toBe(false));

      expect(result.current.user).toBeNull();
    });

    it('should use default IDENTITY_URL when env not set', async () => {
      // Verify default URL is used (aadharcha.in)
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ valid: false }),
      });

      renderHook(() => useAuth(), { wrapper });

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          'https://aadharcha.in/api/auth/validate',
          expect.any(Object)
        );
      });
    });
  });

  describe('login', () => {
    it('should redirect to SSO login page', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ valid: false }),
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => expect(result.current.loading).toBe(false));

      act(() => {
        result.current.login();
      });

      expect(mockLocation.href).toContain('https://aadharcha.in/login');
      expect(mockLocation.href).toContain('return_url=');
    });

    it('should use default identity URL for login redirect', () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ valid: false }),
      });

      const { result } = renderHook(() => useAuth(), { wrapper });

      act(() => {
        result.current.login();
      });

      expect(mockLocation.href).toContain('https://aadharcha.in/login');
      expect(mockLocation.href).toContain('return_url=');
    });
  });

  describe('logout', () => {
    it('should call logout API and clear user', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            valid: true,
            user: { id: '123', email: 'test@example.com', role: 'resident' },
          }),
        })
        .mockResolvedValueOnce({
          ok: true,
        });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => expect(result.current.user).not.toBeNull());

      await act(async () => {
        await result.current.logout();
      });

      expect(global.fetch).toHaveBeenCalledWith(
        'https://aadharcha.in/api/auth/logout',
        expect.objectContaining({
          method: 'POST',
          credentials: 'include',
        })
      );
      expect(result.current.user).toBeNull();
      expect(mockLocation.href).toBe('/');
    });

    it('should handle logout API errors gracefully', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            valid: true,
            user: { id: '123', email: 'test@example.com', role: 'resident' },
          }),
        })
        .mockRejectedValueOnce(new Error('Logout failed'));

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => expect(result.current.user).not.toBeNull());

      await act(async () => {
        await result.current.logout();
      });

      expect(result.current.user).toBeNull();
      expect(mockLocation.href).toBe('/');
    });
  });

  describe('AuthProvider', () => {
    it('should throw error when useAuth is used without provider', () => {
      const consoleError = jest.spyOn(console, 'error').mockImplementation();

      expect(() => {
        renderHook(() => useAuth());
      }).toThrow('useAuth must be used within AuthProvider');

      consoleError.mockRestore();
    });

    it('should validate session on mount', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ valid: false }),
      });

      renderHook(() => useAuth(), { wrapper });

      expect(global.fetch).toHaveBeenCalledWith(
        'https://aadharcha.in/api/auth/validate',
        expect.any(Object)
      );
    });
  });

  describe('manual validateSession call', () => {
    it('should return true for valid session', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'resident',
      };

      // Mock both the initial mount call and the manual call
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ valid: false }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ valid: true, user: mockUser }),
        });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => expect(result.current.loading).toBe(false));

      let isValid = false;
      await act(async () => {
        isValid = await result.current.validateSession();
      });

      expect(isValid).toBe(true);
      expect(result.current.user).toEqual(mockUser);
    });

    it('should return false for invalid session', async () => {
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ valid: false }),
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 401,
          statusText: 'Unauthorized',
        });

      const { result } = renderHook(() => useAuth(), { wrapper });

      await waitFor(() => expect(result.current.loading).toBe(false));

      let isValid = true;
      await act(async () => {
        isValid = await result.current.validateSession();
      });

      expect(isValid).toBe(false);
      expect(result.current.user).toBeNull();
    });
  });
});
