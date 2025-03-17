const { handleDragOver, handleDragLeave } = require('../static/js/convert_page');

// DragEvent polyfill
class MockDragEvent extends Event {
  constructor(type, options) {
    super(type, options);
    this.dataTransfer = options?.dataTransfer || {};
  }
}
global.DragEvent = MockDragEvent;

describe('Drag and Drop', () => {
  let dropZone;

  beforeEach(() => {
    document.body.innerHTML = `<div class="drop-zone"></div>`;
    dropZone = document.querySelector('.drop-zone');
  });

  test('adds dragover class on dragover', () => {
    const event = new DragEvent('dragover');
    handleDragOver(event);
    expect(dropZone.classList.contains('dragover')).toBe(true);
  });

  test('removes dragover class on dragleave', () => {
    dropZone.classList.add('dragover');
    const event = new DragEvent('dragleave');
    handleDragLeave(event);
    expect(dropZone.classList.contains('dragover')).toBe(false);
  });
});