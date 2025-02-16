import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
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
  http.post('http://localhost:5000/run2', () => {
    return HttpResponse.json({}, { status: 200 })
  }),
  
  http.get('http://localhost:5000/api/states', () => {
    return HttpResponse.json({
      angle: 0,
      rotation_angle: 0,
      img_count: 0
    })
  }),
  
  http.get('http://localhost:5000/api/latest-image', () => {
    return new HttpResponse('mock-image-data', {
      headers: {
        'Content-Type': 'image/jpeg',
      },
    })
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
  server.use(
    http.post('http://localhost:5000/run2', () => {
      return HttpResponse.error()
    })
  );

  render(<App />);
  
  const connectButton = screen.getByText('Connect');
  fireEvent.click(connectButton);

  // Wait for the error to appear
  await act(async () => {
    await new Promise(resolve => setTimeout(resolve, 100));
  });

  // Looking for partial text match using regex
  const errorElement = screen.getByText(/Error connecting to device/i);
  expect(errorElement).toBeInTheDocument();
  
  // Connect button should still be visible
  expect(screen.getByText('Connect')).toBeInTheDocument();
});


  // Test 4: Periodic state fetching
  test('periodically fetches states after connection', async () => {
    jest.useFakeTimers();
    
    let stateCallCount = 0;
    server.use(
      http.get('http://localhost:5000/api/states', (req, res, ctx) => {
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
    http.post('http://localhost:5000/run2', () => {
      return HttpResponse.error()
    })
  );

  render(<App />);
  
  const connectButton = screen.getByText('Connect');
  fireEvent.click(connectButton);

  await act(async () => {
    await new Promise(resolve => setTimeout(resolve, 100));
  });

  const errorElement = screen.getByText(/Error connecting to device/i);
  expect(errorElement).toBeInTheDocument();
});

// Test 6: Network error during state fetching
test('handles network error during state fetching', async () => {
  jest.useFakeTimers();
  
  // First render with successful connection
  render(<App />);
  
  const connectButton = screen.getByText('Connect');
  fireEvent.click(connectButton);
  
  await screen.findByAltText('Image 1');

  // Simulate network error for state fetching
  server.use(
    http.get('http://localhost:5000/api/states', () => {
      return HttpResponse.error()
    })
  );

  // Advance timer to trigger state fetch
  await act(async () => {
    jest.advanceTimersByTime(100);
  });

  await act(async () => {
    await new Promise(resolve => setTimeout(resolve, 100));
  });

  const errorElement = screen.getByText(/Error connecting to server/i);
  expect(errorElement).toBeInTheDocument();

  jest.useRealTimers();
});
});