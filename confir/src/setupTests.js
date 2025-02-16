// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Mock BroadcastChannel
class MockBroadcastChannel {
  constructor(channel) {
    this.channel = channel;
    this.onmessage = null;
  }
  postMessage(message) {}
  close() {}
}
global.BroadcastChannel = MockBroadcastChannel;

// Mock TransformStream
class MockTransformStream {
  constructor(transformer) {
    this.transformer = transformer;
    this.readable = {};
    this.writable = {};
  }
}
global.TransformStream = MockTransformStream;