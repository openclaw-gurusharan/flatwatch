import { fireEvent, render, screen } from '@testing-library/react';
import { ProtectedRoute } from '../ProtectedRoute';
import { useAuth } from '../auth';

jest.mock('../auth', () => ({
  useAuth: jest.fn(),
}));

const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;

describe('ProtectedRoute', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders children for authenticated users', () => {
    const login = jest.fn().mockResolvedValue(undefined);
    mockUseAuth.mockReturnValue({
      user: { id: '2', email: 'resident@flatwatch.test', role: 'resident' },
      loading: false,
      error: null,
      validateSession: jest.fn(),
      login,
      logout: jest.fn(),
    });

    render(
      <ProtectedRoute>
        <div>secret content</div>
      </ProtectedRoute>
    );

    expect(screen.getByText('secret content')).toBeInTheDocument();
    expect(login).not.toHaveBeenCalled();
  });

  it('does not auto-login unauthenticated users', () => {
    const login = jest.fn().mockResolvedValue(undefined);
    mockUseAuth.mockReturnValue({
      user: null,
      loading: false,
      error: null,
      validateSession: jest.fn(),
      login,
      logout: jest.fn(),
    });

    render(
      <ProtectedRoute>
        <div>secret content</div>
      </ProtectedRoute>
    );

    expect(screen.getByText('Sign in required')).toBeInTheDocument();
    expect(login).not.toHaveBeenCalled();
  });

  it('only attempts login when the sign-in button is clicked', () => {
    const login = jest.fn().mockResolvedValue(undefined);
    mockUseAuth.mockReturnValue({
      user: null,
      loading: false,
      error: null,
      validateSession: jest.fn(),
      login,
      logout: jest.fn(),
    });

    render(
      <ProtectedRoute>
        <div>secret content</div>
      </ProtectedRoute>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    expect(login).toHaveBeenCalledTimes(1);
  });
});
