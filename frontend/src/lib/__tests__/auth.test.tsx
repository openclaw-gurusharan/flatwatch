import { renderHook, act, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '../auth';

global.fetch = jest.fn();

const mockLocation = { href: '' };
Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true,
});

const AUTH_TOKEN_KEY = 'flatwatch-auth-token';

describe('flatwatch auth provider', () => {
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <AuthProvider>{children}</AuthProvider>
  );

  beforeEach(() => {
    jest.clearAllMocks();
    window.localStorage.clear();
    mockLocation.href = '';
  });

  it('treats missing local token as signed out', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.user).toBeNull();
    expect(result.current.error).toBeNull();
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('verifies an existing token with the local backend', async () => {
    window.localStorage.setItem(AUTH_TOKEN_KEY, 'demo-token');
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        valid: true,
        user: {
          id: 7,
          email: 'resident@flatwatch.test',
          name: 'Resident',
          role: 'resident',
        },
      }),
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(global.fetch).toHaveBeenCalledWith(
      'http://127.0.0.1:8001/api/auth/verify',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          Authorization: 'Bearer demo-token',
        }),
      })
    );
    expect(result.current.user).toEqual({
      id: 7,
      email: 'resident@flatwatch.test',
      name: 'Resident',
      role: 'resident',
    });
  });

  it('clears an invalid token on 401', async () => {
    window.localStorage.setItem(AUTH_TOKEN_KEY, 'expired-token');
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 401,
      statusText: 'Unauthorized',
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.user).toBeNull();
    expect(window.localStorage.getItem(AUTH_TOKEN_KEY)).toBeNull();
  });

  it('logs in through the local backend and stores the token', async () => {
    const loginResponse = {
      access_token: 'fresh-token',
      token_type: 'bearer',
      user: {
        id: 2,
        email: 'resident@flatwatch.test',
        name: 'Resident User',
        role: 'resident',
      },
    };

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => expect(result.current.loading).toBe(false));

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => loginResponse,
    });

    await act(async () => {
      await result.current.login();
    });

    expect(global.fetch).toHaveBeenLastCalledWith(
      'http://127.0.0.1:8001/api/auth/login',
      expect.objectContaining({
        method: 'POST',
      })
    );
    expect(window.localStorage.getItem(AUTH_TOKEN_KEY)).toBe('fresh-token');
    expect(result.current.user).toEqual({
      id: '2',
      email: 'resident@flatwatch.test',
      name: 'Resident User',
      role: 'resident',
    });
  });

  it('logs out by clearing the local token and returning home', async () => {
    window.localStorage.setItem(AUTH_TOKEN_KEY, 'demo-token');
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        valid: true,
        user: {
          id: 2,
          email: 'resident@flatwatch.test',
          name: 'Resident User',
          role: 'resident',
        },
      }),
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => expect(result.current.user).not.toBeNull());

    await act(async () => {
      await result.current.logout();
    });

    expect(window.localStorage.getItem(AUTH_TOKEN_KEY)).toBeNull();
    expect(result.current.user).toBeNull();
    expect(mockLocation.href).toBe('/');
  });
});
