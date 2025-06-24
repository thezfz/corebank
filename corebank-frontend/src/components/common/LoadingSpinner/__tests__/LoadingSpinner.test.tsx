import { describe, it, expect } from 'vitest'
import { render } from '../../../../test/utils'
import LoadingSpinner from '../LoadingSpinner'

describe('LoadingSpinner 组件', () => {
  it('应该渲染默认的加载动画', () => {
    const { container } = render(<LoadingSpinner />)

    const spinner = container.firstChild as HTMLElement
    expect(spinner).toBeInTheDocument()
    expect(spinner).toHaveClass('animate-spin')
    expect(spinner).toHaveClass('h-8', 'w-8') // 默认 md 尺寸
  })

  it('应该应用自定义的 className', () => {
    const { container } = render(<LoadingSpinner className="custom-class" />)

    const spinner = container.firstChild as HTMLElement
    expect(spinner).toHaveClass('custom-class')
  })

  it('应该根据 size 属性调整大小', () => {
    const { container, rerender } = render(<LoadingSpinner size="sm" />)
    let spinner = container.firstChild as HTMLElement
    expect(spinner).toHaveClass('h-4', 'w-4')

    rerender(<LoadingSpinner size="lg" />)
    spinner = container.firstChild as HTMLElement
    expect(spinner).toHaveClass('h-12', 'w-12')
  })

  it('应该包含基本的样式类', () => {
    const { container } = render(<LoadingSpinner />)

    const spinner = container.firstChild as HTMLElement
    expect(spinner).toHaveClass('animate-spin')
    expect(spinner).toHaveClass('rounded-full')
    expect(spinner).toHaveClass('border-2')
    expect(spinner).toHaveClass('border-gray-300')
    expect(spinner).toHaveClass('border-t-primary-600')
  })
})
