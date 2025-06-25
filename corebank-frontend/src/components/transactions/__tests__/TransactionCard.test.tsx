import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import TransactionCard from '../TransactionCard'
import type { Transaction } from '../../../types/api'

describe('TransactionCard', () => {
  const mockDepositTransaction: Transaction = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    account_id: 'account-123',
    transaction_type: 'deposit',
    amount: '1000.50',
    status: 'completed',
    timestamp: '2025-01-15T10:30:00Z',
    description: '工资存款',
    related_account_id: null
  }

  const mockWithdrawalTransaction: Transaction = {
    id: '123e4567-e89b-12d3-a456-426614174001',
    account_id: 'account-123',
    transaction_type: 'withdrawal',
    amount: '500.00',
    status: 'completed',
    timestamp: '2025-01-15T14:30:00Z',
    description: '取现',
    related_account_id: null
  }

  const mockTransferTransaction: Transaction = {
    id: '123e4567-e89b-12d3-a456-426614174002',
    account_id: 'account-123',
    transaction_type: 'transfer',
    amount: '200.00',
    status: 'pending',
    timestamp: '2025-01-15T16:30:00Z',
    description: '转账给朋友',
    related_account_id: 'account-456'
  }

  it('应该显示存款交易信息', () => {
    render(<TransactionCard transaction={mockDepositTransaction} />)
    
    expect(screen.getByText('存款')).toBeInTheDocument()
    expect(screen.getByText('已完成')).toBeInTheDocument()
    expect(screen.getByText('+¥1,000.50')).toBeInTheDocument()
    expect(screen.getByText('工资存款')).toBeInTheDocument()
  })

  it('应该显示取款交易信息', () => {
    render(<TransactionCard transaction={mockWithdrawalTransaction} />)
    
    expect(screen.getByText('取款')).toBeInTheDocument()
    expect(screen.getByText('已完成')).toBeInTheDocument()
    expect(screen.getByText('-¥500.00')).toBeInTheDocument()
    expect(screen.getByText('取现')).toBeInTheDocument()
  })

  it('应该显示转账交易信息', () => {
    render(<TransactionCard transaction={mockTransferTransaction} />)
    
    expect(screen.getByText('转账')).toBeInTheDocument()
    expect(screen.getByText('处理中')).toBeInTheDocument()
    expect(screen.getByText('¥200.00')).toBeInTheDocument()
    expect(screen.getByText('转账给朋友')).toBeInTheDocument()
    expect(screen.getByText(/相关账户: \*\*\*\* -456/)).toBeInTheDocument()
  })

  it('应该正确显示不同状态', () => {
    const failedTransaction = { ...mockDepositTransaction, status: 'failed' as const }
    render(<TransactionCard transaction={failedTransaction} />)
    
    expect(screen.getByText('失败')).toBeInTheDocument()
  })

  it('应该正确格式化日期和时间', () => {
    render(<TransactionCard transaction={mockDepositTransaction} />)

    // 检查是否包含日期格式
    expect(screen.getByText(/2025/)).toBeInTheDocument()
    // 时间会根据时区转换，所以只检查是否有时间格式
    expect(screen.getByText(/\d{2}:\d{2}/)).toBeInTheDocument()
  })

  it('应该在点击时调用onClick回调', () => {
    const onClick = vi.fn()
    render(<TransactionCard transaction={mockDepositTransaction} onClick={onClick} />)
    
    const card = screen.getByText('存款').closest('div')?.parentElement
    if (card) {
      fireEvent.click(card)
      expect(onClick).toHaveBeenCalled()
    }
  })

  it('应该显示交易ID', () => {
    render(<TransactionCard transaction={mockDepositTransaction} />)
    
    expect(screen.getByText(/ID: 123e4567/)).toBeInTheDocument()
  })

  it('应该为不同交易类型显示正确的颜色', () => {
    const { rerender } = render(<TransactionCard transaction={mockDepositTransaction} />)
    
    // 存款应该是绿色
    expect(screen.getByText('+¥1,000.50')).toHaveClass('text-green-600')
    
    // 取款应该是红色
    rerender(<TransactionCard transaction={mockWithdrawalTransaction} />)
    expect(screen.getByText('-¥500.00')).toHaveClass('text-red-600')
    
    // 转账应该是蓝色
    rerender(<TransactionCard transaction={mockTransferTransaction} />)
    expect(screen.getByText('¥200.00')).toHaveClass('text-blue-600')
  })

  it('应该在没有描述时不显示描述', () => {
    const transactionWithoutDescription = { ...mockDepositTransaction, description: null }
    render(<TransactionCard transaction={transactionWithoutDescription} />)
    
    expect(screen.queryByText('工资存款')).not.toBeInTheDocument()
  })

  it('应该在没有相关账户时不显示相关账户信息', () => {
    render(<TransactionCard transaction={mockDepositTransaction} />)
    
    expect(screen.queryByText(/相关账户/)).not.toBeInTheDocument()
  })
})
