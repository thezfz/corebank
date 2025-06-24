/// <reference types="vitest" />
/// <reference types="@testing-library/jest-dom" />

import type { TestingLibraryMatchers } from '@testing-library/jest-dom/matchers'

declare module 'vitest' {
  interface Assertion<T = any> extends jest.Matchers<void>, TestingLibraryMatchers<T, void> {}
  interface AsymmetricMatchersContaining extends jest.Matchers<void>, TestingLibraryMatchers<any, void> {}
}

// 全局类型扩展
declare global {
  namespace Vi {
    interface JestAssertion<T = any> extends jest.Matchers<void>, TestingLibraryMatchers<T, void> {}
  }
}
