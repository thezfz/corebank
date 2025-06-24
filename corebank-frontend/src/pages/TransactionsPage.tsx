export default function TransactionsPage() {
  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-xl font-semibold text-gray-900">Transactions</h1>
          <p className="mt-2 text-sm text-gray-700">
            View your transaction history and make new transactions.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none space-x-2">
          <button className="btn-primary">Deposit</button>
          <button className="btn-primary">Withdraw</button>
          <button className="btn-primary">Transfer</button>
        </div>
      </div>
      <div className="mt-8">
        <div className="card">
          <div className="card-body">
            <p className="text-gray-500 text-center py-8">
              No transactions found. Make your first transaction to see it here.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
