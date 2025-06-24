/// <reference types="vitest" />
/// <reference types="@testing-library/jest-dom" />
/// <reference path="./vitest-setup.d.ts" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: true,
    // 明确指定测试文件模式，支持 __tests__ 目录
    include: [
      'src/**/__tests__/**/*.{test,spec}.{js,ts,jsx,tsx}',
      'src/**/*.{test,spec}.{js,ts,jsx,tsx}'
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        'src/**/__tests__/**',
        '**/*.d.ts',
        '**/*.config.*',
        'dist/',
        '**/index.ts', // 排除 index.ts 文件
      ],
    },
  },
})
