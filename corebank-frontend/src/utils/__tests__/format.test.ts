import { describe, it, expect } from 'vitest'
import { formatCurrency, formatDate, validateUsername, validatePassword } from '../format'

// 单元测试
describe('格式化工具函数', () => {
  describe('formatCurrency', () => {
    it('应该正确格式化正数金额', () => {
      expect(formatCurrency(1234.56)).toBe('¥1,234.56')
    })

    it('应该正确格式化零金额', () => {
      expect(formatCurrency(0)).toBe('¥0.00')
    })

    it('应该正确格式化负数金额', () => {
      expect(formatCurrency(-500)).toBe('-¥500.00')
    })
  })

  describe('formatDate', () => {
    it('应该正确格式化日期对象', () => {
      const date = new Date('2025-01-15')
      expect(formatDate(date)).toBe('2025/01/15')
    })

    it('应该正确格式化日期字符串', () => {
      expect(formatDate('2025-12-25')).toBe('2025/12/25')
    })
  })

  describe('validateUsername', () => {
    it('应该接受有效的用户名', () => {
      expect(validateUsername('user123')).toBe(true)
      expect(validateUsername('test_user')).toBe(true)
      expect(validateUsername('ABC123')).toBe(true)
    })

    it('应该拒绝无效的用户名', () => {
      expect(validateUsername('ab')).toBe(false) // 太短
      expect(validateUsername('user@name')).toBe(false) // 特殊字符
      expect(validateUsername('')).toBe(false) // 空字符串
    })
  })

  describe('validatePassword', () => {
    it('应该接受强密码', () => {
      expect(validatePassword('Password123')).toBe(true)
      expect(validatePassword('MySecure1')).toBe(true)
    })

    it('应该拒绝弱密码', () => {
      expect(validatePassword('password')).toBe(false) // 无大写字母和数字
      expect(validatePassword('PASSWORD123')).toBe(false) // 无小写字母
      expect(validatePassword('Password')).toBe(false) // 无数字
      expect(validatePassword('Pass1')).toBe(false) // 太短
    })
  })
})
