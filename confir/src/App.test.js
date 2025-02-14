import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import App from './App';

// Mock the image imports
jest.mock('./AP.png', () => 'AP.png');
jest.mock('./OB.png', () => 'OB.png');
jest.mock('./background.png', () => 'background.png');
jest.mock('./blueBox.png', () => 'blueBox.png');
jest.mock('./carmbox.png', () => 'carmbox.png');
jest.mock('./tiltcarm.png', () => 'tiltcarm.png');
jest.mock('./rotcarm.png', () => 'rotcarm.png');
jest.mock('./IMUConnectionIcon.png', () => 'IMUConnectionIcon.png');
jest.mock('./videoConnectionIcon.png', () => 'videoConnectionIcon.png');

// Setup MSW server for API mocking
const server = setupServer(
  // Default handlers
  rest.post('http://localhost:5000/run2', (req, res, ctx) => {
    return res(ctx.status(200));
  }),
  
  rest.get('http://localhost:5000/api/states', (req, res, ctx) => {
    return res(ctx.json({
      angle: 0,
      rotation_angle: 0,
      img_count: 0
    }));
  }),
  
  rest.get('http://localhost:5000/api/latest-image', (req, res, ctx) => {
    return res(
      ctx.set('Content-Type', 'image/jpeg'),
      ctx.body('mock-image-data')
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Connection Tests', () => {
  // Test 1: Initial UI state
  test('shows connect button initially', () => {
    render(<App />);
    expect(screen.getByText('Connect')).toBeInTheDocument();
  });

  // Test 2: Successful connection
  test('handles successful connection', async () => {
    render(<App />);
    
    const connectButton = screen.getByText('Connect');
    fireEvent.click(connectButton);

    // Wait for connection to complete and UI to update
    await screen.findByAltText('Image 1');
    await screen.findByAltText('Image 2');
    
    // Verify connect button is no longer visible
    expect(screen.queryByText('Connect')).not.toBeInTheDocument();
  });

  // Test 3: Failed connection
  test('handles failed connection', async () => {
    // Override default handler for failed connection scenario
    server.use(
      rest.post('http://localhost:5000/run2', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    render(<App />);
    
    const connectButton = screen.getByText('Connect');
    fireEvent.click(connectButton);

    // Wait for error message to appear
    const errorMessage = await screen.findByText(/Error connecting to device/i);
    expect(errorMessage).toBeInTheDocument();
    
    // Connect button should still be visible
    expect(screen.getByText('Connect')).toBeInTheDocument();
  });

  // Test 4: Periodic state fetching
  test('periodically fetches states after connection', async () => {
    jest.useFakeTimers();
    
    let stateCallCount = 0;
    server.use(
      rest.get('http://localhost:5000/api/states', (req, res, ctx) => {
        stateCallCount++;
        return res(ctx.json({
          angle: stateCallCount * 10, // Changing angle to verify updates
          rotation_angle: 0,
          img_count: stateCallCount
        }));
      })
    );

    render(<App />);
    
    // Connect
    const connectButton = screen.getByText('Connect');
    fireEvent.click(connectButton);
    
    // Wait for initial connection
    await screen.findByAltText('Image 1');

    // Advance timers and verify state updates
    await act(async () => {
      jest.advanceTimersByTime(300); // Advance 300ms (3 intervals)
    });

    expect(stateCallCount).toBeGreaterThan(1);
    
    jest.useRealTimers();
  });

  // Test 5: Connection timeout
  test('handles connection timeout', async () => {
    server.use(
      rest.post('http://localhost:5000/run2', (req, res, ctx) => {
        return res(ctx.delay(5000), ctx.status(408));
      })
    );

    render(<App />);
    
    const connectButton = screen.getByText('Connect');
    fireEvent.click(connectButton);

    const errorMessage = await screen.findByText(/Error connecting to device/i);
    expect(errorMessage).toBeInTheDocument();
  });

  // Test 6: Network error during state fetching
  test('handles network error during state fetching', async () => {
    jest.useFakeTimers();
    
    render(<App />);
    
    // Successfully connect first
    const connectButton = screen.getByText('Connect');
    fireEvent.click(connectButton);
    
    await screen.findByAltText('Image 1');

    // Simulate network error for state fetching
    server.use(
      rest.get('http://localhost:5000/api/states', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    // Advance timer to trigger state fetch
    await act(async () => {
      jest.advanceTimersByTime(100);
    });

    const errorMessage = await screen.findByText(/Error connecting to server/i);
    expect(errorMessage).toBeInTheDocument();

    jest.useRealTimers();
  });
});