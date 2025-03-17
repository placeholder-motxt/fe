// Add DragEvent polyfill
class MockDragEvent extends Event {
    constructor(type, options) {
      super(type, options);
      this.dataTransfer = options?.dataTransfer || { files: [] };
    }
  }
  global.DragEvent = MockDragEvent;
  
  // Keep existing mocks
  jest.mock('*.css', () => ({}));
  jest.mock('*.svg', () => ({}));
  
  class MockFormData {
    append = jest.fn();
  }
  global.FormData = MockFormData;
  
  global.URL.createObjectURL = jest.fn(() => 'mock-url');
  global.URL.revokeObjectURL = jest.fn();
  
  Object.defineProperty(document, 'cookie', {
    writable: true,
    value: 'csrftoken=testtoken123'
  });