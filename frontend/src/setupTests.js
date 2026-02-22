// Setup tests file for Jest
import '@testing-library/jest-dom';

// Mock global objects if needed
global.matchMedia = global.matchMedia || function() {
  return {
    matches: false,
    addListener: jest.fn(),
    removeListener: jest.fn()
  };
};

// Mock console.error to fail tests on console errors
global.console.error = jest.fn((...args) => {
  global.console.log(...args);
  throw new Error(`Console error: ${args.join(' ')}`);
});
